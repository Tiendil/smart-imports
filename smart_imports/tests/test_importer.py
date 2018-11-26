
import os
import math
import json
import uuid
import unittest
import importlib
import subprocess

from unittest import mock

from .. import rules
from .. import config
from .. import helpers
from .. import importer
from .. import constants
from .. import exceptions
from .. import scopes_tree


TEST_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestApplyRules(unittest.TestCase):

    def setUp(self):
        self.source_module = 'smart_imports.tests.fake_package.config_variables'

        self.config = config.DEFAULT_CONFIG.clone(path='#config.1',
                                                  rules=[{'type': 'rule_custom',
                                                          'variables': {'config_variable': {'module': self.source_module}}},
                                                         {'type': 'rule_local_modules'},
                                                         {'type': 'rule_stdlib'},
                                                         {'type': 'rule_predefined_names'}])

        self.module = type(os)

    def test_command_not_found(self):
        result = importer.apply_rules(module_config=self.config,
                                      module=self.module,
                                      variable='x')
        self.assertEqual(result, None)

    def test_command_found(self):
        command = importer.apply_rules(module_config=self.config,
                                       module=self.module,
                                       variable='config_variable')

        self.assertEqual(command, rules.ImportCommand(target_module=self.module,
                                                      target_attribute='config_variable',
                                                      source_module=self.source_module,
                                                      source_attribute=None))

    def test_rules_priority(self):
        test_config = config.DEFAULT_CONFIG.clone(path='#config.2',
                                                  rules=[{'type': 'rule_custom',
                                                          'variables': {'var_1': {'module': 'math'}}},
                                                         {'type': 'rule_custom',
                                                          'variables': {'var_1': {'module': 'json'}}}])
        command = importer.apply_rules(module_config=test_config,
                                       module=self.module,
                                       variable='var_1')

        self.assertEqual(command, rules.ImportCommand(target_module=self.module,
                                                      target_attribute='var_1',
                                                      source_module='math',
                                                      source_attribute=None))


class TestGetModuleScopesTree(unittest.TestCase):

    def test(self):
        source = '''
x = 1

def y(q):
    return q + z
        '''
        scope = importer.get_module_scopes_tree(source)

        self.assertEqual(scope.variables, {'x': scopes_tree.VariableInfo(constants.VARIABLE_STATE.INITIALIZED, 2),
                                           'y': scopes_tree.VariableInfo(constants.VARIABLE_STATE.INITIALIZED, 4)})

        self.assertEqual(scope.children[0].variables,
                         {'q': scopes_tree.VariableInfo(constants.VARIABLE_STATE.INITIALIZED, 4),
                          'z': scopes_tree.VariableInfo(constants.VARIABLE_STATE.UNINITIALIZED, 5)})


class TestExtractVariables(unittest.TestCase):

    def test_empty_source(self):
        self.assertEqual(importer.extract_variables(''), ([], {}))

    def test_has_source(self):
        source = '''
x = 1 + y

def y():
  return x + z
'''
        self.assertEqual(set(importer.extract_variables(source)[0]),
                         {'z', 'y'})


class TestProcessModule(unittest.TestCase):

    SIMPLE_SOURCE = '''
x = 'X'

def y(z):
    return z + math.log(1)
'''

    def test_process_simple(self):
        module_name = 'process_simple_' + uuid.uuid4().hex

        with helpers.test_directory() as temp_directory:
            with open(os.path.join(temp_directory, module_name + '.py'), 'w') as f:
                f.write(self.SIMPLE_SOURCE)

            module = importlib.import_module(module_name)

            self.assertEqual(getattr(module, 'math', None), None)

            importer.process_module(module_config=config.DEFAULT_CONFIG,
                                    module=module)

            self.assertEqual(getattr(module, 'math'), math)

    def test_process_simple__cached(self):
        module_name = 'process_simple_' + uuid.uuid4().hex

        with helpers.test_directory() as temp_directory:
            with open(os.path.join(temp_directory, module_name + '.py'), 'w') as f:
                f.write(self.SIMPLE_SOURCE)

            module = importlib.import_module(module_name)

            self.assertEqual(getattr(module, 'math', None), None)

            # not required to create other temp directory, since filenames do not intersect
            test_config = config.DEFAULT_CONFIG.clone(cache_dir=temp_directory)

            importer.process_module(module_config=test_config,
                                    module=module)

            self.assertEqual(getattr(module, 'math'), math)

            self.assertTrue(os.path.isfile(os.path.join(temp_directory, module_name + '.cache')))

            with mock.patch('smart_imports.importer.extract_variables') as extract_variables:
                importer.process_module(module_config=test_config,
                                        module=module)

            extract_variables.assert_not_called()

    def prepair_data(self, temp_directory):
        modules_names = []

        for i in range(1, 5):
            modules_names.append('process_module_circular_{}_{}'.format(i, uuid.uuid4().hex))

        source_1 = '''
def import_hook():
    from smart_imports import config
    from smart_imports import importer
    from smart_imports import discovering

    target_module = discovering.find_target_module()

    importer.process_module(module_config=config.DEFAULT_CONFIG,
                            module=target_module)


import_hook()


x = 1


def y():
    return {module_2_name}.z()
'''.format(module_2_name=modules_names[1])

        source_2 = '''
def import_hook():
    from smart_imports import config
    from smart_imports import importer
    from smart_imports import discovering

    target_module = discovering.find_target_module()

    importer.process_module(module_config=config.DEFAULT_CONFIG,
                            module=target_module)


import_hook()


def z():
    return {module_1_name}.x
'''.format(module_1_name=modules_names[0])

        source_3 = '''
def import_hook():
    from smart_imports import config
    from smart_imports import importer
    from smart_imports import discovering

    target_module = discovering.find_target_module()

    importer.process_module(module_config=config.DEFAULT_CONFIG,
                            module=target_module)


import_hook()

x = 1

y = 10 + {module_4_name}.z

'''.format(module_4_name=modules_names[3])

        source_4 = '''

def import_hook():
    from smart_imports import config
    from smart_imports import importer
    from smart_imports import discovering

    target_module = discovering.find_target_module()

    importer.process_module(module_config=config.DEFAULT_CONFIG,
                            module=target_module)


import_hook()


z = 100 + {module_1_name}.x
'''.format(module_1_name=modules_names[0])

        sources = [source_1, source_2, source_3, source_4]

        for name, source in zip(modules_names, sources):
            with open(os.path.join(temp_directory, name + '.py'), 'w') as f:
                f.write(source)

        return modules_names

    def test_process_circular__local_namespace(self):

        with helpers.test_directory() as temp_directory:

            modules_names = self.prepair_data(temp_directory)

            module = importlib.import_module(modules_names[0])

            self.assertTrue(hasattr(module, modules_names[1]))

            self.assertEqual(module.y(), 1)

    def test_process_circular__global_namespace(self):
        with helpers.test_directory() as temp_directory:
            modules_names = self.prepair_data(temp_directory)

            module = importlib.import_module(modules_names[2])

            self.assertTrue(hasattr(module, modules_names[3]))

            self.assertEqual(module.y, 111)

    def test_no_import_found(self):
        module_name = 'process_module_no_imports_{}'.format(uuid.uuid4().hex)

        source = '''
def y():
    print(x)

def z():
    print(x)
'''
        with helpers.test_directory() as temp_directory:
            with open(os.path.join(temp_directory, module_name + '.py'), 'w') as f:
                f.write(source)

            module = importlib.import_module(module_name)

            with self.assertRaises(exceptions.NoImportFound) as error:
                importer.process_module(module_config=config.DEFAULT_CONFIG,
                                        module=module)

            self.assertEqual(set(error.exception.arguments['lines']), {3, 6})


class TestAll(unittest.TestCase):

    def test(self):
        self.assertNotIn('string', globals())

        importer.all(importlib.import_module('smart_imports.tests.test_importer'))

        self.assertIn('string', globals())

        self.assertEqual(string.digits, '0123456789')


class TestSimpleScript(unittest.TestCase):

    def prepair_modules(self, base_directory):
        os.makedirs(os.path.join(base_directory, 'a', 'b', 'c'))

        script = '''
import smart_imports

smart_imports.all()

myprint((__name__, datetime.datetime.now()))
        '''

        with open(os.path.join(base_directory, 'a.py'), 'w') as f:
            f.write(script)

        config = {'rules': [{'type': 'rule_predefined_names'},
                            {'type': 'rule_stdlib'},
                            {'type': 'rule_custom',
                             'variables': {'myprint': {'module': 'pprint', 'attribute': 'pprint'}}}]}

        with open(os.path.join(base_directory, 'smart_imports.json'), 'w') as f:
            f.write(json.dumps(config))

    def test(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            output = subprocess.check_output(['python', os.path.join(temp_directory, 'a.py')])

            self.assertIn(b"'__main__'", output)
            self.assertIn(b"datetime.datetime", output)

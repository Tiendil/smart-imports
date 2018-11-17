
import os
import math
import json
import unittest
import importlib
import subprocess

from .. import rules
from .. import config
from .. import helpers
from .. import importer
from .. import constants
from .. import exceptions
from .. import scopes_tree

from .fake_package import apply_rules as apply_rules_module
from .fake_package import process_module_simple as process_module_simple_module


TEST_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestApplyRules(unittest.TestCase):

    def setUp(self):
        self.source_module = 'smart_imports.tests.fake_package.config_variables'

        self.config = {'rules': [{'type': 'rule_custom',
                                  'variables': {'config_variable': {'module': self.source_module}}},
                                 {'type': 'rule_local_modules'},
                                 {'type': 'rule_stdlib'},
                                 {'type': 'rule_predefined_names'}]}

    def test_command_not_found(self):
        result = importer.apply_rules(module_config=self.config,
                                      module=apply_rules_module,
                                      variable='x')
        self.assertEqual(result, None)

    def test_command_found(self):
        command = importer.apply_rules(module_config=self.config,
                                       module=apply_rules_module,
                                       variable='config_variable')

        self.assertEqual(command, rules.ImportCommand(target_module=apply_rules_module,
                                                      target_attribute='config_variable',
                                                      source_module=self.source_module,
                                                      source_attribute=None))

    def test_rules_priority(self):
        config = {'rules': [{'type': 'rule_custom',
                             'variables': {'var_1': {'module': 'math'}}},
                            {'type': 'rule_custom',
                             'variables': {'var_1': {'module': 'json'}}}]}

        command = importer.apply_rules(module_config=config,
                                       module=apply_rules_module,
                                       variable='var_1')

        self.assertEqual(command, rules.ImportCommand(target_module=apply_rules_module,
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


class TestProcessModule(unittest.TestCase):

    def test_process_simple(self):
        self.assertEqual(getattr(process_module_simple_module, 'math', None), None)

        importer.process_module(module_config=config.DEFAULT_CONFIG,
                                module=process_module_simple_module)

        self.assertEqual(getattr(process_module_simple_module, 'math'), math)

    def test_process_circular__local_namespace(self):
        module = importlib.import_module('smart_imports.tests.fake_package.process_module_circular_1')

        self.assertTrue(hasattr(module, 'process_module_circular_2'))

        self.assertEqual(module.y(), 1)

    def test_process_circular__global_namespace(self):
        module = importlib.import_module('smart_imports.tests.fake_package.process_module_circular_3')

        self.assertTrue(hasattr(module, 'process_module_circular_4'))

        self.assertEqual(module.y, 111)

    def test_no_import_found(self):
        module = importlib.import_module('smart_imports.tests.fake_package.process_module_no_imports')

        with self.assertRaises(exceptions.NoImportFound):
            importer.process_module(module_config=config.DEFAULT_CONFIG,
                                    module=module)


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

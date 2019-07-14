
import os
import sys
import uuid
import unittest
import importlib

from unittest import mock

from .. import rules
from .. import config
from .. import helpers
from .. import exceptions


class TestCustomRule(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.config = {'variables': {'y': {'module': 'z'},
                                     'p': {'module': 'q', 'attribute': 'w'}}}
        self.rule = rules.CustomRule(config=self.config)

    def test_no_variables(self):
        command = rules.CustomRule(config={'variables': {}}).apply(module='module',
                                                                   variable='x')
        self.assertEqual(command, None)

    def test_no_variable(self):
        command = self.rule.apply(module='module',
                                  variable='x')
        self.assertEqual(command, None)

    def test_only_module(self):
        command = self.rule.apply(module='module',
                                  variable='y')
        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='y',
                                                      source_module='z',
                                                      source_attribute=None))

    def test_module_attribute(self):
        command = self.rule.apply(module='module',
                                  variable='p')
        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='p',
                                                      source_module='q',
                                                      source_attribute='w'))


class TestLocalModulesRule(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.rule = rules.LocalModulesRule(config={})

    def prepair_modules(self, base_directory):
        os.makedirs(os.path.join(base_directory, 'a', 'b', 'c'))

        with open(os.path.join(base_directory, 'a', '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'x.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'b', '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'b', 'y.py'), 'w') as f:
            f.write(' ')

    def test_wrong_package(self):
        module = type(os)('some_module')

        self.assertEqual(module.__package__, None)

        command = self.rule.apply(module=module,
                                  variable='y')

        self.assertEqual(command, None)

        command = self.rule.apply(module=mock.Mock(),
                                  variable='y')

        self.assertEqual(command, None)


    def test_module_found(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = importlib.import_module('a.b')

            command = self.rule.apply(module=module,
                                      variable='y')

            self.assertEqual(command, rules.ImportCommand(target_module=module,
                                                          target_attribute='y',
                                                          source_module='a.b.y',
                                                          source_attribute=None))

    def test_package_path_not_found(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = importlib.import_module('a.b')

            command = self.rule.apply(module=module,
                                      variable='x')

            self.assertEqual(command, None)


class TestGlobalModulesRule(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.rule = rules.GlobalModulesRule(config={})

    def test_no_global_module(self):
        module_name = 'global_module_{}'.format(uuid.uuid4().hex)

        with helpers.test_directory() as temp_directory:
            with open(os.path.join(temp_directory, '{}.py'.format(module_name)), 'w') as f:
                f.write(' ')

            module = type(os)('some_module')

            command = self.rule.apply(module=module,
                                      variable='y')

            self.assertEqual(command, None)

    def test_has_global_module(self):
        module_name = 'global_module_{}'.format(uuid.uuid4().hex)

        with helpers.test_directory() as temp_directory:
            with open(os.path.join(temp_directory, '{}.py'.format(module_name)), 'w') as f:
                f.write(' ')

            module = type(os)('some_module')

            command = self.rule.apply(module=module,
                                      variable=module_name)

            self.assertEqual(command, rules.ImportCommand(target_module=module,
                                                          target_attribute=module_name,
                                                          source_module=module_name,
                                                          source_attribute=None))


class TestStdLibRule(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.rule = rules.StdLibRule(config={})

    def test_system_modules(self):
        self.assertEqual(self.rule._STDLIB_MODULES['os'], {'module': 'os'})
        self.assertEqual(self.rule._STDLIB_MODULES['os_path'], {'module': 'os.path'})

    def test_builting_modules(self):
        self.assertTrue(set(sys.builtin_module_names).issubset(set(self.rule._STDLIB_MODULES.keys())))

    def test_not_system_module(self):
        command = self.rule.apply('module', 'bla_bla')
        self.assertEqual(command, None)

    def test_system_module(self):
        command = self.rule.apply('module', 'os_path')
        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='os_path',
                                                      source_module='os.path',
                                                      source_attribute=None))

    def test_builtin_module(self):
        command = self.rule.apply('module', 'math')
        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='math',
                                                      source_module='math',
                                                      source_attribute=None))


class TestPredifinedNamesRule(unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.rule = rules.PredefinedNamesRule(config={})

    def test_common_name(self):
        command = self.rule.apply('module', 'bla_bla')
        self.assertEqual(command, None)

    def test_predefined_names(self):
        for name in {'__name__', '__file__', '__doc__', '__annotations__'}:
            command = self.rule.apply('module', name)
            self.assertEqual(command, rules.NoImportCommand())


class TestPrefixRule(unittest.TestCase):

    def setUp(self):
        self.config = {'prefixes': [{"prefix": "other_", "module": "xxx.yyy"},
                                    {"prefix": "some_xxx_", "module": "aaa.bbb.qqq"},
                                    {"prefix": "some_", "module": "aaa.bbb"}]}
        self.rule = rules.PrefixRule(config=self.config)

    def test_wrong_prefix(self):
        command = self.rule.apply(module='module',
                                  variable='pqr_variable')
        self.assertEqual(command, None)

    def test_prefix_found(self):
        command = self.rule.apply(module='module',
                                  variable='some_variable')

        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='some_variable',
                                                      source_module='aaa.bbb.variable',
                                                      source_attribute=None))

    def test_prefix_order(self):
        command = self.rule.apply(module='module',
                                  variable='some_xxx_variable')

        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='some_xxx_variable',
                                                      source_module='aaa.bbb.qqq.variable',
                                                      source_attribute=None))


class TestLocalModulesFromParentRule(unittest.TestCase):

    def setUp(self):
        self.config = {"suffixes": [".c",
                                    ".b.c"]}
        self.rule = rules.LocalModulesFromParentRule(config=self.config)

    def prepair_modules(self, base_directory):
        os.makedirs(os.path.join(base_directory, 'a', 'b', 'c'))

        with open(os.path.join(base_directory, 'a', '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'x.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'b', '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'b', 'y.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'b', 'c', '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'b', 'c', 'z.py'), 'w') as f:
            f.write(' ')

    def test_no_parents_found(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = importlib.import_module('a.b.y')

            command = self.rule.apply(module=module,
                                      variable='xxx')

            self.assertEqual(command, None)

    def test_parents_found(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = importlib.import_module('a.b.c.z')

            command = self.rule.apply(module=module,
                                      variable='y')

            self.assertEqual(command, rules.ImportCommand(target_module=module,
                                                          target_attribute='y',
                                                          source_module='a.b.y',
                                                          source_attribute=None))

    def test_parents_found__complex(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = importlib.import_module('a.b.c.z')

            command = self.rule.apply(module=module,
                                      variable='x')

            self.assertEqual(command, rules.ImportCommand(target_module=module,
                                                          target_attribute='x',
                                                          source_module='a.x',
                                                          source_attribute=None))


class TestLocalModulesFromNamespaceRule(unittest.TestCase):

    def setUp(self):
        self.config = {'map': {'a.b': ['a.c'],
                               'a.c': ['a.b', 'a']}}
        self.rule = rules.LocalModulesFromNamespaceRule(config=self.config)

    def prepair_modules(self, base_directory):
        os.makedirs(os.path.join(base_directory, 'a', 'b'))
        os.makedirs(os.path.join(base_directory, 'a', 'c'))

        with open(os.path.join(base_directory, 'a', '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'x.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'b', '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'b', 'y.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'c', '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'c', 'z.py'), 'w') as f:
            f.write(' ')

    def test_no_module_found(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = importlib.import_module('a.x')

            command = self.rule.apply(module=module,
                                      variable='z')

            self.assertEqual(command, None)

    def test_no_relations_found(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = importlib.import_module('a.b.y')

            command = self.rule.apply(module=module,
                                      variable='q')

            self.assertEqual(command, None)

    def test_relation_found(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = importlib.import_module('a.b.y')

            command = self.rule.apply(module=module,
                                      variable='z')

            self.assertEqual(command, rules.ImportCommand(target_module=module,
                                                          target_attribute='z',
                                                          source_module='a.c.z',
                                                          source_attribute=None))

    def test_relation_found__second_relation(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = importlib.import_module('a.c.z')

            command = self.rule.apply(module=module,
                                      variable='x')

            self.assertEqual(command, rules.ImportCommand(target_module=module,
                                                          target_attribute='x',
                                                          source_module='a.x',
                                                          source_attribute=None))


class TestDefaultRules(unittest.TestCase):

    def test(self):
        self.assertCountEqual(rules._FABRICS.keys(), {'rule_local_modules_from_parent',
                                                      'rule_predefined_names',
                                                      'rule_stdlib',
                                                      'rule_prefix',
                                                      'rule_local_modules_from_namespace',
                                                      'rule_local_modules',
                                                      'rule_global_modules',
                                                      'rule_custom'})


class TestRegister(unittest.TestCase):

    def setUp(self):
        super().setUp()
        rules.remove('xxx')

    def tearDown(self):
        super().tearDown()
        rules.remove('xxx')

    def test_success(self):
        rules.register('xxx', 'my.rule')
        self.assertEqual(rules._FABRICS['xxx'], 'my.rule')

    def test_already_registered(self):
        rules.register('xxx', 'my.rule')

        with self.assertRaises(exceptions.RuleAlreadyRegistered):
            rules.register('xxx', 'my.rule')


class TestGetForConfig(unittest.TestCase):

    def setUp(self):
        super().setUp()
        rules.remove('xxx')
        rules.reset_rules_cache()

    def tearDown(self):
        super().tearDown()
        rules.remove('xxx')
        rules.reset_rules_cache()

    def test_no_rule(self):
        with self.assertRaises(exceptions.RuleNotRegistered):
            test_config = config.DEFAULT_CONFIG.clone(rules=[{'type': 'xxx'}])
            rules.get_for_config(test_config)

    def test_success(self):
        test_config = config.DEFAULT_CONFIG.clone(rules=[{"type": "rule_local_modules"},
                                                         {"type": "rule_stdlib"}])

        found_rules_1 = rules.get_for_config(test_config)
        found_rules_2 = rules.get_for_config(test_config)

        for rule_1, rule_2 in zip(found_rules_1, found_rules_2):
            self.assertIs(rule_1, rule_2)

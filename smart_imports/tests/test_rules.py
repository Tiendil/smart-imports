import sys
import unittest

from unittest import mock

from .. import rules
from .. import exceptions


class TestRuleCustom(unittest.TestCase):

    def test_no_variables(self):
        command = rules.rule_custom(config={},
                                    module='module',
                                    variable='x')
        self.assertEqual(command, None)

    def test_no_variable(self):
        command = rules.rule_custom(config={'variables': {'y': {'module': 'z'}}},
                                    module='module',
                                    variable='x')
        self.assertEqual(command, None)

    def test_only_module(self):
        command = rules.rule_custom(config={'variables': {'y': {'module': 'z'}}},
                                    module='module',
                                    variable='y')
        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='y',
                                                      source_module='z',
                                                      source_attribute=None))

    def test_module_attribute(self):
        command = rules.rule_custom(config={'variables': {'y': {'module': 'z',
                                                                'attribute': 'c'}}},
                                    module='module',
                                    variable='y')
        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='y',
                                                      source_module='z',
                                                      source_attribute='c'))


class TestRuleLocalModules(unittest.TestCase):

    def test_module_found(self):

        def simple_package_path(path):
            return path

        def simple_has_submodule(path, name):
            return True

        def simple_name(path):
            return path.replace('/', '.')

        class FakeModule:
            def __init__(self):
                self.__file__ = 'a/b/c'

        module = FakeModule()

        with mock.patch('smart_imports.discovering.determine_full_module_name', simple_name):
            with mock.patch('smart_imports.discovering.determine_package_path', simple_package_path):
                with mock.patch('smart_imports.discovering.has_submodule', simple_has_submodule):
                    command = rules.rule_local_modules(config={},
                                                       module=module,
                                                       variable='y')

        self.assertEqual(command, rules.ImportCommand(target_module=module,
                                                      target_attribute='y',
                                                      source_module='a.b.c.y',
                                                      source_attribute=None))

    def test_package_path_not_found(self):
        def simple_package_path(path):
            return None

        def simple_name(path):
            return path.replace('/', '.')

        class FakeModule:
            def __init__(self):
                self.__file__ = 'a/b/c'

        module = FakeModule()

        with mock.patch('smart_imports.discovering.determine_full_module_name', simple_name):
            with mock.patch('smart_imports.discovering.determine_package_path', simple_package_path):
                command = rules.rule_local_modules(config={},
                                                   module=module,
                                                   variable='y')

        self.assertEqual(command, None)


class TestSTDLIB_MODULES(unittest.TestCase):

    def test_system_modules(self):
        self.assertEqual(rules.STDLIB_MODULES['os'], {'module': 'os'})
        self.assertEqual(rules.STDLIB_MODULES['path'], {'module': 'os.path'})

    def test_builting_moduyles(self):
        self.assertTrue(set(sys.builtin_module_names).issubset(set(rules.STDLIB_MODULES.keys())))


class TestRuleSTDLIB(unittest.TestCase):

    def test_not_system_module(self):
        command = rules.rule_stdlib({}, 'module', 'bla_bla')
        self.assertEqual(command, None)

    def test_system_module(self):
        command = rules.rule_stdlib({}, 'module', 'path')
        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='path',
                                                      source_module='os.path',
                                                      source_attribute=None))

    def test_builtin_module(self):
        command = rules.rule_stdlib({}, 'module', 'math')
        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='math',
                                                      source_module='math',
                                                      source_attribute=None))


class TestRulePredifinedNames(unittest.TestCase):

    def test_common_name(self):
        command = rules.rule_predefined_names({}, 'module', 'bla_bla')
        self.assertEqual(command, None)

    def test_predefined_names(self):
        for name in {'__name__', '__file__', '__doc__', '__annotations__'}:
            command = rules.rule_predefined_names({}, 'module', name)
            self.assertEqual(command, rules.NoImportCommand())


class TestDefaultRules(unittest.TestCase):

    def test(self):
        self.assertCountEqual(rules.RULES.keys(), {'rule_parent_modules',
                                                   'rule_predefined_names',
                                                   'rule_stdlib',
                                                   'rule_prefix',
                                                   'rule_local_from_namespace',
                                                   'rule_local_modules',
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
        self.assertEqual(rules.RULES['xxx'], 'my.rule')

    def test_already_registered(self):
        rules.register('xxx', 'my.rule')

        with self.assertRaises(exceptions.RuleAlreadyRegistered):
            rules.register('xxx', 'my.rule')


class TestApply(unittest.TestCase):

    def setUp(self):
        super().setUp()
        rules.remove('xxx')

    def tearDown(self):
        super().tearDown()
        rules.remove('xxx')

    def test_no_rule(self):
        with self.assertRaises(exceptions.RuleNotRegistered):
            rules.apply(config={'type': 'xxx'},
                        module='module',
                        variable='variable')

    def test_success(self):
        rules.register('xxx', lambda *argv, **kwargs: 'yyy')

        command = rules.apply(config={'type': 'xxx'},
                              module='module',
                              variable='variable')

        self.assertEqual(command, 'yyy')

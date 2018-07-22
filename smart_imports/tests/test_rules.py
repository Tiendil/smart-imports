
import os
import sys
import types
import tempfile
import unittest
import contextlib

from unittest import mock

from .. import rules
from .. import exceptions


def unload_test_packages():
    for package_name in ['a']:
        for key, value in list(sys.modules.items()):
            if (key == package_name or key.startswith(package_name+'.')) and isinstance(value, types.ModuleType):
                del sys.modules[key]


@contextlib.contextmanager
def test_directory():
    unload_test_packages()

    with tempfile.TemporaryDirectory() as temp_directory:
        sys.path.append(temp_directory)
        yield temp_directory
        sys.path.pop()


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


class TestSTDLIBModules(unittest.TestCase):

    def test_system_modules(self):
        self.assertEqual(rules.STDLIB_MODULES['os'], {'module': 'os'})
        self.assertEqual(rules.STDLIB_MODULES['os_path'], {'module': 'os.path'})

    def test_builting_moduyles(self):
        self.assertTrue(set(sys.builtin_module_names).issubset(set(rules.STDLIB_MODULES.keys())))


class TestRuleSTDLIB(unittest.TestCase):

    def test_not_system_module(self):
        command = rules.rule_stdlib({}, 'module', 'bla_bla')
        self.assertEqual(command, None)

    def test_system_module(self):
        command = rules.rule_stdlib({}, 'module', 'os_path')
        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='os_path',
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


class TestRulePrefix(unittest.TestCase):

    def setUp(self):
        self.config = {'prefixes': [{"prefix": "other_", "module": "xxx.yyy"},
                                    {"prefix": "some_xxx_", "module": "aaa.bbb.qqq"},
                                    {"prefix": "some_", "module": "aaa.bbb"}]}

    def test_wrong_prefix(self):
        command = rules.rule_prefix(config=self.config,
                                    module='module',
                                    variable='pqr_variable')
        self.assertEqual(command, None)

    def test_prefix_found(self):
        command = rules.rule_prefix(config=self.config,
                                    module='module',
                                    variable='some_variable')

        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='some_variable',
                                                      source_module='aaa.bbb.variable',
                                                      source_attribute=None))

    def test_prefix_order(self):
        command = rules.rule_prefix(config=self.config,
                                    module='module',
                                    variable='some_xxx_variable')

        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='some_xxx_variable',
                                                      source_module='aaa.bbb.qqq.variable',
                                                      source_attribute=None))


class TestRuleLocalModulesFromParent(unittest.TestCase):

    def setUp(self):
        self.config = {"suffixes": [".c",
                                    ".b.c"]}

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

    def test_no_module_found(self):
        with test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            command = rules.rule_local_modules_from_parent(config=self.config,
                                                           module=mock.Mock(__file__=os.path.join(temp_directory, 'a', 'b', 'q.py')),
                                                           variable='xxx')
            self.assertEqual(command, None)

    def test_no_parents_found(self):
        with test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            command = rules.rule_local_modules_from_parent(config=self.config,
                                                           module=mock.Mock(__file__=os.path.join(temp_directory, 'a', 'b', 'y.py')),
                                                           variable='xxx')
            self.assertEqual(command, None)

    def test_parents_found(self):
        with test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = mock.Mock(__file__=os.path.join(temp_directory, 'a', 'b', 'c', 'z.py'))

            command = rules.rule_local_modules_from_parent(config=self.config,
                                                           module=module,
                                                           variable='y')

            self.assertEqual(command, rules.ImportCommand(target_module=module,
                                                          target_attribute='y',
                                                          source_module='a.b.y',
                                                          source_attribute=None))

    def test_parents_found__complex(self):
        with test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = mock.Mock(__file__=os.path.join(temp_directory, 'a', 'b', 'c', 'z.py'))

            command = rules.rule_local_modules_from_parent(config=self.config,
                                                           module=module,
                                                           variable='x')

            self.assertEqual(command, rules.ImportCommand(target_module=module,
                                                          target_attribute='x',
                                                          source_module='a.x',
                                                          source_attribute=None))


class TestRuleLocalModulesFromNamespace(unittest.TestCase):

    def setUp(self):
        self.config = {'map': {'a.b': ['a.c'],
                               'a.c': ['a.b', 'a']}}

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
        with test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = mock.Mock(__file__=os.path.join(temp_directory, 'a', 'x.py'))

            command = rules.rule_local_modules_from_namespace(config=self.config,
                                                              module=module,
                                                              variable='z')

            self.assertEqual(command, None)

    def test_no_relations_found(self):
        with test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = mock.Mock(__file__=os.path.join(temp_directory, 'a', 'b', 'y.py'))

            command = rules.rule_local_modules_from_namespace(config=self.config,
                                                              module=module,
                                                              variable='q')

            self.assertEqual(command, None)

    def test_relation_found(self):
        with test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = mock.Mock(__file__=os.path.join(temp_directory, 'a', 'b', 'y.py'))

            command = rules.rule_local_modules_from_namespace(config=self.config,
                                                              module=module,
                                                              variable='z')

            self.assertEqual(command, rules.ImportCommand(target_module=module,
                                                          target_attribute='z',
                                                          source_module='a.c.z',
                                                          source_attribute=None))

    def test_relation_found__second_relation(self):
        with test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            module = mock.Mock(__file__=os.path.join(temp_directory, 'a', 'c', 'z.py'))

            command = rules.rule_local_modules_from_namespace(config=self.config,
                                                              module=module,
                                                              variable='x')

            self.assertEqual(command, rules.ImportCommand(target_module=module,
                                                          target_attribute='x',
                                                          source_module='a.x',
                                                          source_attribute=None))


class TestDefaultRules(unittest.TestCase):

    def test(self):
        self.assertCountEqual(rules.RULES.keys(), {'rule_local_modules_from_parent',
                                                   'rule_predefined_names',
                                                   'rule_stdlib',
                                                   'rule_prefix',
                                                   'rule_local_modules_from_namespace',
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

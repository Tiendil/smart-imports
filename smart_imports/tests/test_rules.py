import os
import sys
import uuid
import tempfile
import unittest

from unittest import mock

from .. import rules
from .. import constants as c
from .. import exceptions as e


class TestRuleConfig(unittest.TestCase):

    def test_no_variables(self):
        command = rules.rule_config(config={},
                                    module='module',
                                    variable='x')
        self.assertEqual(command, None)

    def test_no_variable(self):
        command = rules.rule_config(config={'variables': {'y': {'module': 'z'}}},
                                    module='module',
                                    variable='x')
        self.assertEqual(command, None)

    def test_only_module(self):
        command = rules.rule_config(config={'variables': {'y': {'module': 'z'}}},
                                    module='module',
                                    variable='y')
        self.assertEqual(command, rules.ImportCommand(target_module='module',
                                                      target_attribute='y',
                                                      source_module='z',
                                                      source_attribute=None))

    def test_module_attribute(self):
        command = rules.rule_config(config={'variables': {'y': {'module': 'z',
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

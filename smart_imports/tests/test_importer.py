
import os
import math
import unittest
import importlib

from .. import rules
from .. import importer
from .. import constants
from .. import exceptions

from .fake_package import apply_rules as apply_rules_module
from .fake_package import process_module_simple as process_module_simple_module


TEST_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestApplyRules(unittest.TestCase):

    def setUp(self):
        self.source_module = 'smart_imports.tests.fake_package.config_variables'

        self.config = {'variables': {'config_variable': {'module': self.source_module}}}

    def test_no_rules(self):
        with self.assertRaises(exceptions.NoImportFound):
            importer.apply_rules(config=self.config,
                                 module=apply_rules_module,
                                 variable='x',
                                 rules=[])

    def test_command_not_found(self):
        with self.assertRaises(exceptions.NoImportFound):
            importer.apply_rules(config=self.config,
                                 module=apply_rules_module,
                                 variable='x',
                                 rules=[rules.rule_config])


    def test_command_found(self):
        command = importer.apply_rules(config=self.config,
                                       module=apply_rules_module,
                                       variable='config_variable',
                                       rules=[rules.rule_config])

        self.assertEqual(command, rules.ImportCommand(target_module=apply_rules_module,
                                                      target_attribute='config_variable',
                                                      source_module=self.source_module,
                                                      source_attribute=None))


class TestGetModuleScopesTree(unittest.TestCase):

    def test(self):
        test_path = os.path.join(TEST_FIXTURES_DIR, 'get_module_scopes_tree.py')

        scope = importer.get_module_scopes_tree(test_path)

        self.assertEqual(scope.variables, {'x': constants.VARIABLE_STATE.INITIALIZED,
                                           'y': constants.VARIABLE_STATE.INITIALIZED})

        self.assertEqual(scope.children[0].variables,
                         {'q': constants.VARIABLE_STATE.INITIALIZED,
                          'z': constants.VARIABLE_STATE.UNINITIALIZED})



class TestProcessModule(unittest.TestCase):

    def test_process_simple(self):
        self.assertEqual(getattr(process_module_simple_module, 'math', None), None)

        importer.process_module(config={},
                                module=process_module_simple_module,
                                rules=[rules.rule_stdlib])

        self.assertEqual(getattr(process_module_simple_module, 'math'), math)

    def test_process_circular__local_namespace(self):
        module = importlib.import_module('smart_imports.tests.fake_package.process_module_circular_1')

        self.assertTrue(hasattr(module, 'process_module_circular_2'))

        self.assertEqual(module.y(), 1)

    def test_process_circular__global_namespace(self):
        module = importlib.import_module('smart_imports.tests.fake_package.process_module_circular_3')

        self.assertTrue(hasattr(module, 'process_module_circular_4'))

        self.assertEqual(module.y, 111)


class TestAll(unittest.TestCase):

    def test(self):
        self.assertNotIn('string', globals())

        importer.all(importlib.import_module('smart_imports.tests.test_importer'))

        self.assertIn('string', globals())

        self.assertEqual(string.digits, '0123456789')

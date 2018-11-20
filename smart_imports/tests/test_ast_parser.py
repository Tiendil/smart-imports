
import os
import sys
import ast
import unittest

from .. import ast_parser
from .. import scopes_tree


TEST_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestAnalyzer(unittest.TestCase):

    @unittest.skipUnless(sys.version.startswith('3.5'), 'test only for python 3.5')
    def test_python_3_5(self):

        with open(os.path.join(TEST_FIXTURES_DIR, 'python_3_5', 'full_parser_test.py')) as f:
            code = f.read()

        tree = ast.parse(code)

        analyzer = ast_parser.Analyzer()

        analyzer.visit(tree)

        variables = scopes_tree.search_candidates_to_import(analyzer.scope)

        fully_undefined_variables, partialy_undefined_variables, variables_scopes = variables

        self.assertEqual(fully_undefined_variables,
                         {'перменная_2',
                          'annotation_1',
                          'annotation_2',
                          'var_3',
                          'var_7',
                          'var_8',
                          'var_11',
                          'var_12',
                          'var_15',
                          'var_22',
                          'var_24',
                          'var_27',
                          'var_38',
                          'var_39',
                          'var_42',
                          'var_44',
                          'var_47',
                          'var_48',
                          'var_50',
                          'var_51',
                          'var_53',
                          'var_55',
                          'var_57',
                          'super',
                          'abs',
                          'range',
                          'zip',
                          'print'})

        self.assertEqual(partialy_undefined_variables,
                         {'var_9',
                          'var_13',
                          'var_46'})

        self.assertEqual(variables_scopes['zip'][0].variables['zip'].line, 32)
        self.assertEqual(variables_scopes['var_33'][0].variables['var_33'].line, 50)

        self.assertEqual({scope.variables['var_46'].line for scope in variables_scopes['var_46']},
                         {66, 68})  # skip line 66 since it is the same scope with line 67 and loop assigment has priority

        self.assertEqual({scope.variables['var_56'].line for scope in variables_scopes['var_56']},
                         {79, 82})

    @unittest.skipUnless(sys.version.startswith('3.6'), 'test only for python 3.6')
    def test_python_3_6(self):

        with open(os.path.join(TEST_FIXTURES_DIR, 'python_3_6', 'full_parser_test.py')) as f:
            code = f.read()

        tree = ast.parse(code)

        analyzer = ast_parser.Analyzer()

        analyzer.visit(tree)

        variables = scopes_tree.search_candidates_to_import(analyzer.scope)

        fully_undefined_variables, partialy_undefined_variables, variables_scopes = variables

        self.assertEqual(fully_undefined_variables,
                         {'перменная_2',
                          'annotation_1',
                          'annotation_2',
                          'var_3',
                          'var_7',
                          'var_8',
                          'var_11',
                          'var_12',
                          'var_15',
                          'var_22',
                          'var_24',
                          'var_27',
                          'var_38',
                          'var_39',
                          'var_42',
                          'var_44',
                          'var_47',
                          'var_48',
                          'var_50',
                          'var_51',
                          'var_53',
                          'var_55',
                          'var_57',
                          'var_59',
                          'var_61',
                          'var_63',
                          'var_65',
                          'var_67',
                          'var_70',
                          'var_72',
                          'var_75',
                          'var_76',
                          'var_79',
                          'var_80',
                          'var_81',
                          'super',
                          'abs',
                          'range',
                          'zip',
                          'print'})

        self.assertEqual(partialy_undefined_variables,
                         {'var_9',
                          'var_13',
                          'var_46'})

        self.assertEqual(variables_scopes['zip'][0].variables['zip'].line, 32)
        self.assertEqual(variables_scopes['var_33'][0].variables['var_33'].line, 50)

        self.assertEqual({scope.variables['var_46'].line for scope in variables_scopes['var_46']},
                         {66, 68})  # skip line 66 since it is the same scope with line 67 and loop assigment has priority

        self.assertEqual({scope.variables['var_56'].line for scope in variables_scopes['var_56']},
                         {79, 82})

    @unittest.skipUnless(sys.version.startswith('3.7'), 'test only for python 3.7')
    def test_python_3_7(self):

        with open(os.path.join(TEST_FIXTURES_DIR, 'python_3_7', 'full_parser_test.py')) as f:
            code = f.read()

        tree = ast.parse(code)

        analyzer = ast_parser.Analyzer()

        analyzer.visit(tree)

        variables = scopes_tree.search_candidates_to_import(analyzer.scope)

        fully_undefined_variables, partialy_undefined_variables, variables_scopes = variables

        self.assertEqual(fully_undefined_variables,
                         {'перменная_2',
                          'annotation_1',
                          'annotation_2',
                          'var_3',
                          'var_7',
                          'var_8',
                          'var_11',
                          'var_12',
                          'var_15',
                          'var_22',
                          'var_24',
                          'var_27',
                          'var_38',
                          'var_39',
                          'var_42',
                          'var_44',
                          'var_47',
                          'var_48',
                          'var_50',
                          'var_51',
                          'var_53',
                          'var_55',
                          'var_57',
                          'var_59',
                          'var_61',
                          'var_63',
                          'var_65',
                          'var_67',
                          'var_70',
                          'var_72',
                          'var_75',
                          'var_76',
                          'var_79',
                          'var_80',
                          'var_81',
                          'super',
                          'abs',
                          'range',
                          'zip',
                          'print'})

        self.assertEqual(partialy_undefined_variables,
                         {'var_9',
                          'var_13',
                          'var_46'})

        self.assertEqual(variables_scopes['zip'][0].variables['zip'].line, 32)
        self.assertEqual(variables_scopes['var_33'][0].variables['var_33'].line, 50)

        self.assertEqual({scope.variables['var_46'].line for scope in variables_scopes['var_46']},
                         {66, 68})  # skip line 66 since it is the same scope with line 67 and loop assigment has priority

        self.assertEqual({scope.variables['var_56'].line for scope in variables_scopes['var_56']},
                         {79, 82})

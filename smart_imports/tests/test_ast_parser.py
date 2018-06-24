
import os
import ast
import unittest

from .. import ast_parser
from .. import scopes_tree


TEST_FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class TestAnalyzer(unittest.TestCase):

    def test_python_3_5(self):

        with open(os.path.join(TEST_FIXTURES_DIR, 'python_3_5', 'full_parser_test.py')) as f:
            code = f.read()

        tree = ast.parse(code)

        analyzer = ast_parser.Analyzer()

        analyzer.visit(tree)

        variables = scopes_tree.search_candidates_to_import(analyzer.scope)

        fully_undefined_variables, partialy_undefined_variables = variables

        self.assertEqual(fully_undefined_variables,
                         {'var_3', 'var_7', 'var_8', 'var_11', 'var_12', 'var_15', 'var_22', 'var_24', 'var_27', 'super', 'abs', 'range', 'zip'})
        self.assertEqual(partialy_undefined_variables,
                         {'var_9', 'var_13'})

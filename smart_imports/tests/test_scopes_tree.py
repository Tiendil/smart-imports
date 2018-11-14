
import unittest

from .. import scopes_tree
from .. import constants as c


class TestScope(unittest.TestCase):

    def test_initialization(self):
        scope = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)

        self.assertEqual(scope.type, c.SCOPE_TYPE.NORMAL)
        self.assertEqual(scope.variables, {})
        self.assertEqual(scope.children, [])
        self.assertEqual(scope.parent, None)

    def test_register_variable(self):
        scope = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)

        scope.register_variable('variable_name', 'state', line=7)

        self.assertEqual(scope.variables, {'variable_name': scopes_tree.VariableInfo('state', 7)})

    def test_register_variable__duplicate_registration(self):
        scope = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)

        scope.register_variable('variable_name', 'state.1', 7)
        scope.register_variable('variable_name', 'state.2', 8)

        self.assertEqual(scope.variables, {'variable_name': scopes_tree.VariableInfo('state.1', 7)})

    def test_add_child(self):
        scope_1 = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_2 = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_1.add_child(scope_2)

        self.assertEqual(scope_1.parent, None)
        self.assertEqual(scope_1.children, [scope_2])

        self.assertEqual(scope_2.parent, scope_1)
        self.assertEqual(scope_2.children, [])


class TestFindRoot(unittest.TestCase):

    def test_already_root(self):
        scope = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        self.assertEqual(scopes_tree.find_root(scope), scope)

    def test_not_root(self):
        scope_root = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_median = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_leaf = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)

        scope_root.add_child(scope_median)
        scope_median.add_child(scope_leaf)

        self.assertEqual(scopes_tree.find_root(scope_leaf), scope_root)
        self.assertEqual(scopes_tree.find_root(scope_median), scope_root)


class TestReversedBranch(unittest.TestCase):

    def test_already_root(self):
        scope = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        self.assertEqual(list(scopes_tree.reversed_branch(scope)), [scope])

    def test_not_root(self):
        scope_root = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_median = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_leaf = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)

        scope_root.add_child(scope_median)
        scope_median.add_child(scope_leaf)

        self.assertEqual(list(scopes_tree.reversed_branch(scope_leaf)),
                         [scope_leaf, scope_median, scope_root])

        self.assertEqual(list(scopes_tree.reversed_branch(scope_median)),
                         [scope_median, scope_root])


class TestGetVariableScopes(unittest.TestCase):

    def test_no_variables(self):
        scope = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        variables = scopes_tree.get_variables_scopes(scope)
        self.assertEqual(variables, {})

    def test_single_node(self):
        scope = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope.variables['var_1'] = 'state'
        scope.variables['var_2'] = 'state'

        variables = scopes_tree.get_variables_scopes(scope)

        self.assertEqual(variables, {'var_1': [scope],
                                     'var_2': [scope]})

    def test_single_branch(self):
        scope_root = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_root.variables['var_1'] = 'state'
        scope_root.variables['var_2'] = 'state'

        scope_median = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_median.variables['var_2'] = 'state'
        scope_median.variables['var_3'] = 'state'

        scope_leaf = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_leaf.variables['var_3'] = 'state'
        scope_leaf.variables['var_4'] = 'state'

        scope_root.add_child(scope_median)
        scope_median.add_child(scope_leaf)

        variables = scopes_tree.get_variables_scopes(scope_root)

        self.assertEqual(variables.keys(), {'var_1', 'var_2', 'var_3', 'var_4'})

        self.assertCountEqual(variables['var_1'], [scope_root])
        self.assertCountEqual(variables['var_2'], [scope_root, scope_median])
        self.assertCountEqual(variables['var_3'], [scope_median, scope_leaf])
        self.assertCountEqual(variables['var_4'], [scope_leaf])

    def test_tree(self):
        scope_root = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_root.variables['var_1'] = 'state'
        scope_root.variables['var_2'] = 'state'

        scope_median_1 = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_median_1.variables['var_2'] = 'state'
        scope_median_1.variables['var_3'] = 'state'

        scope_leaf_1 = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_leaf_1.variables['var_3'] = 'state'
        scope_leaf_1.variables['var_4'] = 'state'

        scope_median_2 = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_median_2.variables['var_4'] = 'state'
        scope_median_2.variables['var_5'] = 'state'

        scope_leaf_2 = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_leaf_2.variables['var_4'] = 'state'
        scope_leaf_2.variables['var_6'] = 'state'

        scope_leaf_3 = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_leaf_3.variables['var_5'] = 'state'
        scope_leaf_3.variables['var_6'] = 'state'

        scope_root.add_child(scope_median_1)
        scope_root.add_child(scope_median_2)

        scope_median_1.add_child(scope_leaf_1)

        scope_median_2.add_child(scope_leaf_2)
        scope_median_2.add_child(scope_leaf_3)

        variables = scopes_tree.get_variables_scopes(scope_root)

        self.assertEqual(variables.keys(), {'var_1', 'var_2', 'var_3', 'var_4', 'var_5', 'var_6'})

        self.assertCountEqual(variables['var_1'], [scope_root])
        self.assertCountEqual(variables['var_2'], [scope_root, scope_median_1])
        self.assertCountEqual(variables['var_3'], [scope_median_1, scope_leaf_1])
        self.assertCountEqual(variables['var_4'], [scope_leaf_1, scope_median_2, scope_leaf_2])
        self.assertCountEqual(variables['var_5'], [scope_median_2, scope_leaf_3])
        self.assertCountEqual(variables['var_6'], [scope_leaf_2, scope_leaf_3])


class TestIsVariableDefined(unittest.TestCase):

    def test_variable_not_in_scope(self):
        scope = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        self.assertFalse(scopes_tree.is_variable_defined('var_1', scope))

    def test_variable_initialized(self):
        scope = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope.register_variable('var_1', c.VARIABLE_STATE.INITIALIZED, 7)
        self.assertTrue(scopes_tree.is_variable_defined('var_1', scope))

    def test_branch_processing(self):
        scope_root = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_root.register_variable('var_1', c.VARIABLE_STATE.UNINITIALIZED, 7)
        scope_root.register_variable('var_2', c.VARIABLE_STATE.INITIALIZED, 8)

        scope_median = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_median.register_variable('var_2', c.VARIABLE_STATE.UNINITIALIZED, 9)
        scope_median.register_variable('var_3', c.VARIABLE_STATE.INITIALIZED, 10)

        scope_leaf = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_leaf.register_variable('var_1', c.VARIABLE_STATE.UNINITIALIZED, 11)
        scope_leaf.register_variable('var_2', c.VARIABLE_STATE.UNINITIALIZED, 12)
        scope_leaf.register_variable('var_3', c.VARIABLE_STATE.UNINITIALIZED, 13)

        scope_root.add_child(scope_median)
        scope_median.add_child(scope_leaf)

        self.assertFalse(scopes_tree.is_variable_defined('var_1', scope_leaf))
        self.assertTrue(scopes_tree.is_variable_defined('var_2', scope_leaf))
        self.assertTrue(scopes_tree.is_variable_defined('var_3', scope_leaf))

    def test_ignore_middle_class_scope(self):
        scope_root = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_root.register_variable('var_1', c.VARIABLE_STATE.UNINITIALIZED, 1)
        scope_root.register_variable('var_2', c.VARIABLE_STATE.INITIALIZED, 2)

        scope_median = scopes_tree.Scope(type=c.SCOPE_TYPE.CLASS)
        scope_median.register_variable('var_2', c.VARIABLE_STATE.UNINITIALIZED, 3)
        scope_median.register_variable('var_3', c.VARIABLE_STATE.INITIALIZED, 4)

        scope_leaf = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_leaf.register_variable('var_1', c.VARIABLE_STATE.UNINITIALIZED, 5)
        scope_leaf.register_variable('var_2', c.VARIABLE_STATE.UNINITIALIZED, 6)
        scope_leaf.register_variable('var_3', c.VARIABLE_STATE.UNINITIALIZED, 7)

        scope_root.add_child(scope_median)
        scope_median.add_child(scope_leaf)

        self.assertFalse(scopes_tree.is_variable_defined('var_1', scope_leaf))
        self.assertTrue(scopes_tree.is_variable_defined('var_2', scope_leaf))
        self.assertFalse(scopes_tree.is_variable_defined('var_3', scope_leaf))

    def test_not_ignore_original_class_scope(self):
        scope_root = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_root.register_variable('var_1', c.VARIABLE_STATE.UNINITIALIZED, 1)
        scope_root.register_variable('var_2', c.VARIABLE_STATE.INITIALIZED, 2)

        scope_median = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_median.register_variable('var_2', c.VARIABLE_STATE.UNINITIALIZED, 3)
        scope_median.register_variable('var_3', c.VARIABLE_STATE.INITIALIZED, 4)

        scope_leaf = scopes_tree.Scope(type=c.SCOPE_TYPE.CLASS)
        scope_leaf.register_variable('var_1', c.VARIABLE_STATE.UNINITIALIZED, 5)
        scope_leaf.register_variable('var_2', c.VARIABLE_STATE.UNINITIALIZED, 6)
        scope_leaf.register_variable('var_3', c.VARIABLE_STATE.UNINITIALIZED, 7)

        scope_root.add_child(scope_median)
        scope_median.add_child(scope_leaf)

        self.assertFalse(scopes_tree.is_variable_defined('var_1', scope_leaf))
        self.assertTrue(scopes_tree.is_variable_defined('var_2', scope_leaf))
        self.assertTrue(scopes_tree.is_variable_defined('var_3', scope_leaf))


class FakeUsageChecker:

    def __init__(self, results):
        self.results = results

    def __call__(self, variable, scope):
        return self.results.pop(0)


class TestDetermineVariableUsage(unittest.TestCase):

    def check(self, results, expected_state):
        scopes = [scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
                  for i in range(len(results))]
        real_state = scopes_tree.determine_variable_usage(variable='var_1',
                                                          scopes=scopes,
                                                          usage_checker=FakeUsageChecker(results))
        self.assertEqual(real_state, expected_state)

    def test(self):
        self.check([], c.VARIABLE_USAGE_TYPE.FULLY_UNDEFINED)
        self.check([True], c.VARIABLE_USAGE_TYPE.FULLY_DEFINED)
        self.check([False], c.VARIABLE_USAGE_TYPE.FULLY_UNDEFINED)
        self.check([True, True], c.VARIABLE_USAGE_TYPE.FULLY_DEFINED)
        self.check([False, True], c.VARIABLE_USAGE_TYPE.PARTIALY_DEFINED)
        self.check([False, False], c.VARIABLE_USAGE_TYPE.FULLY_UNDEFINED)


class TestSearchUndefinedVariableLines(unittest.TestCase):

    def test(self):
        scope_root = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_root.register_variable('var_1', c.VARIABLE_STATE.UNINITIALIZED, 1)
        scope_root.register_variable('var_2', c.VARIABLE_STATE.INITIALIZED, 2)

        scope_median = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_median.register_variable('var_2', c.VARIABLE_STATE.UNINITIALIZED, 3)

        scope_leaf = scopes_tree.Scope(type=c.SCOPE_TYPE.CLASS)
        scope_leaf.register_variable('var_1', c.VARIABLE_STATE.UNINITIALIZED, 4)
        scope_leaf.register_variable('var_2', c.VARIABLE_STATE.UNINITIALIZED, 5)
        scope_leaf.register_variable('var_3', c.VARIABLE_STATE.UNINITIALIZED, 6)

        scope_root.add_child(scope_median)
        scope_median.add_child(scope_leaf)

        self.assertEqual(scopes_tree.search_undefined_variable_lines('var_1',
                                                                     [scope_root, scope_leaf],
                                                                     scopes_tree.is_variable_defined),
                         [1, 4])

        self.assertEqual(scopes_tree.search_undefined_variable_lines('var_2',
                                                                     [scope_root, scope_median, scope_leaf],
                                                                     scopes_tree.is_variable_defined),
                         [])

        self.assertEqual(scopes_tree.search_undefined_variable_lines('var_3',
                                                                     [scope_leaf],
                                                                     scopes_tree.is_variable_defined),
                         [6])


class TestSearchCandidatesToImport(unittest.TestCase):

    def test(self):
        scope_root = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_root.register_variable('var_1', c.VARIABLE_STATE.UNINITIALIZED, 1)
        scope_root.register_variable('var_2', c.VARIABLE_STATE.INITIALIZED, 2)

        scope_median_1 = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_median_1.register_variable('var_2', c.VARIABLE_STATE.UNINITIALIZED, 3)
        scope_median_1.register_variable('var_3', c.VARIABLE_STATE.INITIALIZED, 4)

        scope_leaf = scopes_tree.Scope(type=c.SCOPE_TYPE.CLASS)
        scope_leaf.register_variable('var_1', c.VARIABLE_STATE.UNINITIALIZED, 5)
        scope_leaf.register_variable('var_2', c.VARIABLE_STATE.UNINITIALIZED, 6)
        scope_leaf.register_variable('var_3', c.VARIABLE_STATE.UNINITIALIZED, 7)

        scope_median_2 = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)
        scope_median_2.register_variable('var_2', c.VARIABLE_STATE.UNINITIALIZED, 8)
        scope_median_2.register_variable('var_3', c.VARIABLE_STATE.UNINITIALIZED, 9)

        scope_root.add_child(scope_median_1)
        scope_root.add_child(scope_median_2)
        scope_median_1.add_child(scope_leaf)

        variables = scopes_tree.search_candidates_to_import(scope_root)

        fully_undefined_variables, partialy_undefined_variables, variables_scopes = variables

        self.assertEqual(fully_undefined_variables, {'var_1'})
        self.assertEqual(partialy_undefined_variables, {'var_3'})
        self.assertEqual(variables_scopes, {'var_1': [scope_root, scope_leaf],
                                            'var_2': [scope_root, scope_median_1, scope_median_2, scope_leaf],
                                            'var_3': [scope_median_1, scope_median_2, scope_leaf]})

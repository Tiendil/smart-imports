
import unittest

from .. import scopes_tree


class TestScope(unittest.TestCase):

    def test_initialization(self):
        scope = scopes_tree.Scope(type='type')

        self.assertEqual(scope.type, 'type')
        self.assertEqual(scope.variables, {})
        self.assertEqual(scope.children, [])
        self.assertEqual(scope.parent, None)

    def test_register_variable(self):
        scope = scopes_tree.Scope(type='type')

        scope.register_variable('variable_name', 'state')

        self.assertEqual(scope.variables, {'variable_name': 'state'})

    def test_register_variable__duplicate_registration(self):
        scope = scopes_tree.Scope(type='type')

        scope.register_variable('variable_name', 'state.1')
        scope.register_variable('variable_name', 'state.2')

        self.assertEqual(scope.variables, {'variable_name': 'state.1'})

    def test_add_child(self):
        scope_1 = scopes_tree.Scope(type='type')
        scope_2 = scopes_tree.Scope(type='type')
        scope_1.add_child(scope_2)

        self.assertEqual(scope_1.parent, None)
        self.assertEqual(scope_1.children, [scope_2])

        self.assertEqual(scope_2.parent, scope_1)
        self.assertEqual(scope_2.children, [])

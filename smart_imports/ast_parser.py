

import ast

from . import constants as c
from . import scopes_tree


class Analyzer(ast.NodeVisitor):

    def __init__(self):
        super().__init__()
        self.scope = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)

    def register_variable_get(self, variable):
        self.scope.register_variable(variable, c.VARIABLE_STATE.UNINITIALIZED)

    def register_variable_set(self, variable):
        self.scope.register_variable(variable, c.VARIABLE_STATE.INITIALIZED)

    def push_scope(self, type):
        scope = scopes_tree.Scope(type)
        self.scope.add_child(scope)
        self.scope = scope

    def pop_scope(self):
        self.scope = self.scope.parent

    def visit_Name(self, node):
        if not isinstance(node.ctx, ast.Store):
            self.register_variable_get(node.id)
        else:
            self.register_variable_set(node.id)

        self.generic_visit(node)

    def _visit_scope(self, node, type):
        self.push_scope(type=type)
        self.generic_visit(node)
        self.pop_scope()

    def _visit_comprehension(self, node):
        self.push_scope(type=type)

        for generator in node.generators:
            self._visit_for_comprehension(generator)

        if hasattr(node, 'elt'):
            self.visit(node.elt)

        if hasattr(node, 'key'):
            self.visit(node.key)

        if hasattr(node, 'value'):
            self.visit(node.value)

        self.pop_scope()

    def _visit_for_comprehension(self, comprehension):
        self.visit(comprehension.iter)
        self.visit(comprehension.target)

        for if_expression in comprehension.ifs:
            self.visit(if_expression)

    def visit_ListComp(self, node):
        self._visit_comprehension(node)

    def visit_SetComp(self, node):
        self._visit_comprehension(node)

    def visit_GeneratorExp(self, node):
        self._visit_comprehension(node)

    def visit_DictComp(self, node):
        self._visit_comprehension(node)

    def visit_Import(self, node):
        for alias in node.names:
            self.register_variable_set(alias.asname if alias.asname else alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.register_variable_set(alias.asname if alias.asname else alias.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.register_variable_set(node.name)
        self._visit_scope(node, type=c.SCOPE_TYPE.NORMAL)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Lambda(self, node):
        self._visit_scope(node, type=c.SCOPE_TYPE.NORMAL)

    def visit_arguments(self, node):
        for arg in node.args:
            self.register_variable_set(arg.arg)

        for arg in node.kwonlyargs:
            self.register_variable_set(arg.arg)

        if node.vararg:
            self.register_variable_set(node.vararg.arg)

        if node.kwarg:
            self.register_variable_set(node.kwarg.arg)

        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.register_variable_set(node.name)

        self.push_scope(type=c.SCOPE_TYPE.CLASS)

        for keyword in node.keywords:
            self.register_variable_set(keyword)

        self.generic_visit(node)
        self.pop_scope()

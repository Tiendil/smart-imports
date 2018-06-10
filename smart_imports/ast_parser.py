

import ast
import enum


class VARIABLE_STATE(enum.Enum):
    INITIALIZED = 0
    UNINITIALIZED = 1


class Scope:
    __slots__ = ('variables_states',)

    def __init__(self):
        self.variables_states = {}

    def register_variable_get(self, variable):
        if variable in self.variables_states:
            return

        self.variables_states[variable] = VARIABLES_STATE.UNINITIALIZED

    def register_variable_set(self, variable):
        if variable in self.variables_states:
            return

        self.variables_states[variable] = VARIABLES_STATE.INITIALIZED


class Analyzer(ast.NodeVisitor):

    def __init__(self):
        super().__init__()
        self.scopes = [Scope()]

    def register_variable_get(self, variable):
        self.scopes[-1].register_variable_get(variable)

    def register_variable_set(self, variable):
        self.scopes[-1].register_variable_set(variable)

    def push_scope(self):
        self.scopes.append(Scope())

    def pop_scope(self):
        self.scopes.pop()

    def visit_Name(self, node):
        if not isinstance(node.ctx, ast.Store):
            self.register_variable_get(node.id)
        else:
            self.register_variable_set(node.id)

        self.generic_visit(node)

    def _visit_scope(self, node):
        self.push_scope()
        self.generic_visit(node)
        self.pop_scope()

    def visit_ListComp(self, node):
        self._visit_scope(node)

    def visit_SetComp(self, node):
        self._visit_scope(node)

    def visit_GeneratorExp(self, node):
        self._visit_scope(node)

    def visit_DictComp(self, node):
        self._visit_scope(node)

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
        self._visit_scope(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Lambda(self, node):
        self._visit_scope(node)

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

    def visit_Global(self, node):
        # TODO: implement
        self.generic_visit(node)

    def visit_NonLocal(self, node):
        # TODO: implement
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.register_variable_set(node.name)

        self.push_scope()

        for keyword in self.node.keywords:
            self.register_variable_set(keyword)

        self.generic_visit(node)
        self.pop_scope()



import ast

from . import constants as c
from . import scopes_tree


class Analyzer(ast.NodeVisitor):

    def __init__(self):
        super().__init__()
        self.scope = scopes_tree.Scope(type=c.SCOPE_TYPE.NORMAL)

    def register_variable_get(self, variable, line):
        self.scope.register_variable(variable, c.VARIABLE_STATE.UNINITIALIZED, line)

    def register_variable_set(self, variable, line):
        self.scope.register_variable(variable, c.VARIABLE_STATE.INITIALIZED, line)

    def push_scope(self, type):
        scope = scopes_tree.Scope(type)
        self.scope.add_child(scope)
        self.scope = scope

    def pop_scope(self):
        self.scope = self.scope.parent

    def visit_Name(self, node):
        if not isinstance(node.ctx, ast.Store):
            self.register_variable_get(node.id, node.lineno)
        else:
            self.register_variable_set(node.id, node.lineno)

    def _visit_comprehension(self, node):
        self.push_scope(type=c.SCOPE_TYPE.COMPREHENSION)

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
            self.register_variable_set(alias.asname if alias.asname else alias.name,
                                       node.lineno)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            self.register_variable_set(alias.asname if alias.asname else alias.name,
                                       node.lineno)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.register_variable_set(node.name, node.lineno)

        for decorator in node.decorator_list:
            self.visit(decorator)

        self.visit_default_arguments(node.args)

        if node.returns is not None:
            self.visit(node.returns)

        self.push_scope(type=c.SCOPE_TYPE.NORMAL)

        self.visit_arguments(node.args)

        for body_node in node.body:
            self.visit(body_node)

        self.pop_scope()

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Lambda(self, node):
        self.visit_default_arguments(node.args)

        self.push_scope(type=c.SCOPE_TYPE.NORMAL)

        self.visit_arguments(node.args)

        self.visit(node.body)

        self.pop_scope()

    def visit_default_arguments(self, node):
        for default in node.defaults:
            if default is None:
                continue

            self.visit(default)

        for default in node.kw_defaults:
            if default is None:
                continue

            self.visit(default)

    def process_arg(self, arg):
        self.register_variable_set(arg.arg, arg.lineno)

        if arg.annotation is not None:
            self.visit(arg.annotation)

    def visit_arguments(self, node):
        if hasattr(node, 'posonlyargs'):
            for arg in node.posonlyargs :
                self.process_arg(arg)

        for arg in node.args:
            self.process_arg(arg)

        for arg in node.kwonlyargs:
            self.process_arg(arg)

        if node.vararg:
            self.process_arg(node.vararg)

        if node.kwarg:
            self.process_arg(node.kwarg)

    def visit_ClassDef(self, node):
        self.register_variable_set(node.name, node.lineno)

        self.push_scope(type=c.SCOPE_TYPE.CLASS)

        for keyword in node.keywords:
            self.register_variable_set(keyword, node.lineno)

        self.generic_visit(node)
        self.pop_scope()

    def visit_ExceptHandler(self, node):
        if node.type:
            self.visit(node.type)

        self.push_scope(type=c.SCOPE_TYPE.NORMAL)

        if node.name:
            self.register_variable_set(node.name, node.lineno)

        for body_node in node.body:
            self.visit(body_node)

        self.pop_scope()

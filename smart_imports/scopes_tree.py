
import collections

from . import constants as c


class VariableInfo:
    __slots__ = ('state', 'line')

    def __init__(self, state, line):
        self.state = state
        self.line = line

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.state == other.state and
                self.line == other.line)

    def __ne__(self, other):
        return not self.__ne__(other)

    def __repr__(self):
        return 'VariableInfo({}, {})'.format(repr(self.state), self.line)


class Scope:
    __slots__ = ('variables', 'variables_lines', 'type', 'children', 'parent')

    def __init__(self, type):
        self.type = type
        self.variables = {}
        self.children = []
        self.parent = None

    def register_variable(self, variable, state, line):
        if variable in self.variables:
            return

        self.variables[variable] = VariableInfo(state, line)

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def level(self):
        if self.parent is None:
            return 0

        return self.parent.level() + 1


def find_root(scope):
    while scope.parent:
        scope = scope.parent

    return scope


def reversed_branch(scope):

    while scope:
        yield scope
        scope = scope.parent


def get_variables_scopes(root_scope):

    variables = {}

    queue = collections.deque()

    queue.append(root_scope)

    while queue:
        scope = queue.popleft()

        queue.extend(scope.children)

        for variable in scope.variables:
            if variable not in variables:
                variables[variable] = []

            variables[variable].append(scope)

    return variables


def is_variable_defined(variable, scope):

    if variable not in scope.variables:
        return False

    if scope.variables[variable].state == c.VARIABLE_STATE.INITIALIZED:
        return True

    for scope in reversed_branch(scope):
        if scope.type == c.SCOPE_TYPE.CLASS:
            continue

        variable_info = scope.variables.get(variable)

        if variable_info and variable_info.state == c.VARIABLE_STATE.INITIALIZED:
            return True

    return False


def determine_variable_usage(variable, scopes, usage_checker):

    if not scopes:
        return c.VARIABLE_USAGE_TYPE.FULLY_UNDEFINED

    counter = collections.Counter(1 if usage_checker(variable, scope) else 0
                                  for scope in scopes)

    if counter.get(1) == len(scopes):
        return c.VARIABLE_USAGE_TYPE.FULLY_DEFINED

    if counter.get(0) == len(scopes):
        return c.VARIABLE_USAGE_TYPE.FULLY_UNDEFINED

    return c.VARIABLE_USAGE_TYPE.PARTIALY_DEFINED


def search_undefined_variable_lines(variable, scopes, usage_checker=is_variable_defined):

    if not scopes:
        return []

    lines = []

    for scope in scopes:
        if usage_checker(variable, scope):
            continue

        lines.append(scope.variables[variable].line)

    lines.sort()

    return lines


def search_candidates_to_import(root_scope):
    variables_scopes = get_variables_scopes(root_scope)

    fully_undefined_variables = set()
    partialy_undefined_variables = set()

    for variable, scopes in variables_scopes.items():
        variable_usage = determine_variable_usage(variable=variable,
                                                  scopes=scopes,
                                                  usage_checker=is_variable_defined)

        if variable_usage == c.VARIABLE_USAGE_TYPE.FULLY_DEFINED:
            continue

        if variable_usage == c.VARIABLE_USAGE_TYPE.FULLY_UNDEFINED:
            fully_undefined_variables.add(variable)
            continue

        partialy_undefined_variables.add(variable)

    return fully_undefined_variables, partialy_undefined_variables, variables_scopes


import collections

from . import constants as c


class Scope:
    __slots__ = ('variables_states', 'type', 'children', 'parent')

    def __init__(self, type):
        self.type = type
        self.variables_states = {}
        self.children = []
        self.parent = None

    def register_variable_get(self, variable):
        if variable in self.variables_states:
            return

        self.variables_states[variable] = c.VARIABLES_STATE.UNINITIALIZED

    def register_variable_set(self, variable):
        if variable in self.variables_states:
            return

        self.variables_states[variable] = c.VARIABLES_STATE.INITIALIZED

    def add_child(self, child):
        self.children.append(child)
        child.parent = self

    def find_root(self):
        if self.parent is None:
            return self

        return self.parent.find_root()

    def reversed_branch(self):
        if self.parent is None:
            return

        yield self

        yield from self.parent.reversed_branch()


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

    if scope.variables[variable] = c.VARIABLES_STATE.INITIALIZED:
        return True

    for scope in scope.reversed_branch():
        if scope.type == c.SCOPE_TYPE.CLASS:
            continue

        if scope.variables.get(variable) == c.VARIABLES_STATE.INITIALIZED:
            return True

    return False


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

    return fully_undefined_variables, partialy_undefined_variables


def determine_variable_usage(variable, scopes, usage_checker):

    counter = collections.Counter(1 if usage_checker(variable, scope) else 0
                                  for scope in scopes)

    if counter.get(1) == len(scopes):
        return c.VARIABLE_USAGE_TYPE.FULLY_DEFINED

    if counter.get(0) == len(scopes):
        return VARIABLE_USAGE_TYPE.FULLY_UNDEFINED

    return VARIABLE_USAGE_TYPE.PARTIALY_DEFINED

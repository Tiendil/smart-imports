
import os
import sys
import importlib
import importlib.util

from . import exceptions
from . import discovering


RULES = {}


def register(name, rule):
    if name in RULES:
        raise exceptions.RuleAlreadyRegistered(rule=name)

    RULES[name] = rule


def remove(name):
    if name in RULES:
        del RULES[name]


def apply(config, module, variable):
    name = config['type']

    if name not in RULES:
        raise exceptions.RuleNotRegistered(rule=name)

    return RULES[name](config, module, variable)


class ImportCommand:
    __slots__ = ('target_module', 'target_attribute', 'source_module', 'source_attribute')

    def __init__(self, target_module, target_attribute, source_module, source_attribute):
        self.target_module = target_module
        self.target_attribute = target_attribute
        self.source_module = source_module
        self.source_attribute = source_attribute

    def __call__(self):
        imported_module = importlib.import_module(self.source_module)

        if self.source_attribute is None:
            value = imported_module
        else:
            value = getattr(imported_module, self.source_attribute)

        setattr(self.target_module, self.target_attribute, value)

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                self.target_module == other.target_module and
                self.target_attribute == other.target_attribute and
                self.source_module == other.source_module and
                self.source_attribute == other.source_attribute)

    def __ne__(self, other):
        return not self.__ne__(other)


class NoImportCommand(ImportCommand):
    __slots__ = ()

    def __init__(self):
        super().__init__(target_module=None,
                         target_attribute=None,
                         source_module=None,
                         source_attribute=None)

    def __call__(self):
        pass


def rule_custom(config, module, variable):

    if 'variables' not in config:
        return None

    if variable not in config['variables']:
        return None

    module_name = config['variables'][variable]['module']
    attribute = config['variables'][variable].get('attribute')
    return ImportCommand(module, variable, module_name, attribute)


def rule_local_modules(config, module, variable):

    package_path = discovering.determine_package_path(module.__file__)

    if package_path is None:
        return None

    if not discovering.has_submodule(package_path, variable):
        return None

    parent_module_name = discovering.determine_full_module_name(package_path)

    return ImportCommand(target_module=module,
                         target_attribute=variable,
                         source_module='{}.{}'.format(parent_module_name, variable),
                         source_attribute=None)


# packages lists for every python version can be found here:
# https://github.com/jackmaney/python-stdlib-list
def _collect_stdlib_modules():
    variables = {}

    for compiled_module_name in sys.builtin_module_names:
        variables[compiled_module_name] = {'module': compiled_module_name}

    with open(os.path.join(os.path.dirname(__file__), 'fixtures', 'python_3_5_packages.txt')) as f:
        for line in f.readlines():
            names = line.strip().split('.')
            for i in range(len(names)):
                variables['_'.join(names[:i+1])] = {'module': '.'.join(names[:i+1])}

    return variables


STDLIB_MODULES = _collect_stdlib_modules()


def rule_stdlib(config, module, variable):

    if variable not in STDLIB_MODULES:
        return None

    module_name = STDLIB_MODULES[variable]['module']
    attribute = STDLIB_MODULES[variable].get('attribute')

    return ImportCommand(module, variable, module_name, attribute)


PREDEFINED_NAMES = frozenset({'__file__', '__annotations__'})


def rule_predefined_names(config, module, variable):

    if variable in PREDEFINED_NAMES:
        return NoImportCommand()

    if variable in __builtins__:
        return NoImportCommand()

    return None


def rule_prefix(config, module, variable):

    for rule in config['prefixes']:

        prefix = rule['prefix']

        if not variable.startswith(prefix):
            continue

        return ImportCommand(module, variable, '{}.{}'.format(rule['module'], variable[len(prefix):]), None)

    return None


def rule_parent_modules(config, module, variable):

    package_path = discovering.determine_package_path(module.__file__)

    if package_path is None:
        return None

    for suffix in config['suffixes']:
        path = package_path.replace(os.sep, '.')
        if path.endswith(suffix):
            package_path = package_path[:-len(suffix)]
            break

    if not discovering.has_submodule(package_path, variable):
        return None

    parent_module_name = discovering.determine_full_module_name(package_path)

    return ImportCommand(target_module=module,
                         target_attribute=variable,
                         source_module='{}.{}'.format(parent_module_name, variable),
                         source_attribute=None)


def rule_local_from_namespace(config, module, variable):

    package_path = discovering.determine_package_path(module.__file__)

    if package_path is None:
        return None

    for target, namespace in config['map'].items():
        path = package_path.replace(os.sep, '.')

        if path.endswith(target):
            package_path = importlib.util.find_spec(namespace).origin
            if package_path.endswith('__init__.py'):
                package_path = os.path.dirname(package_path)
            break

    if not discovering.has_submodule(package_path, variable):
        return None

    parent_module_name = discovering.determine_full_module_name(package_path)

    return ImportCommand(target_module=module,
                         target_attribute=variable,
                         source_module='{}.{}'.format(parent_module_name, variable),
                         source_attribute=None)


register('rule_predefined_names', rule_predefined_names)
register('rule_local_modules', rule_local_modules)
register('rule_custom', rule_custom)
register('rule_stdlib', rule_stdlib)
register('rule_prefix', rule_prefix)
register('rule_parent_modules', rule_parent_modules)
register('rule_local_from_namespace', rule_local_from_namespace)

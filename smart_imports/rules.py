
import os
import sys
import pkgutil
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
        return not self.__eq__(other)


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


LOCAL_MODULES_CACHE = {}


def rule_local_modules(config, module, variable):

    package_name = module.__package__

    if package_name not in LOCAL_MODULES_CACHE:
        parent = sys.modules[package_name]

        local_modules = set()

        for module_finder, name, ispkg in pkgutil.iter_modules(path=parent.__path__):
            local_modules.add(name)

        LOCAL_MODULES_CACHE[package_name] = frozenset(local_modules)

    if variable not in LOCAL_MODULES_CACHE[package_name]:
        return None

    return ImportCommand(target_module=module,
                         target_attribute=variable,
                         source_module='{}.{}'.format(package_name, variable),
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


def rule_local_modules_from_parent(config, module, variable):

    package_name = module.__package__

    for suffix in config['suffixes']:

        if not package_name.endswith(suffix):
            continue

        base_package_name = package_name[:-len(suffix)]

        source_module = '{}.{}'.format(base_package_name, variable)

        if discovering.find_spec(source_module) is None:
            continue

        return ImportCommand(target_module=module,
                             target_attribute=variable,
                             source_module=source_module,
                             source_attribute=None)


def rule_local_modules_from_namespace(config, module, variable):

    package_name = module.__package__

    for target, namespaces in config['map'].items():
        for namespace in namespaces:

            if package_name != target:
                continue

            spec = discovering.find_spec(namespace)

            if spec is None:
                continue

            namespace_package = spec.parent

            source_module = '{}.{}'.format(namespace_package, variable)

            if discovering.find_spec(source_module) is None:
                continue

            return ImportCommand(target_module=module,
                                 target_attribute=variable,
                                 source_module=source_module,
                                 source_attribute=None)


register('rule_predefined_names', rule_predefined_names)
register('rule_local_modules', rule_local_modules)
register('rule_custom', rule_custom)
register('rule_stdlib', rule_stdlib)
register('rule_prefix', rule_prefix)
register('rule_local_modules_from_parent', rule_local_modules_from_parent)
register('rule_local_modules_from_namespace', rule_local_modules_from_namespace)

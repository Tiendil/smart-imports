
import os
import sys
import pkgutil
import importlib
import importlib.util

from . import exceptions
from . import discovering


_FABRICS = {}
_RULES = {}


def register(name, rule):
    if name in _FABRICS:
        raise exceptions.RuleAlreadyRegistered(rule=name)

    _FABRICS[name] = rule


def remove(name):
    if name in _FABRICS:
        del _FABRICS[name]


def get_for_config(config):
    uid = config.uid

    if uid not in _RULES:
        rules = []

        for rule_config in config.rules:
            fabric_type = rule_config['type']

            if fabric_type not in _FABRICS:
                raise exceptions.RuleNotRegistered(rule=fabric_type)

            rule = _FABRICS[fabric_type](config=rule_config)

            if not rule.verify_config():
                raise exceptions.ConfigHasWrongFormat(path=config.path,
                                                      message='wrong format of rule {}'.format(fabric_type))

            rules.append(rule)

        _RULES[uid] = rules

    return _RULES[uid]


def reset_rules_cache():
    _RULES.clear()


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


class _BaseRule:
    __slots__ = ('config',)

    def __init__(self, config):
        self.config = config

    def verify_config(self):
        return True

    def apply(self, module, variable):
        raise NotImplementedError


class CustomRule(_BaseRule):
    __slots__ = ()

    def verify_config(self):
        if 'variables' not in self.config:
            return False

        return super().verify_config()

    def apply(self, module, variable):

        if variable not in self.config['variables']:
            return None

        module_name = self.config['variables'][variable]['module']
        attribute = self.config['variables'][variable].get('attribute')
        return ImportCommand(module, variable, module_name, attribute)


class LocalModulesRule(_BaseRule):
    __slots__ = ()

    _LOCAL_MODULES_CACHE = {}

    def verify_config(self):
        return super().verify_config()

    def apply(self, module, variable):

        package_name = getattr(module, '__package__', None)

        if not package_name:
            return None

        if package_name not in self._LOCAL_MODULES_CACHE:
            parent = sys.modules[package_name]

            local_modules = set()

            for module_finder, name, ispkg in pkgutil.iter_modules(path=parent.__path__):
                local_modules.add(name)

            self._LOCAL_MODULES_CACHE[package_name] = frozenset(local_modules)

        if variable not in self._LOCAL_MODULES_CACHE[package_name]:
            return None

        return ImportCommand(target_module=module,
                             target_attribute=variable,
                             source_module='{}.{}'.format(package_name, variable),
                             source_attribute=None)


class GlobalModulesRule(_BaseRule):
    __slots__ = ()

    def verify_config(self):
        return super().verify_config()

    def apply(self, module, variable):

        loader = pkgutil.find_loader(variable)

        if loader is None:
            return None

        return ImportCommand(target_module=module,
                             target_attribute=variable,
                             source_module=variable,
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


class StdLibRule(_BaseRule):
    __slots__ = ('_stdlib_modules',)

    _STDLIB_MODULES = _collect_stdlib_modules()

    def verify_config(self):
        return super().verify_config()

    def apply(self, module, variable):

        if variable not in self._STDLIB_MODULES:
            return None

        module_name = self._STDLIB_MODULES[variable]['module']
        attribute = self._STDLIB_MODULES[variable].get('attribute')

        return ImportCommand(module, variable, module_name, attribute)


class PredefinedNamesRule(_BaseRule):
    __slots__ = ()

    PREDEFINED_NAMES = frozenset({'__file__', '__annotations__'})

    def verify_config(self):
        return super().verify_config()

    def apply(self, module, variable):

        if variable in self.PREDEFINED_NAMES:
            return NoImportCommand()

        if variable in __builtins__:
            return NoImportCommand()

        return None


class PrefixRule(_BaseRule):
    __slots__ = ()

    def verify_config(self):
        if 'prefixes' not in self.config:
            return False

        for rule in self.config['prefixes']:
            if 'prefix' not in rule:
                return False

        return super().verify_config()

    def apply(self, module, variable):

        for rule in self.config['prefixes']:
            prefix = rule['prefix']

            if not variable.startswith(prefix):
                continue

            return ImportCommand(module, variable, '{}.{}'.format(rule['module'], variable[len(prefix):]), None)

        return None


class LocalModulesFromParentRule(_BaseRule):
    __slots__ = ()

    def verify_config(self):
        if 'suffixes' not in self.config:
            return False

        return super().verify_config()

    def apply(self, module, variable):

        package_name = module.__package__

        for suffix in self.config['suffixes']:

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


class LocalModulesFromNamespaceRule(_BaseRule):
    __slots__ = ()

    def verify_config(self):
        return super().verify_config()

    def apply(self, module, variable):

        if 'map' not in self.config:
            return False

        package_name = module.__package__

        for target, namespaces in self.config['map'].items():
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


register('rule_predefined_names', PredefinedNamesRule)
register('rule_local_modules', LocalModulesRule)
register('rule_global_modules', GlobalModulesRule)
register('rule_custom', CustomRule)
register('rule_stdlib', StdLibRule)
register('rule_prefix', PrefixRule)
register('rule_local_modules_from_parent', LocalModulesFromParentRule)
register('rule_local_modules_from_namespace', LocalModulesFromNamespaceRule)

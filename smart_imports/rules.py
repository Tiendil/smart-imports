
import os
import importlib

from . import discovering


class ImportCommand:
    __slots__ = ('target_module', 'target_attribute', 'source_module', 'source_attribute')

    def __init__(self, target_module, target_attribute, source_module, source_attribute):
        self.target_module = target_module
        self.target_attribute = target_attribute
        self.source_module = source_module
        self.source_attribute = source_attribute

    def __call__(self):
        imported_module = __import__(self.source_module,
                                     globals=self.target_module.__dict__,
                                     locals=self.target_module.__dict__)

        if self.source_attribute is None:
            value = self.imported_module
        else:
            value = getattr(self.imported_module, self.source_attribute)

        setattr(self.target_module, self.target_attribute, value)


def rule_config(config, module, variable):

    if 'variables' not in config:
        return None

    if variable not in config['variables']:
        return None

    module_name = config['variables'][variable]['module']
    attribute = config['variables'][variable].get('attribute')

    return ImportCommand(module, variable, module_name, attribute)

def rule_local_modules(config, module, variable):
    module_name = discovering.determine_full_module_name(module.__path__)
    return ImportCommand(module, variable, '{}.{}'.format(module_name, variable))


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
                variables[names[i]] = {'module': '.'.join(names[:i+1])}

    return variables


STDLIB_MODULES = _collect_stdlib_modules()


def rule_stdlib(config, module, variable):
    module_name = STDLIB_MODULES[variable]['module']
    attribute = STDLIB_MODULES[variable].get('attribute')

    return ImportCommand(module, variable, module_name, attribute)

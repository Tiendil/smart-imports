
import ast
import itertools

from . import rules
from . import config
from . import ast_parser
from . import exceptions
from . import scopes_tree
from . import discovering


def apply_rules(module_config, module, variable):

    for rule_name in module_config['rules_order']:

        command = rules.apply(rule_name, module_config['rules'], module, variable)

        if command:
            return command

    raise exceptions.NoImportFound(module=module, variable=variable)


def get_module_scopes_tree(module_path):
    with open(module_path) as f:
        code = f.read()

    tree = ast.parse(code)

    analyzer = ast_parser.Analyzer()

    analyzer.visit(tree)

    return analyzer.scope


def process_module(module_config, module):

    root_scope = get_module_scopes_tree(module.__file__)

    variables = scopes_tree.search_candidates_to_import(root_scope)

    fully_undefined_variables, partialy_undefined_variables = variables

    commands = []

    for variable in itertools.chain(fully_undefined_variables, partialy_undefined_variables):
        command = apply_rules(module_config=module_config,
                              module=module,
                              variable=variable)
        commands.append(command)

    for command in commands:
        command()


def all(target_module=None):

    if target_module is None:
        target_module = discovering.find_target_module()

    module_config = config.get(target_module.__file__)

    process_module(module_config=module_config,
                   module=target_module)

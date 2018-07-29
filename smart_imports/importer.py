
import ast

from . import rules
from . import config
from . import ast_parser
from . import exceptions
from . import scopes_tree
from . import discovering


def apply_rules(module_config, module, variable):

    for rule_config in module_config['rules']:

        command = rules.apply(rule_config, module, variable)

        if command:
            return command

    raise exceptions.NoImportFound(variable=variable,
                                   module=module.__name__,
                                   path=module.__file__)


def get_module_scopes_tree(module_path):
    with open(module_path, encoding='utf-8') as f:
        code = f.read()

    tree = ast.parse(code)

    analyzer = ast_parser.Analyzer()

    analyzer.visit(tree)

    return analyzer.scope


def variables_processor(variables):
    return variables


def process_module(module_config, module, variables_processor=variables_processor):

    root_scope = get_module_scopes_tree(module.__file__)

    variables = scopes_tree.search_candidates_to_import(root_scope)

    fully_undefined_variables, partialy_undefined_variables = variables

    # sort variables to fixate import order
    variables = list(fully_undefined_variables)
    variables.extend(partialy_undefined_variables)
    variables.sort()

    variables = variables_processor(variables)

    commands = []

    for variable in variables:
        command = apply_rules(module_config=module_config,
                              module=module,
                              variable=variable)
        commands.append(command)

    for command in commands:
        command()


def all(target_module=None, variables_processor=variables_processor):

    if target_module is None:
        target_module = discovering.find_target_module()

    module_config = config.get(target_module.__file__)

    process_module(module_config=module_config,
                   module=target_module,
                   variables_processor=variables_processor)

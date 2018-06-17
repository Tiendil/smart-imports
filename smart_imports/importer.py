
import ast
import itertools

from . import rules
from . import ast_parser
from . import exceptions
from . import scopes_tree
from . import discovering


def apply_rules(config, module, variable, rules):

    for rule in rules:
        command = rule(config, module, variable)

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


def process_module(config, module, rules):

    root_scope = get_module_scopes_tree(module.__file__)

    variables = scopes_tree.search_candidates_to_import(root_scope)

    fully_undefined_variables, partialy_undefined_variables = variables

    commands = []

    for variable in itertools.chain(fully_undefined_variables, partialy_undefined_variables):
        command = apply_rules(config=config,
                              module=module,
                              variable=variable,
                              rules=rules)
        commands.append(command)

    for command in commands:
        command()


def all(target_module=None):

    if target_module is None:
        target_module = discovering.find_target_module()

    config_path = discovering.find_config_file(target_module.__file__)

    config = {}

    if config_path is not None:
        config = discovering.load_config(config_path)

    process_module(config=config,
                   module=target_module,
                   rules=[rules.rule_predefined_names,
                          rules.rule_config,
                          rules.rule_local_modules,
                          rules.rule_stdlib])

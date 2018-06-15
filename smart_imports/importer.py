
import itertools

from . import rules
from . import ast_parser
from . import exceptions
from . import discovering


def process_rules(config, module, variable, rules):

    command = None

    for rule in rules:
        command = rule(config, module, variable)

        if command:
            break

    if command is None:
        raise exceptions.ModuleSearchError(module.__file__)

    command()


def process_module(config, module, rules):

    with open(module.__file__) as f:
        code = f.read()

    tree = ast.parse(code)

    analyzer = ast_parser.Analyzer()

    analyzer.visit(tree)

    variables = scopes_tree.search_candidates_to_import(analyzer.scope)

    fully_undefined_variables, partialy_undefined_variables = variables

    for variable in itertools.chain(fully_undefined_variables, partialy_undefined_variables):
        process_rules(config=config,
                      module=module,
                      variable=variable,
                      rules=rules)


def all():

    target_module = discovering.find_target_module()

    config = discovering.find_config(target_module.__file__)

    process_module(config=config,
                   module=target_module,
                   rules=[rules.rule_config,
                          rules.rule_stdlib,
                          rules.rule_local_modules])

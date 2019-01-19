
import ast

from . import cache
from . import rules
from . import config
from . import ast_parser
from . import exceptions
from . import scopes_tree
from . import discovering


def apply_rules(module_config, module, variable):

    for rule in rules.get_for_config(module_config):
        command = rule.apply(module, variable)

        if command:
            return command

    return None


def get_module_scopes_tree(source):
    tree = ast.parse(source)

    analyzer = ast_parser.Analyzer()

    analyzer.visit(tree)

    return analyzer.scope


def variables_processor(variables):
    return variables


def extract_variables(source):

    root_scope = get_module_scopes_tree(source)

    variables = scopes_tree.search_candidates_to_import(root_scope)

    fully_undefined_variables, partialy_undefined_variables, variables_scopes = variables

    variables = list(fully_undefined_variables)
    variables.extend(partialy_undefined_variables)

    return variables, variables_scopes


def process_module(module_config, module, variables_processor=variables_processor):

    source = module.__loader__.get_source(module.__name__)

    parser_cache = cache.Cache(cache_dir=module_config.cache_dir,
                               module_name=module.__name__,
                               source=source)

    variables = parser_cache.get()

    variables_scopes = None

    if variables is None:
        variables, variables_scopes = extract_variables(source=source)

        parser_cache.set(variables)

    # sort variables to fixate import order
    variables.sort()

    variables = variables_processor(variables)

    commands = []

    for variable in variables:
        command = apply_rules(module_config=module_config,
                              module=module,
                              variable=variable)

        if command is not None:
            commands.append(command)
            continue

        # process import error
        if variables_scopes is None:
            _, variables_scopes = extract_variables(source=source)

        undefined_lines = scopes_tree.search_undefined_variable_lines(variable, variables_scopes[variable])

        raise exceptions.NoImportFound(variable=variable,
                                       module=module.__name__,
                                       path=module.__file__,
                                       lines=undefined_lines)

    for command in commands:
        command()


def all(target_module=None, variables_processor=variables_processor):

    if target_module is None:
        target_module = discovering.find_target_module()

    module_config = config.get(target_module.__file__)

    process_module(module_config=module_config,
                   module=target_module,
                   variables_processor=variables_processor)


import importlib

from mypy.plugin import Plugin
from mypy import nodes

from smart_imports import config as sm_config
from smart_imports import importer as sm_importer


class SmartImportsPlugin(Plugin):

    # search for imports and add them to AST of files, processed by mypy
    def get_additional_deps(self, file_node):

        smart_import_import = None

        for imported_module in file_node.imports:

            if not isinstance(imported_module, nodes.Import):
                # TODO: check all nodes
                continue

            for fullname, name in imported_module.ids:
                if fullname == 'smart_imports':
                    smart_import_import = imported_module
                    break

            if smart_import_import is None:
                continue

        if smart_import_import is None:
            return []

        import_index = file_node.defs.index(smart_import_import) + 1

        module_config = sm_config.get(file_node.path)

        target_module = importlib.import_module(file_node.fullname)

        commands = sm_importer.process_module(module_config=module_config,
                                              module=target_module,
                                              variables_processor=sm_importer.variables_processor)

        dependencies = []

        for command in commands:
            dependencies.append((0, command.source_module, -1))

            if command.source_attribute is None:
                new_import = nodes.Import(ids=[(command.source_module, command.target_attribute)])
            else:
                names = [(command.source_attribute,
                          command.target_attribute if command.source_attribute != command.target_attribute else None)]

                new_import = nodes.ImportFrom(id=command.source_module,
                                              names=names,
                                              relative=0)

            new_import.line = smart_import_import.line
            new_import.column = smart_import_import.column
            new_import.end_line = smart_import_import.end_line
            new_import.is_top_level = True
            new_import.is_unreachable = False

            file_node.defs.insert(import_index, new_import)
            file_node.imports.append(new_import)

        return dependencies


def plugin(version: str):
    return SmartImportsPlugin

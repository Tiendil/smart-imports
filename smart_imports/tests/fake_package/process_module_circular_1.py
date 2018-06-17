
def import_hook():
    from smart_imports import rules
    from smart_imports import importer
    from smart_imports import discovering

    target_module = discovering.find_target_module()

    importer.process_module(config={},
                            module=target_module,
                            rules=[rules.rule_local_modules])


import_hook()


x = 1


def y():
    return process_module_circular_2.z()

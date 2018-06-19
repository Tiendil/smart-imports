
def import_hook():
    from smart_imports import config
    from smart_imports import importer
    from smart_imports import discovering

    target_module = discovering.find_target_module()

    importer.process_module(module_config=config.DEFAULT_CONFIG,
                            module=target_module)


import_hook()


z = 100 + process_module_circular_1.x

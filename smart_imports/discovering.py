
import os
import json
import inspect

from . import constants


def find_target_module():

    for frame_info in inspect.stack():
        if frame_info.function == '<module>':
            return inspect.getmodule(frame_info.frame)


def find_config_file(path, config_name):
    if not os.path.isdir(path):
        path = os.path.dirname(path)

    while path:
        file_name = os.path.join(path, config_name)

        if os.path.isfile(file_name):
            return filename

        path = os.path.dirname(path)

    return None


def find_config(path):
    config_path = find_config_file(path, constants.CONFIG_FILE_NAME)

    if config_path is None:
        return None

    with open(config_path) as f:
        return json.load(f)

    return None


def determine_full_module_name(path):
    base_path = path

    if not os.path.isdir(base_path):
        base_path = os.path.dirname(base_path)

    while os.path.isfile(os.path.join(base_path, '__init__.py')):
        base_path = os.path.dirname(base_path)

    module_name = path[len(base_path):]

    if module_name.endswith('.py'):
        module_name = module_name[:-3]

    module_name = module_name.replace('\\', '/')

    while module_name[0] == '/':
        module_name = module_name[1:]

    while module_name[-1] == '/':
        module_name = module_name[:-1]

    return module_name.replace('/', '.')

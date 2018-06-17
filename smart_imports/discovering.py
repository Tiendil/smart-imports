
import os
import json
import inspect

from . import constants
from . import exceptions


def find_target_module():

    for frame_info in inspect.stack():
        if frame_info.function == '<module>':
            return inspect.getmodule(frame_info.frame)


def find_config_file(path, config_name=constants.CONFIG_FILE_NAME):
    if not os.path.isdir(path):
        path = os.path.dirname(path)

    while path != '/':

        file_name = os.path.join(path, config_name)

        if os.path.isfile(file_name):
            return file_name

        path = os.path.dirname(path)

    return None


def load_config(path):

    if not os.path.isfile(path):
        raise exceptions.ConfigNotFound(path=path)

    with open(path) as f:
        try:
            return json.load(f)
        except ValueError:
            raise exceptions.ConfigHasWrongFormat(path=path)


def determine_full_module_name(path):
    base_path = path

    if not os.path.isdir(base_path):
        base_path = os.path.dirname(base_path)

    while os.path.isfile(os.path.join(base_path, '__init__.py')):
        base_path = os.path.dirname(base_path)

    module_name = path[len(base_path):]

    if module_name.endswith('.py'):
        module_name = module_name[:-3]

    double_separator = os.sep + os.sep

    while double_separator in module_name:
        module_name = module_name.replace(double_separator, os.sep)

    while module_name and module_name[0] == os.sep:
        module_name = module_name[1:]

    while module_name and module_name[-1] == os.sep:
        module_name = module_name[:-1]

    return module_name.replace(os.sep, '.')


def determine_package_path(path):

    if os.path.isdir(path):
        return path

    if not os.path.isfile(path):
        return None

    if not path.endswith('.py'):
        return None

    return os.path.dirname(path)

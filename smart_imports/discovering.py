
import os
import sys
import inspect


def find_target_module():
    # can not use inspect.stack() here becaouse of bug, look:
    # - https://github.com/ipython/ipython/issues/1456/
    # - https://github.com/ipython/ipython/commit/298fdab5025745cd25f7f48147d8bc4c65be9d4a#diff-fd943bf091e5f13c5ef9b58043fa5129R209
    # - https://mail.python.org/pipermail/python-list/2010-September/587974.html
    #
    # instead emulate simplier behaviour (and, probably, it faster)

    frame = sys._getframe(1)

    while frame:
        if frame.f_code.co_name == '<module>':
            return inspect.getmodule(frame)

        frame = frame.f_back


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


def has_submodule(path, name):
    return (os.path.isfile(os.path.join(path, name, '__init__.py')) or
            os.path.isfile(os.path.join(path, name + '.py')))

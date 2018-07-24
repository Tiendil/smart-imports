
import sys
import inspect
import importlib


def find_target_module():
    # can not use inspect.stack() here becouse of bug, look:
    # - https://github.com/ipython/ipython/issues/1456/
    # - https://github.com/ipython/ipython/commit/298fdab5025745cd25f7f48147d8bc4c65be9d4a#diff-fd943bf091e5f13c5ef9b58043fa5129R209
    # - https://mail.python.org/pipermail/python-list/2010-September/587974.html
    #
    # instead emulate simplier behaviour (and, probably, faster)

    frame = sys._getframe(1)

    while frame:
        if frame.f_code.co_name == '<module>':
            # faster than inspect.getmodule(frame)
            for module in sys.modules.values():
                if getattr(module, '__file__', None) == frame.f_code.co_filename:
                    return module

            return sys.modules[inspect.getmodulename(frame.f_code.co_filename)]

        frame = frame.f_back


SPEC_CACHE = {}


def find_spec(module_name):
    if module_name not in SPEC_CACHE:
        SPEC_CACHE[module_name] = importlib.util.find_spec(module_name)

    return SPEC_CACHE[module_name]


import sys
import types
import tempfile
import contextlib

from . import discovering


def unload_test_packages():
    for package_name in ['a']:
        for key, value in list(sys.modules.items()):
            if (key == package_name or key.startswith(package_name+'.')) and isinstance(value, types.ModuleType):
                del sys.modules[key]

    discovering.SPEC_CACHE.clear()


@contextlib.contextmanager
def test_directory():
    unload_test_packages()

    with tempfile.TemporaryDirectory() as temp_directory:
        sys.path.append(temp_directory)
        yield temp_directory
        sys.path.pop()

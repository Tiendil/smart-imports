
import os
import pathlib
import hashlib
import warnings
import functools

from . import constants


WARNING_MESSAGE = 'Error while accessing smart imports cache'


def get_checksum(source):
    return hashlib.sha256(source.encode('utf-8')).hexdigest()


def get_cache_path(cache_dir, module_name):
    return os.path.join(cache_dir, module_name + '.cache')


def ignore_errors(function):

    @functools.wraps(function)
    def wrapper(*argv, **kwargs):
        try:
            return function(*argv, **kwargs)
        except Exception as e:
            warnings.warn('{}: {}'.format(WARNING_MESSAGE, e), UserWarning, stacklevel=2)
            return None

    return wrapper


@ignore_errors
def get(cache_dir, module_name, checksum):

    cache_path = get_cache_path(cache_dir, module_name)

    if not os.path.isfile(cache_path):
        return None

    with open(cache_path) as f:
        protocol_version = f.readline().strip()

        if protocol_version != constants.CACHE_PROTOCOL_VERSION:
            return None

        saved_checksum = f.readline().strip()

        if saved_checksum != checksum:
            return None

        variables = [variable.strip() for variable in f.readlines()]

    return variables


@ignore_errors
def set(cache_dir, module_name, checksum, variables):
    pathlib.Path(cache_dir).mkdir(parents=True, exist_ok=True)

    cache_path = get_cache_path(cache_dir, module_name)

    with open(cache_path, 'w') as f:
        f.write(constants.CACHE_PROTOCOL_VERSION)
        f.write('\n')

        f.write(checksum)
        f.write('\n')

        for variable in variables:
            f.write(variable)
            f.write('\n')


class Cache:
    __slots__ = ('cache_dir', 'module_name', 'checksum',)

    def __init__(self, cache_dir, module_name, source):
        self.cache_dir = cache_dir
        self.module_name = module_name
        self.checksum = get_checksum(source)

    def get(self):
        if self.cache_dir is None:
            return None

        return get(cache_dir=self.cache_dir,
                   module_name=self.module_name,
                   checksum=self.checksum)

    def set(self, variables):
        if self.cache_dir is None:
            return None

        set(cache_dir=self.cache_dir,
            module_name=self.module_name,
            checksum=self.checksum,
            variables=variables)

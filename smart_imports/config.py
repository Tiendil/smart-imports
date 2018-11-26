
import os
import json
import copy
import pathlib

from . import constants
from . import exceptions


CONFIGS_CACHE = {}


def expand_cache_dir_path(config_path, cache_dir):

    if cache_dir is None:
        return cache_dir

    path = pathlib.Path(cache_dir)

    if path.is_absolute():
        return cache_dir

    if cache_dir[0] == '~':
        return str(path.expanduser())

    return str(pathlib.Path(config_path).parent / cache_dir)


class Config:
    __slots__ = ('path', 'cache_dir', 'rules')

    def __init__(self):
        self.path = None
        self.cache_dir = None
        self.rules = []

    @property
    def uid(self):
        return self.path

    def initialize(self, path, data):
        self.path = path

        self.cache_dir = expand_cache_dir_path(config_path=path,
                                               cache_dir=data.get('cache_dir', self.cache_dir))

        if 'rules' not in data:
            raise exceptions.ConfigHasWrongFormat(path=path, message='"rules" MUST be defined')

        self.rules = data['rules']

        for rule_config in self.rules:
            if 'type' not in rule_config:
                raise exceptions.ConfigHasWrongFormat(path=path, message='rule type does not specified for every rule')

    def serialize(self):
        return {'path': self.path,
                'cache_dir': self.cache_dir,
                'rules': self.rules}

    def clone(self, **kwargs):
        clone = copy.deepcopy(self)

        for field, value in kwargs.items():
            setattr(clone, field, value)

        return clone

    def __eq__(self, other):
        return (self.__class__ == other.__class__ and
                all(getattr(self, field) == getattr(other, field) for field in self.__slots__))

    def __ne__(self, other):
        return not self.__eq__(other)


DEFAULT_CONFIG = Config()

DEFAULT_CONFIG.initialize(path='#default_config',
                          data={'rules': [{'type': 'rule_local_modules'},
                                          {'type': 'rule_stdlib'},
                                          {'type': 'rule_predefined_names'},
                                          {'type': 'rule_global_modules'}]})


def get(path, config_name=constants.CONFIG_FILE_NAME):

    if not os.path.isdir(path):
        path = os.path.dirname(path)

    config = None
    checked_paths = []

    while path != '/':

        if path in CONFIGS_CACHE:
            config = CONFIGS_CACHE[path]
            break

        checked_paths.append(path)

        config_path = os.path.join(path, config_name)

        if os.path.isfile(config_path):
            config = load(config_path)
            break

        path = os.path.dirname(path)

    if config is None:
        config = DEFAULT_CONFIG.clone(path=path)

    for path in checked_paths:
        CONFIGS_CACHE[path] = config

    return config


def load(path):

    if not os.path.isfile(path):
        raise exceptions.ConfigNotFound(path=path)

    with open(path) as f:
        try:
            data = json.load(f)
        except ValueError as e:
            raise exceptions.ConfigHasWrongFormat(path=path, message=str(e))

    config = Config()

    config.initialize(path, data)

    return config

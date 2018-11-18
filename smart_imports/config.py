
import os
import json
import uuid

from . import constants
from . import exceptions


CONFIGS_CACHE = {}


DEFAULT_CONFIG = {'uid': 'smart_imports_default_config',
                  'path': None,
                  'rules': [{'type': 'rule_local_modules'},
                            {'type': 'rule_stdlib'},
                            {'type': 'rule_predefined_names'}]}


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
        config = DEFAULT_CONFIG

    for path in checked_paths:
        CONFIGS_CACHE[path] = config

    if 'uid' not in config:
        config['uid'] = uuid.uuid4().hex

    if 'path' not in config:
        config['path'] = config_path

    return config


def load(path):

    if not os.path.isfile(path):
        raise exceptions.ConfigNotFound(path=path)

    with open(path) as f:
        try:
            config = json.load(f)
        except ValueError as e:
            raise exceptions.ConfigHasWrongFormat(path=path, message=str(e))

    check(path, config)

    return config


def check(path, config):
    if 'rules' not in config:
        raise exceptions.ConfigHasWrongFormat(path=path, message='"rules" MUST be defined')

    for rule_config in config['rules']:
        if 'type' not in rule_config:
            raise exceptions.ConfigHasWrongFormat(path=path, message='rule type does not specified for every rule')


import os
import json

from . import constants
from . import exceptions


CONFIGS_CACHE = {}


DEFAULT_CONFIG = {'rules_order': ['rule_predefined_names',
                                  'rule_local_modules',
                                  'rule_custom',
                                  'rule_stdlib'],

                  'rules': {'rule_predefined_names': {},
                            'rule_local_modules': {},
                            'rule_custom': {'variables': {}},
                            'rule_stdlib': {}}}


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

    return config


def load(path):

    if not os.path.isfile(path):
        raise exceptions.ConfigNotFound(path=path)

    with open(path) as f:
        try:
            config = json.load(f)
        except ValueError:
            raise exceptions.ConfigHasWrongFormat(path=path, message='not in JSON format')

    check(path, config)

    return config


def check(path, config):
    if 'rules_order' not in config:
        raise exceptions.ConfigHasWrongFormat(path=path, message='"rules_order" MUST be defined')

    if 'rules' not in config:
        raise exceptions.ConfigHasWrongFormat(path=path, message='"rules" MUST be defined')

    for rule_name in config['rules_order']:
        if rule_name not in config['rules']:
            raise exceptions.ConfigHasWrongFormat(path=path, message='"rules" does not contain config for rule "{}"'.format(rule_name))

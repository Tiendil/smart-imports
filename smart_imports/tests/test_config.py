
import os
import json
import uuid
import copy
import tempfile
import unittest

from .. import config
from .. import constants
from .. import exceptions


class TestGet(unittest.TestCase):

    def setUp(self):
        super().setUp()
        config.CONFIGS_CACHE.clear()

    def tearDown(self):
        super().tearDown()
        config.CONFIGS_CACHE.clear()

    def prepair_data(self, temp_directory):
        path = os.path.join(temp_directory,
                            'dir_with_not_reached_config',
                            'dir_with_config',
                            'empty_dir',
                            'leaf_dir')
        os.makedirs(path)

        with open(os.path.join(temp_directory,
                               'dir_with_not_reached_config',
                               constants.CONFIG_FILE_NAME), 'w') as f:
            data = copy.deepcopy(config.DEFAULT_CONFIG)
            data['test'] = 1
            f.write(json.dumps(data))

        with open(os.path.join(temp_directory,
                               'dir_with_not_reached_config',
                               'dir_with_config',
                               constants.CONFIG_FILE_NAME), 'w') as f:
            data = copy.deepcopy(config.DEFAULT_CONFIG)
            data['test'] = 2
            f.write(json.dumps(data))

        return path

    def test_get(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            leaf_path = self.prepair_data(temp_directory)

            loaded_config = config.get(leaf_path)

            data = copy.deepcopy(config.DEFAULT_CONFIG)
            data['test'] = 2

            self.assertEqual(data, loaded_config)

        # test cache here, file already removed, but cached data still exists
        loaded_config = config.get(leaf_path)

        self.assertEqual(data, loaded_config)

        self.assertEqual(config.CONFIGS_CACHE,
                         {leaf_path: data,
                          os.path.dirname(leaf_path): data,
                          os.path.dirname(os.path.dirname(leaf_path)): data})

    maxDiff = None
    def test_two_configs(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            leaf_path_1 = self.prepair_data(temp_directory)

            leaf_path_2 = leaf_path_1 + '2'
            os.makedirs(leaf_path_2)

            with open(os.path.join(leaf_path_2, constants.CONFIG_FILE_NAME), 'w') as f:
                data_2 = copy.deepcopy(config.DEFAULT_CONFIG)
                data_2['test'] = 3
                f.write(json.dumps(data_2))

            loaded_config_1 = config.get(leaf_path_1)
            loaded_config_2 = config.get(leaf_path_2)

            data_1 = copy.deepcopy(config.DEFAULT_CONFIG)
            data_1['test'] = 2

            self.assertEqual(data_1, loaded_config_1)
            self.assertEqual(data_2, loaded_config_2)

        self.assertEqual(config.CONFIGS_CACHE,
                         {leaf_path_2: data_2,
                          leaf_path_1: data_1,
                          os.path.dirname(leaf_path_1): data_1,
                          os.path.dirname(os.path.dirname(leaf_path_1)): data_1})

    def test_not_found_find(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            leaf_path = self.prepair_data(temp_directory)

            loaded_config = config.get(leaf_path, config_name='not_found.json')

            self.assertEqual(loaded_config, config.DEFAULT_CONFIG)


class TestLoad(unittest.TestCase):

    def test_not_exists(self):
        with self.assertRaises(exceptions.ConfigNotFound):
            config.load('/tmp/{}'.format(uuid.uuid4().hex))

    def test_wrong_format(self):
        with self.assertRaises(exceptions.ConfigHasWrongFormat):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write('broken json'.encode('utf-8'))
                f.close()

                config.load(f.name)

    def test_success(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(json.dumps(config.DEFAULT_CONFIG).encode('utf-8'))
            f.close()

            self.assertEqual(config.load(f.name), config.DEFAULT_CONFIG)

    def test_check_on_load(self):
        with self.assertRaises(exceptions.ConfigError):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(b'{}')
                f.close()

                config.load(f.name)


class TestCheck(unittest.TestCase):

    def check_load(self, data):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(json.dumps(data).encode('utf-8'))
            f.close()

            config.load(f.name)

    def test_no_rules_order(self):
        data = copy.deepcopy(config.DEFAULT_CONFIG)
        del data['rules_order']

        with self.assertRaises(exceptions.ConfigHasWrongFormat):
            self.check_load(data)

    def test_no_rules(self):
        data = copy.deepcopy(config.DEFAULT_CONFIG)
        del data['rules']

        with self.assertRaises(exceptions.ConfigHasWrongFormat):
            self.check_load(data)

    def test_no_rule_config(self):
        data = copy.deepcopy(config.DEFAULT_CONFIG)
        del data['rules']['rule_stdlib']

        with self.assertRaises(exceptions.ConfigHasWrongFormat):
            self.check_load(data)

    def test_succesS(self):
        self.check_load(config.DEFAULT_CONFIG)

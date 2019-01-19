
import os
import json
import uuid
import pathlib
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

    def prepair_data(self, temp_directory,
                     parent_config=config.DEFAULT_CONFIG,
                     child_config=config.DEFAULT_CONFIG):
        path = os.path.join(temp_directory,
                            'dir_with_not_reached_config',
                            'dir_with_config',
                            'empty_dir',
                            'leaf_dir')
        os.makedirs(path)

        path_1 = os.path.join(temp_directory,
                              'dir_with_not_reached_config',
                              constants.CONFIG_FILE_NAME)

        with open(path_1, 'w') as f:
            data = parent_config.clone(path=path_1)
            f.write(json.dumps(data.serialize()))

        path_2 = os.path.join(temp_directory,
                              'dir_with_not_reached_config',
                              'dir_with_config',
                              constants.CONFIG_FILE_NAME)

        with open(path_2, 'w') as f:
            data = child_config.clone(path='#config.2')
            f.write(json.dumps(data.serialize()))

        return path

    def test_get(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            leaf_path = self.prepair_data(temp_directory)

            loaded_config = config.get(leaf_path)

            config_path = os.path.join(os.path.dirname(os.path.dirname(leaf_path)), constants.CONFIG_FILE_NAME)

            expected_config = config.DEFAULT_CONFIG.clone(path=config_path)

            self.assertEqual(expected_config, loaded_config)

        # test cache here, file already removed, but cached data still exists
        loaded_config = config.get(leaf_path)

        self.assertEqual(expected_config, loaded_config)

        self.assertEqual(config.CONFIGS_CACHE,
                         {leaf_path: expected_config,
                          os.path.dirname(leaf_path): expected_config,
                          os.path.dirname(os.path.dirname(leaf_path)): expected_config})

    def test_get__fill_missed_arguments(self):
        with tempfile.TemporaryDirectory() as temp_directory:

            child_config = config.DEFAULT_CONFIG.clone(rules=[])

            leaf_path = self.prepair_data(temp_directory, child_config=child_config)

            loaded_config = config.get(leaf_path)

            self.assertEqual(loaded_config.uid, loaded_config.path)
            self.assertEqual(loaded_config.path, loaded_config.path)

            self.assertTrue(os.path.isfile(loaded_config.path))

    def test_two_configs(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            leaf_path_1 = self.prepair_data(temp_directory)

            leaf_path_2 = leaf_path_1 + '2'
            os.makedirs(leaf_path_2)

            config_2_path = os.path.join(leaf_path_2, constants.CONFIG_FILE_NAME)

            with open(config_2_path, 'w') as f:
                expected_config_2 = config.DEFAULT_CONFIG.clone(path=config_2_path)
                f.write(json.dumps(expected_config_2.serialize()))

            loaded_config_1 = config.get(leaf_path_1)
            loaded_config_2 = config.get(leaf_path_2)

            config_1_path = os.path.join(os.path.dirname(os.path.dirname(leaf_path_1)), constants.CONFIG_FILE_NAME)

            expected_config_1 = config.DEFAULT_CONFIG.clone(path=config_1_path)

            expected_config_1.path = config_1_path
            expected_config_2.path = config_2_path

            self.assertEqual(expected_config_1, loaded_config_1)
            self.assertEqual(expected_config_2, loaded_config_2)

        self.assertEqual(config.CONFIGS_CACHE,
                         {leaf_path_2: expected_config_2,
                          leaf_path_1: expected_config_1,
                          os.path.dirname(leaf_path_1): expected_config_1,
                          os.path.dirname(os.path.dirname(leaf_path_1)): expected_config_1})

    def test_not_found_find(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            leaf_path = self.prepair_data(temp_directory)

            loaded_config = config.get(leaf_path, config_name='not_found.json')

            self.assertEqual(loaded_config, config.DEFAULT_CONFIG.clone(path=loaded_config.path))


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
            f.write(json.dumps(config.DEFAULT_CONFIG.serialize()).encode('utf-8'))
            f.close()

            self.assertEqual(config.load(f.name), config.DEFAULT_CONFIG.clone(path=f.name))

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

    def test_no_rules(self):
        data = config.DEFAULT_CONFIG.serialize()
        del data['rules']

        with self.assertRaises(exceptions.ConfigHasWrongFormat):
            self.check_load(data)

    def test_success(self):
        self.check_load(config.DEFAULT_CONFIG.serialize())


class TestExpandCacheDirPath(unittest.TestCase):

    def test_none(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = config.expand_cache_dir_path(config_path=f.name, cache_dir=None)
            self.assertEqual(path, None)

    def test_homedir(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = config.expand_cache_dir_path(config_path=f.name, cache_dir='~/1/2/3')
            self.assertEqual(path, str(pathlib.Path.home() / '1/2/3'))

    def test_absolute(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = config.expand_cache_dir_path(config_path=f.name, cache_dir='/1/2/3')
            self.assertEqual(path, '/1/2/3')

    def test_relative(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            path = config.expand_cache_dir_path(config_path=f.name, cache_dir='./1/2/3')
            self.assertEqual(path, str(pathlib.Path(f.name).parent / './1/2/3'))

            path = config.expand_cache_dir_path(config_path=f.name, cache_dir='1/2/3')
            self.assertEqual(path, str(pathlib.Path(f.name).parent / '1/2/3'))

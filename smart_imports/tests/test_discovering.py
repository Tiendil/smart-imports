
import os
import uuid
import tempfile
import unittest

from .. import discovering
from .. import constants as c
from .. import exceptions as e


class TestFindConfigFile(unittest.TestCase):

    def prepair_data(self, temp_directory):
        path = os.path.join(temp_directory,
                            'dir_with_not_reached_config',
                            'dir_with_config',
                            'empty_dir',
                            'leaf_dir')
        os.makedirs(path)

        with open(os.path.join(temp_directory,
                               'dir_with_not_reached_config',
                               c.CONFIG_FILE_NAME), 'w') as f:
            f.write('1')

        with open(os.path.join(temp_directory,
                               'dir_with_not_reached_config',
                               'dir_with_config',
                               c.CONFIG_FILE_NAME), 'w') as f:
            f.write('2')

        return path


    def test_find(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            leaf_path = self.prepair_data(temp_directory)

            path = discovering.find_config_file(leaf_path)

            self.assertEqual(path,
                             os.path.join(temp_directory,
                                          'dir_with_not_reached_config',
                                          'dir_with_config',
                                          c.CONFIG_FILE_NAME))

    def test_not_found_find(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            leaf_path = self.prepair_data(temp_directory)

            path = discovering.find_config_file(leaf_path, config_name='not_found.json')

            self.assertEqual(path, None)


class TestLoadConfig(unittest.TestCase):

    def test_not_exists(self):
        with self.assertRaises(e.ConfigNotFound):
            discovering.load_config('/tmp/{}'.format(uuid.uuid4().hex))

    def test_wrong_format(self):
        with self.assertRaises(e.ConfigHasWrongFormat):
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write('broken json'.encode('utf-8'))
                f.close()

                discovering.load_config(f.name)

    def test_success(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write('{"a": "b"}'.encode('utf-8'))
            f.close()

            self.assertEqual(discovering.load_config(f.name), {'a': 'b'})


class TestDetermineFullModuleName(unittest.TestCase):

    def prepair_data(self, temp_directory):
        path = os.path.join(temp_directory,
                            'not_package',
                            'top_package',
                            'mid_package',
                            'leaf_package')
        os.makedirs(path)

        with open(os.path.join(temp_directory,
                               'not_package',
                               'top_package',
                               '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(temp_directory,
                               'not_package',
                               'top_package',
                               'mid_package',
                               '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(temp_directory,
                               'not_package',
                               'top_package',
                               'mid_package',
                               'leaf_package',
                               '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(temp_directory,
                               'not_package',
                               'top_package',
                               'mid_package',
                               'leaf_package',
                               'code.py'), 'w') as f:
            f.write(' ')

        return path

    def test_not_directory(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            self.prepair_data(temp_directory)
            module_name = discovering.determine_full_module_name(os.path.join(temp_directory,
                                                                              'not_package',
                                                                              'top_package',
                                                                              'mid_package',
                                                                              'leaf_package',
                                                                              'code.py'))
        self.assertEqual(module_name, 'top_package.mid_package.leaf_package.code')

    def test_directory(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            self.prepair_data(temp_directory)
            module_name = discovering.determine_full_module_name(os.path.join(temp_directory,
                                                                              'not_package',
                                                                              'top_package',
                                                                              'mid_package'))
        self.assertEqual(module_name, 'top_package.mid_package')

    def test_separators(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            self.prepair_data(temp_directory)
            path = os.path.join(temp_directory,
                                'not_package',
                                'top_package',
                                'mid_package')
            module_name = discovering.determine_full_module_name('///' + path +'///')
        self.assertEqual(module_name, 'top_package.mid_package')

    def test_top_package(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            self.prepair_data(temp_directory)
            module_name = discovering.determine_full_module_name(os.path.join(temp_directory,
                                                                              'not_package',
                                                                              'top_package'))
        self.assertEqual(module_name, 'top_package')


class TestDeterminePackagePath(unittest.TestCase):

    def test_is_directory(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            path = os.path.join(temp_directory, 'x', 'y')
            os.makedirs(path)

            self.assertEqual(discovering.determine_package_path(path),
                             path)

    def test_not_file_and_not_directory(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            path = os.path.join(temp_directory, 'x', 'y')

            self.assertEqual(discovering.determine_package_path(path),
                             None)

    def test_init_py(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            path = os.path.join(temp_directory, 'x', 'y')

            os.makedirs(path)

            with open(os.path.join(path,'__init__.py'), 'w') as f:
                f.write(' ')

            self.assertEqual(discovering.determine_package_path(os.path.join(path,'__init__.py')),
                             path)

    def test_not_init_py(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            path = os.path.join(temp_directory, 'x', 'y')

            os.makedirs(path)

            with open(os.path.join(path,'code.py'), 'w') as f:
                f.write(' ')

            self.assertEqual(discovering.determine_package_path(os.path.join(path,'code.py')),
                             None)

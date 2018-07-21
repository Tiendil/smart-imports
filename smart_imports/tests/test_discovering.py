
import os
import tempfile
import unittest

from .. import discovering


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

    def test_py(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            path = os.path.join(temp_directory, 'x', 'y')

            os.makedirs(path)

            with open(os.path.join(path,'code.py'), 'w') as f:
                f.write(' ')

            self.assertEqual(discovering.determine_package_path(os.path.join(path,'code.py')),
                             path)

    def test_not_py(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            path = os.path.join(temp_directory, 'x', 'y')

            os.makedirs(path)

            with open(os.path.join(path,'code.xx'), 'w') as f:
                f.write(' ')

            self.assertEqual(discovering.determine_package_path(os.path.join(path,'code.xx')),
                             None)


class TestHasSubmodule(unittest.TestCase):

    def test_package(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            path = os.path.join(temp_directory, 'x', 'y')
            os.makedirs(path)

            with open(os.path.join(path, '__init__.py'), 'w') as f:
                f.write(' ')

            self.assertTrue(discovering.has_submodule(os.path.join(temp_directory, 'x'), 'y'))

    def test_module(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            path = os.path.join(temp_directory, 'x', 'y')
            os.makedirs(path)

            with open(os.path.join(path, 'z.py'), 'w') as f:
                f.write(' ')

            self.assertTrue(discovering.has_submodule(path, 'z'))

    def test_no_submodule(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            path = os.path.join(temp_directory, 'x', 'y')
            os.makedirs(path)

            self.assertFalse(discovering.has_submodule(path, 'z'))

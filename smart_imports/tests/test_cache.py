
import os
import uuid
import unittest
import tempfile
import warnings

from unittest import mock

from .. import cache


class TestGetChecksum(unittest.TestCase):

    def test_not_intersect(self):
        sums = set()

        for i in range(1000):
            sums.add(cache.get_checksum(uuid.uuid4().hex))

        self.assertEqual(len(sums), 1000)


class TestGetCachePath(unittest.TestCase):

    def test(self):
        self.assertEqual(cache.get_cache_path(cache_dir='/tmp/cache_dir',
                                              module_name='my.super.module'),
                         '/tmp/cache_dir/my.super.module.cache')


class TestGetSet(unittest.TestCase):

    def test_not_cached(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            variables = cache.get(cache_dir=temp_directory,
                                  module_name='x.y',
                                  checksum=cache.get_checksum('abc'))
            self.assertEqual(variables, None)

    def test_set_get(self):
        variables = ['a', 'x', 'zzz', 'long_long_long']

        with tempfile.TemporaryDirectory() as temp_directory:
            cache.set(cache_dir=temp_directory,
                      module_name='x.y',
                      checksum=cache.get_checksum('abc'),
                      variables=variables)

            self.assertTrue(os.path.isfile(os.path.join(temp_directory, 'x.y.cache')))

            loaded_variables = cache.get(cache_dir=temp_directory,
                                         module_name='x.y',
                                         checksum=cache.get_checksum('abc'))

            self.assertEqual(variables, loaded_variables)

    def test_set_get__create_directories(self):
        variables = ['a', 'x', 'zzz', 'long_long_long']

        with tempfile.TemporaryDirectory() as temp_directory:
            cache_dir = os.path.join(temp_directory, 'unexisted_1', 'unexisted_2')

            cache.set(cache_dir=cache_dir,
                      module_name='x.y',
                      checksum=cache.get_checksum('abc'),
                      variables=variables)

            self.assertTrue(os.path.isdir(cache_dir))

            self.assertTrue(os.path.isfile(os.path.join(cache_dir, 'x.y.cache')))

            loaded_variables = cache.get(cache_dir=cache_dir,
                                         module_name='x.y',
                                         checksum=cache.get_checksum('abc'))

            self.assertEqual(variables, loaded_variables)

    def test_set_get__ignore_errors(self):
        variables = ['a', 'x', 'zzz', 'long_long_long']

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            cache.set(cache_dir=None,
                      module_name='x.y',
                      checksum=cache.get_checksum('abc'),
                      variables=variables)

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert cache.WARNING_MESSAGE in str(w[-1].message)

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            loaded_variables = cache.get(cache_dir=None,
                                         module_name='x.y',
                                         checksum=cache.get_checksum('abc'))

            assert len(w) == 1
            assert issubclass(w[-1].category, UserWarning)
            assert cache.WARNING_MESSAGE in str(w[-1].message)

            self.assertEqual(loaded_variables, None)


    def test_wrong_checksum(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            cache.set(cache_dir=temp_directory,
                      module_name='x.y',
                      checksum=cache.get_checksum('abc'),
                      variables=['x'])

            loaded_variables = cache.get(cache_dir=temp_directory,
                                         module_name='x.y',
                                         checksum=cache.get_checksum('abcd'))

            self.assertEqual(loaded_variables, None)

    def test_wrong_protocol_version(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            cache.set(cache_dir=temp_directory,
                      module_name='x.y',
                      checksum=cache.get_checksum('abc'),
                      variables=['x'])

            loaded_variables = cache.get(cache_dir=temp_directory,
                                         module_name='x.y',
                                         checksum=cache.get_checksum('abc'))

            self.assertEqual(loaded_variables, ['x'])

            with mock.patch('smart_imports.constants.CACHE_PROTOCOL_VERSION', uuid.uuid4().hex):
                loaded_variables = cache.get(cache_dir=temp_directory,
                                             module_name='x.y',
                                             checksum=cache.get_checksum('abc'))

            self.assertEqual(loaded_variables, None)

    def test_no_variables(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            cache.set(cache_dir=temp_directory,
                      module_name='x.y',
                      checksum=cache.get_checksum('abc'),
                      variables=[])

            self.assertTrue(os.path.isfile(os.path.join(temp_directory, 'x.y.cache')))

            loaded_variables = cache.get(cache_dir=temp_directory,
                                         module_name='x.y',
                                         checksum=cache.get_checksum('abc'))

            self.assertEqual(loaded_variables, [])


class TestCache(unittest.TestCase):

    def test_no_cache_dir(self):
        module_cache = cache.Cache(cache_dir=None,
                                   module_name='x.y',
                                   source='abc')

        variables = module_cache.get()

        self.assertEqual(variables, None)

    def test_has_cache_dir(self):
        variables = ['x', 'long_long']

        with tempfile.TemporaryDirectory() as temp_directory:
            module_cache = cache.Cache(cache_dir=temp_directory,
                                       module_name='x.y',
                                       source='abc')

            module_cache.set(variables=variables)

            self.assertTrue(os.path.isfile(os.path.join(temp_directory, 'x.y.cache')))

            loaded_variables = module_cache.get()

        self.assertTrue(loaded_variables, variables)

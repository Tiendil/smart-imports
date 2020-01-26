
import os
import unittest

from .. import helpers
from .. import discovering


class TestFindSpec(unittest.TestCase):

    def prepair_modules(self, base_directory):
        os.makedirs(os.path.join(base_directory, 'a', 'b', 'c'))
        os.makedirs(os.path.join(base_directory, 'a', 'b', 'd'))

        with open(os.path.join(base_directory, 'a', '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'x.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'b', '__init__.py'), 'w') as f:
            f.write(' ')

        with open(os.path.join(base_directory, 'a', 'b', 'y.py'), 'w') as f:
            f.write(' ')

    def test_no_spec(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            spec = discovering.find_spec('a.c')

            self.assertEqual(spec, None)
            self.assertEqual(discovering.SPEC_CACHE, {'a.c': None})

    def test_spec_found(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            spec = discovering.find_spec('a.b')

            self.assertEqual(spec.name, 'a.b')
            self.assertEqual(discovering.SPEC_CACHE, {'a.b': spec})

    def test_spec_from_cache(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            spec_1 = discovering.find_spec('a.b')
            spec_2 = discovering.find_spec('a.b')

            self.assertEqual(spec_1.name, 'a.b')
            self.assertEqual(discovering.SPEC_CACHE, {'a.b': spec_1})

            self.assertTrue(spec_1 is spec_2)

    def test_multiple_modules(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            spec_1 = discovering.find_spec('a.b')
            spec_2 = discovering.find_spec('a.x')

            self.assertEqual(spec_1.name, 'a.b')
            self.assertEqual(spec_2.name, 'a.x')
            self.assertEqual(discovering.SPEC_CACHE, {'a.b': spec_1,
                                                      'a.x': spec_2})

    def test_fake_namespace_package(self):
        with helpers.test_directory() as temp_directory:
            self.prepair_modules(temp_directory)

            self.assertEqual(discovering.find_spec('a.d'), None)

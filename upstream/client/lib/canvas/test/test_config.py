#
# TESTS
#

import os
import time
from unittest import TestCase

from canvas.config import Config


class ConfigTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        while os.path.isfile('/tmp/nofile'):
            os.remove('/tmp/nofile')
            time.sleep(0.1)

    def test_config_empty(self):
        c1 = Config(path='/tmp/nofile')

        self.assertEqual(c1.sections(), [])

    def test_config_get_section_is_none(self):
        c1 = Config(path='/tmp/nofile')

        self.assertEqual(c1.get(None, 'anything'), None)

    def test_config_get_section_not_found(self):
        c1 = Config(path='/tmp/nofile')
        self.assertEqual(c1.get('bar', 'foo'), None)

    def test_config_set_section_is_none(self):
        c1 = Config(path='/tmp/nofile')

        with self.assertRaises(KeyError):
            c1.set(None, None, None)

        with self.assertRaises(TypeError):
            c1.set('', None, None)

    def test_config_set_key_is_none(self):
        c1 = Config(path='/tmp/nofile')

        with self.assertRaises(TypeError):
            c1.set('Empty', None, None)

        with self.assertRaises(TypeError):
            c1.set('Empty', '', None)

    def test_config_set_value_is_none(self):
        c1 = Config(path='/tmp/nofile')

        with self.assertRaises(TypeError):
            c1.set('Empty', 'bar', None)

    def test_config_set(self):
        c1 = Config(path='/tmp/nofile')

        c1.set('foo', 'bar', 'baz')
        c1.set('foo', 'baz', '1')
        c1.set('bar', 'foo', 'baz')

        self.assertEqual(c1.get('foo', 'bar'), 'baz')
        self.assertEqual(c1.get('foo', 'baz'), '1')
        self.assertEqual(c1.get('bar', 'foo'), 'baz')

    def test_config_get_key_is_none(self):
        c1 = Config(path='/tmp/nofile')

        c1.set('foo', 'bar', 'baz')

        self.assertEqual(c1.get('foo', None), None)
        self.assertEqual(c1.get('foo', ''), None)

    def test_config_get_key_not_found(self):
        c1 = Config(path='/tmp/nofile')

        c1.set('foo', 'bar', 'baz')

        self.assertEqual(c1.get('foo', 'baz'), None)

    def test_config_sections(self):
        c1 = Config(path='/tmp/nofile')

        self.assertEqual(c1.sections(), [])

        c1.set('foo', 'bar', 'baz')
        c1.set('foo', 'baz', '1')
        c1.set('bar', 'foo', 'baz')

        self.assertEqual(c1.sections(), ['foo', 'bar'])

    def test_config_save_load(self):
        c1 = Config(path='/tmp/nofile')

        c1.set('foo', 'bar', 'baz')
        c1.set('foo', 'baz', '1')
        c1.set('bar', 'foo', 'baz')

        c1.save()

        self.assertEqual(os.path.isfile('/tmp/nofile'), True)

        c2 = Config(path='/tmp/nofile')

        self.assertEqual(c2.sections(), ['foo', 'bar'])
        self.assertEqual(c2.get('foo', 'bar'), 'baz')
        self.assertEqual(c2.get('foo', 'baz'), '1')
        self.assertEqual(c2.get('bar', 'foo'), 'baz')

    def test_config_unset_section_is_none(self):
        c1 = Config(path='/tmp/nofile')

        value = c1.unset(None, 'bar')
        self.assertEqual(value, False)

        value = c1.unset('', 'bar')
        self.assertEqual(value, False)

    def test_config_unset_key_is_none(self):
        c1 = Config(path='/tmp/nofile')

        c1.set('foo', 'bar', 'baz')

        value = c1.unset('foo', None)
        self.assertEqual(value, False)

        value = c1.unset('foo', '')
        self.assertEqual(value, False)

    def test_config_unset_section_not_found(self):
        c1 = Config(path='/tmp/nofile')

        value = c1.unset('foo', 'bar')
        self.assertEqual(value, False)

    def test_config_unset_key_not_found(self):
        c1 = Config(path='/tmp/nofile')

        c1.set('foo', 'bar', 'baz')

        value = c1.unset('foo', 'rab')
        self.assertEqual(value, False)

    def test_config_unset_key(self):
        c1 = Config(path='/tmp/nofile')
        c1.set('foo', 'bar', 'baz')

        # Check that we get True if key unset
        value = c1.unset('foo', 'bar')
        self.assertEqual(value, True)

        self.assertEqual(c1.get('foo', 'bar'), None)

if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(ConfigTestCase)
    unittest.TextTestRunner().run(suite)

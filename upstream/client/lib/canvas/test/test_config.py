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

    def test_config_entries(self):
        c1 = Config(path='/tmp/nofile')

        c1.set('foo', 'bar', 'baz')
        c1.set('foo', 'baz', '1')
        c1.set('bar', 'foo', 'baz')

        self.assertEqual(c1.sections(), ['foo', 'bar'])
        self.assertEqual(c1.get('foo', 'bar'), 'baz')
        self.assertEqual(c1.get('foo', 'baz'), '1')
        self.assertEqual(c1.get('bar', 'foo'), 'baz')

    def test_config_missing_key(self):
        c1 = Config(path='/tmp/nofile')
        self.assertEqual(c1.get('bar', 'foo'), None)

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

    def test_config_unset_key(self):
        c1 = Config(path='/tmp/nofile')
        c1.set('foo', 'bar', 'baz')

        self.assertEqual(c1.get('foo', 'bar'), 'baz')

        # Check that we get True if key unset
        value = c1.unset('foo', 'bar')
        self.assertEqual(value, True)

        self.assertEqual(c1.get('foo', 'bar'), None)

        # Check that we get False if section does not exist
        value = c1.unset('barry', 'bar')
        self.assertEqual(value, False)




if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(ConfigTestCase)
    unittest.TextTestRunner().run(suite)


#
# TESTS
#

from unittest import TestCase

from canvas.config import Config


class ConfigTestCase(TestCase):
    def setUp(self):
        pass

    def test_empty(self):
        c1 = Config(path='/tmp/nofile')

        self.assertEqual(c1.sections(), [])

    def test_entries(self):
        c1 = Config(path='/tmp/nofile')

        c1.set('foo', 'bar', 'baz')
        c1.set('foo', 'baz', '1')
        c1.set('bar', 'foo', 'baz')

        self.assertEqual(c1.sections(), ['foo', 'bar'])
        self.assertEqual(c1.get('foo', 'bar'), 'baz')
        self.assertEqual(c1.get('foo', 'baz'), '1')
        self.assertEqual(c1.get('bar', 'foo'), 'baz')



if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(RepoTestCase)
    unittest.TextTestRunner().run(suite)


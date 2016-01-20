
#
# TESTS
#

from unittest import TestCase

from canvas.package import Repository, RepoSet

class RepoTestCase(TestCase):

  def setUp(self):
    pass

  def test_repo_empty(self):
    r1 = Repository({})

    self.assertEqual(None, r1.name)
    self.assertEqual(None, r1.stub)
    self.assertEqual(None, r1.baseurl)
    self.assertEqual(None, r1.mirrorlist)
    self.assertEqual(None, r1.metalink)
    self.assertEqual(None, r1.enabled)
    self.assertEqual(None, r1.gpgkey)
    self.assertEqual(None, r1.gpgcheck)
    self.assertEqual(None, r1.cost)
    self.assertEqual(None, r1.exclude)
    self.assertEqual(None, r1.priority)
    self.assertEqual(None, r1.meta_expired)

  def test_repo_equality(self):
    r1 = Repository({'n': 'foo'})
    r2 = Repository({'n': 'foo', 's': 'foo'})
    r3 = Repository({'n': 'bar', 's': 'foo'})
    r4 = Repository({'n': 'bar', 's': 'foo1'})
    r5 = Repository({'n': 'baz', 's': 'foo1'})

    # stub is the equality check
    self.assertNotEqual(r1, r2)
    self.assertEqual(r2, r3)
    self.assertNotEqual(r3, r4)
    self.assertEqual(r4, r5)


if __name__ == "__main__":
  import unittest
  suite = unittest.TestLoader().loadTestsFromTestCase(PackageTestCase)
  unittest.TextTestRunner().run(suite)

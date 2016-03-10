#
# TESTS
#

from unittest import TestCase

from canvas.package import Package, PackageSet

class PackageTestCase(TestCase):

    def setUp(self):
        pass

    def test_package_empty(self):
        p1 = Package({})

        self.assertEqual(None, p1.name)
        self.assertEqual(None, p1.epoch)
        self.assertEqual(None, p1.version)
        self.assertEqual(None, p1.release)
        self.assertEqual(None, p1.arch)

        # empty packages will have a default action of include
        self.assertEqual({'z': 1}, p1.to_object())

    def test_package_equality(self):
        p1 = Package({})
        p2 = Package({'n': 'foo'})
        p3 = Package({'n': 'foo', 'a': 'x86_64'})
        p4 = Package({'n': 'foo', 'a': 'x86_64', 'v': '1.0'})
        p5 = Package({'n': 'foo', 'a': 'i386'})

        self.assertNotEqual(p1, p2)
        self.assertEqual(p1.action, Package.ACTION_INCLUDE)
        self.assertEqual(p2, p3)
        self.assertEqual(p2, p4)
        self.assertNotEqual(p3, p5)

    def test_package_group(self):
        p1 = Package({})
        p2 = Package({'n': '@foo'})

        self.assertNotEqual(p1.action, Package.ACTION_INCLUDE | Package.ACTION_GROUP)
        self.assertEqual(p2.action, Package.ACTION_INCLUDE | Package.ACTION_GROUP)

    def test_packageset_equality(self):
        p1 = Package({'n': 'foo'})
        p2 = Package({'n': 'foo', 'a': 'x'})
        p3 = Package({'n': 'foo', 'a': 'y'})

        l1 = PackageSet()
        l2 = PackageSet()

        # p1 has a no arch defined is loosely equal to an explict arch being
        # defined for the same name
        l1.add(p1)
        l2.add(p2)
        self.assertEqual(l1, l2)

        # p3 has an explicit arch which will overwrite the undefined arch for the
        # package of the same name, result in the two lists each having an explicit
        # defined arch which are not equal
        l1.add(p3)
        self.assertNotEqual(l1, l2)

    def test_packageset_update(self):
        p1 = Package({'n': 'foo'})
        p2 = Package({'n': 'foo', 'a': 'x'})
        p3 = Package({'n': 'foo', 'a': 'y'})

        l1 = PackageSet()
        l2 = PackageSet()

        l1.add(p2)
        l1.add(p3)

        self.assertEqual(PackageSet([p2, p3]), l1)

        l2.add(p1)
        self.assertEqual(PackageSet([p1]), l2)

        l2.update(l1)
        self.assertEqual(PackageSet([p2, p3]), l2)

    def test_packageset_uniqueness(self):
        p1 = Package({'n': 'foo'})
        p2 = Package({'n': 'foo', 'a': 'x'})
        p3 = Package({'n': 'foo', 'a': 'y'})

        l1 = PackageSet()

        l1.add(p1)
        self.assertTrue(len(l1) == 1)

        # adding second package of same name with arch defined should overwrite
        # existing package with undefined arch
        l1.add(p2)
        self.assertTrue(len(l1) == 1)
        self.assertEqual(l1[0].arch, 'x')

        l1.add(p3)
        self.assertTrue(len(l1) == 2)

    def test_packageset_difference(self):
        p1 = Package({'n': 'foo'})
        p2 = Package({'n': 'foo', 'a': 'x'})

        p3 = Package({'n': 'bar'})
        p4 = Package({'n': 'bar', 'a': 'y'})

        p5 = Package({'n': 'baz'})
        p6 = Package({'n': 'car'})

        l1 = PackageSet([p1, p3, p5])
        l2 = PackageSet([p2, p4, p6])

        (luniq1, luniq2) = l1.difference(l2)

        self.assertEqual(PackageSet([p5]), luniq1)
        self.assertEqual(PackageSet([p6]), luniq2)


if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(PackageTestCase)
    unittest.TextTestRunner().run(suite)

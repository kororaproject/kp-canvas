
#
# TESTS
#

from unittest import TestCase

from canvas.package import Package, PackageSet, ErrorInvalidPackage


class PackageTestCase(TestCase):

    def setUp(self):
        pass

    def test_package_parse_empty(self):
        p1 = Package({})

        self.assertEqual(None, p1.name)
        self.assertEqual(None, p1.epoch)
        self.assertEqual(None, p1.version)
        self.assertEqual(None, p1.release)
        self.assertEqual(None, p1.arch)

        # empty packages will have a default action of include
        self.assertEqual({'z': 1}, p1.to_object())

    # https://fedoraproject.org/wiki/Packaging:NamingGuidelines
    # [a-zA-Z0-9-._+]
    def test_package_parse_str_valid_name(self):

        # Hyphen is acceptable
        try:
            Package("abc-xyz")
        except ErrorInvalidPackage:
            self.fail("Package raised ErrorInvalidPackage on valid package name")

        # Numbers are acceptable
        try:
            Package("foobar3")
        except ErrorInvalidPackage:
            self.fail("Package raised ErrorInvalidPackage on valid package name")

        try:
            Package("lemon3.3")
        except ErrorInvalidPackage:
            self.fail("Package raised ErrorInvalidPackage on valid package name")

        # Underscore is acceptable
        try:
            Package("foo_bar")
        except ErrorInvalidPackage:
            self.fail("Package raised ErrorInvalidPackage on valid package name")

        # Plus is acceptable
        try:
            Package("pie++")
        except ErrorInvalidPackage:
            self.fail("Package raised ErrorInvalidPackage on valid package name")

        # Groups are acceptable
        try:
            Package("@Development Tools")
        except ErrorInvalidPackage:
            self.fail("Package raised ErrorInvalidPackage on valid package name")

# TODO:
#  def test_package_parse_str_invalid_name(self):


    def test_package_parse_str_valid_version(self):
        # Standard format
        try:
            Package("bar@1-2")
        except ErrorInvalidPackage:
            self.fail("Package raised ErrorInvalidPackage on valid package version")

        # Point releases are acceptable
        try:
            Package("bar@1.3-2")
        except ErrorInvalidPackage:
            self.fail("Package raised ErrorInvalidPackage on valid package version")

        # Large version numbers
        try:
            p = Package("bar@1234-2")
        except ErrorInvalidPackage:
            self.fail("Package raised ErrorInvalidPackage on valid package version")

    def test_package_parse_str_invalid_version(self):
        # Release is required
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar@1")

        with self.assertRaises(ErrorInvalidPackage):
            Package("bar@1-")

        # Must have version, release is not enough
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar@-2")

        # Multiple release specifiers
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar@1.2-3-2")

    def test_package_parse_str_valid_arch(self):
        # Standard format
        try:
            p = Package("bar:i386")
        except ErrorInvalidPackage:
            self.fail("Package raised ErrorInvalidPackage on valid arch")

    def test_package_parse_str_invalid_arch(self):
        # Must have arch string
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar:")


    def test_package_parse_str_valid_epoc(self):
        # Standard format
        try:
            p = Package("bar#1@1.2-3")
        except ErrorInvalidPackage:
            self.fail("Package raised ErrorInvalidPackage on valid epoc")

        # Multiple digits are acceptable
        try:
            p = Package("bar#13@1.2-3")
        except ErrorInvalidPackage:
            self.fail("Package raised ErrorInvalidPackage on valid epoc")


    def test_package_parse_str_invalid_epoc(self):
        # Must have version/release
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar#1")

        # Must have version/release
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar#@1.2-4")

        # Adding arch, we still need version and release
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar#1:i586")

        # Must be numeric
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar#a@1.2-4")

        # Must be integer
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar#1.1@1.2-3")



    def test_package_parse_str_invalid_format(self):
        # Dangling separators
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar#@1.2-3")
        # Dangling epoc sign
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar#@")

        # Cannot have version without release
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar@2.3.4")
        # Epoc requires version to be specified
        with self.assertRaises(ErrorInvalidPackage):
            Package("bar#1")

    def test_package_parse_str(self):

        p1 = Package("foo")
        p2 = Package("~foo:x86_64")
        p3 = Package("bar@2.1.4-0")
        p4 = Package("baz#1@2.1-3:x86_64")

        self.assertEqual("foo", p1.name)
        self.assertEqual(Package.ACTION_INCLUDE, p1.action)
        self.assertEqual(None, p1.epoch)
        self.assertEqual(None, p1.version)
        self.assertEqual(None, p1.release)
        self.assertEqual(None, p1.arch)

        self.assertEqual("foo", p2.name)
        self.assertEqual(Package.ACTION_EXCLUDE, p2.action)
        self.assertEqual(None, p2.epoch)
        self.assertEqual(None, p2.version)
        self.assertEqual(None, p2.release)
        self.assertEqual("x86_64", p2.arch)

        self.assertEqual("bar", p3.name)
        self.assertEqual(Package.ACTION_INCLUDE, p3.action)
        self.assertEqual(None, p3.epoch)
        self.assertEqual("2.1.4", p3.version)
        self.assertEqual("0", p3.release)
        self.assertEqual(None, p3.arch)

        self.assertEqual("baz", p4.name)
        self.assertEqual(Package.ACTION_INCLUDE, p4.action)
        self.assertEqual("1", p4.epoch)
        self.assertEqual("2.1", p4.version)
        self.assertEqual("3", p4.release)
        self.assertEqual("x86_64", p4.arch)


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

# http://dnf.readthedocs.org/en/latest/command_ref.html#specifying-packages-label
# Release in this case includes the fc23
# Valid formats for pkg_spec:
#   name
#   name.arch
#   name-[epoc:]version-release.arch
#   name-[epoc:]version-release

# Not valid in canvas:
#   name-[epoc:]version

    def test_package_to_pkg_spec(self):
        p1 = Package('foo')
        p2 = Package('foo:x86_64')
        p3 = Package('foo@1.0-1:x86_64')
        p4 = Package('foo_bar@1.2.3-1')
        p5 = Package('the_silver_searcher#0@0.31.0-1:x86_64')

        # Basic "name"
        self.assertEqual(p1.to_pkg_spec(), "foo")

        # "name.arch"
        self.assertEqual(p2.to_pkg_spec(), "foo.x86_64")

        # "name-version-release.arch"
        self.assertRegexpMatches(p3.to_pkg_spec(), r'^foo-1.0-1.fc\d{2}.x86_64$')

        # "name-version-release"
        self.assertRegexpMatches(p4.to_pkg_spec(), r'^foo_bar-1.2.3-1.fc\d{2}$')

        # "name-epoc:version-release.arch"
        self.assertRegexpMatches(p5.to_pkg_spec(),
                                 r'^the_silver_searcher-0:0.31.0-1.fc\d{2}.x86_64$')


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

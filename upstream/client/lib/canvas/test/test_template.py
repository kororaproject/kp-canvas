
#
# TESTS
#

from unittest import TestCase

from canvas.template import Template, ErrorInvalidTemplate
from canvas.object import ObjectSet
from canvas.package import Package, PackageSet
from canvas.repository import RepoSet


class TemplateTestCase(TestCase):

    def setUp(self):
        pass

    def test_template_create_empty(self):
        t1 = Template({})

        self.assertEqual(None, t1.name)
        self.assertEqual(None, t1.user)
        self.assertEqual(None, t1.uuid)
        self.assertEqual(None, t1.description)

        self.assertEqual([], t1.includes)

        self.assertEqual([], t1._includes_resolved)
        self.assertEqual({}, t1._meta)

        self.assertEqual(RepoSet(), t1.repos)
        self.assertEqual(RepoSet(), t1._includes_repos)
        self.assertEqual(RepoSet(), t1._delta_repos)

        self.assertEqual(PackageSet(), t1._packages)
        self.assertEqual(PackageSet(), t1._includes_packages)
        self.assertEqual(PackageSet(), t1._delta_packages)

        self.assertEqual([], t1._stores)
        self.assertEqual(ObjectSet(), t1._objects)


    def test_template_parse_str_valid(self):
        t1 = Template("foo:bar")
        t2 = Template("foo:bar@baz")
        t3 = Template("foo:bar@")

        self.assertEqual("foo", t1.user)
        self.assertEqual("bar", t1.name)
        self.assertEqual(None, t1.version)
        self.assertEqual("foo:bar", t1.unv)

        self.assertEqual("foo", t2.user)
        self.assertEqual("bar", t2.name)
        self.assertEqual("baz", t2.version)
        self.assertEqual("foo:bar@baz", t2.unv)

        self.assertEqual("foo", t3.user)
        self.assertEqual("bar", t3.name)
        self.assertEqual(None, t3.version)
        self.assertEqual("foo:bar", t3.unv)

    def test_template_parse_str_invalid(self):

        # empty string
        with self.assertRaises(ErrorInvalidTemplate):
            Template("")

        # pure whitespace
        with self.assertRaises(ErrorInvalidTemplate):
            Template(" ")

        # no user
        with self.assertRaises(ErrorInvalidTemplate):
            Template("foo")

        with self.assertRaises(ErrorInvalidTemplate):
            Template(":foo@bar")

        # no user or version
        with self.assertRaises(ErrorInvalidTemplate):
            Template(":foo@")

        # no name
        with self.assertRaises(ErrorInvalidTemplate):
            Template("foo:")

#    def test_template_from_kickstart_invalid_path(self):
#        t1 = Template({})
#        t1.from_kickstart('')


    def test_template_add_includes_str(self):
        t1 = Template("foo:bar")

        t1.includes = 'foo'
        self.assertEqual(["foo:foo"], t1.includes)

        t1.includes = ['foo','bar@baz']
        self.assertEqual(["foo:foo", "foo:bar@baz"], t1.includes)

        t1.includes = 'foo,bar@baz,baz'
        self.assertEqual(["foo:foo", "foo:bar@baz", "foo:baz"], t1.includes)


    def test_template_add_includes_obj(self):
        t1 = Template("foo:bar")
        t2 = Template("bar:baz")
        t3 = Template("baz:daz")

        p1 = Package("foo")
        p2 = Package("bar")
        p3 = Package("baz")
        p4 = Package("~baz")

        t1.add_package(p1)

        t2.add_package(p2)
        t2.add_package(p3)

        t3.add_package(p4)

        # check includes
        t1.includes = [t2]
        self.assertEqual(["bar:baz"], t1.includes)

        # check includes (rebuild)
        t1.includes = [t2, t3]
        self.assertEqual(["bar:baz", "baz:daz"], t1.includes)

        # check package resolution
        t1.includes = [t2]
        self.assertEqual(PackageSet([p1, p2, p3]), t1.packages_all)

        # check package resolution (ordered)
        t1.includes = [t2, t3]
        self.assertEqual(PackageSet([p1, p2, p3]), t1.packages_all)

        t1.includes = [t3, t2]
        self.assertEqual(PackageSet([p1, p2, p4]), t1.packages_all)



if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TemplateTestCase)
    unittest.TextTestRunner().run(suite)

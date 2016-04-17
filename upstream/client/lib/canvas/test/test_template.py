
#
# TESTS
#

from unittest import TestCase

from canvas.template import Template, ErrorInvalidTemplate
from canvas.repository import RepoSet
from canvas.package import PackageSet


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
        self.assertEqual([], t1._objects)


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


    def test_template_add_includes(self):
        t1 = Template("foo:bar")

        t1.includes = 'foo'
        self.assertEqual(["foo:foo"], t1.includes)

        t1.includes = ['foo','bar@baz']
        self.assertEqual(["foo:foo", "foo:bar@baz"], t1.includes)

        t1.includes = 'foo,bar@baz,baz'
        self.assertEqual(["foo:foo", "foo:bar@baz", "foo:baz"], t1.includes)

if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TemplateTestCase)
    unittest.TextTestRunner().run(suite)

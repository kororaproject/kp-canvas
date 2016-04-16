
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
        templ1 = Template({})

        self.assertEqual(None, templ1.name)
        self.assertEqual(None, templ1.user)
        self.assertEqual(None, templ1.uuid)
        self.assertEqual(None, templ1.description)

        self.assertEqual([], templ1.includes)

        self.assertEqual([], templ1._includes_resolved)
        self.assertEqual({}, templ1._meta)

        self.assertEqual(RepoSet(), templ1.repos)
        self.assertEqual(RepoSet(), templ1._includes_repos)
        self.assertEqual(RepoSet(), templ1._delta_repos)

        self.assertEqual(PackageSet(), templ1._packages)
        self.assertEqual(PackageSet(), templ1._includes_packages)
        self.assertEqual(PackageSet(), templ1._delta_packages)

        self.assertEqual([], templ1._stores)
        self.assertEqual([], templ1._objects)


    def test_template_parse_str_valid(self):
        # valid
        templ1 = Template("foo")
        templ2 = Template("foo:bar")
        templ3 = Template("foo:bar@baz")
        templ4 = Template("foo:bar@")

        self.assertEqual(None, templ1.user)
        self.assertEqual("foo", templ1.name)
        self.assertEqual(None, templ1.version)

        self.assertEqual("foo", templ2.user)
        self.assertEqual("bar", templ2.name)
        self.assertEqual(None, templ2.version)

        self.assertEqual("foo", templ3.user)
        self.assertEqual("bar", templ3.name)
        self.assertEqual("baz", templ3.version)

        self.assertEqual("foo", templ4.user)
        self.assertEqual("bar", templ4.name)
        self.assertEqual(None, templ4.version)

    def test_template_parse_str_invalid(self):

        # Whitespace name
        with self.assertRaises(ErrorInvalidTemplate):
            Template(" ")

        # Empty name
        with self.assertRaises(ErrorInvalidTemplate):
            Template(":foo@bar")

        # Empty name and version
        with self.assertRaises(ErrorInvalidTemplate):
            Template(":foo@")

        # Empty string
        with self.assertRaises(ErrorInvalidTemplate):
            Template("")

        # Empty name
        with self.assertRaises(ErrorInvalidTemplate):
            Template("foo:")

#    def test_template_from_kickstart_invalid_path(self):
#        templ1 = Template({})
#        templ1.from_kickstart('')





if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TemplateTestCase)
    unittest.TextTestRunner().run(suite)

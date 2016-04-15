
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
        templ1 = Template("test1")
        templ2 = Template("tst:test1")

        self.assertEqual("test1", templ1.name)
        self.assertEqual(None, templ1.user)

        self.assertEqual("test1", templ2.name)
        self.assertEqual("tst", templ2.user)

    def test_template_parse_str_invalid(self):

        # Whitespace name
        with self.assertRaises(ErrorInvalidTemplate):
            Template(" ")

        # Empty string
        with self.assertRaises(ErrorInvalidTemplate):
            Template("")

        # Whitespace user
        with self.assertRaises(ErrorInvalidTemplate):
            Template(" :test1")

        # Missing user
        with self.assertRaises(ErrorInvalidTemplate):
            Template(":test1")

        # Missing name
        with self.assertRaises(ErrorInvalidTemplate):
            Template("tst:")

        # Trailing seperator
        with self.assertRaises(ErrorInvalidTemplate):
            Template("tst:test1:")

#    def test_template_from_kickstart_invalid_path(self):
#        templ1 = Template({})
#        templ1.from_kickstart('')





if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(TemplateTestCase)
    unittest.TextTestRunner().run(suite)


#
# TESTS
#

from unittest import TestCase

from canvas.machine import Machine, ErrorInvalidMachine
from canvas.repository import RepoSet
from canvas.package import PackageSet


class MachineTestCase(TestCase):

    def setUp(self):
        pass

    def test_machine_parse_str_valid(self):
        # valid
        m2 = Machine("foo:bar")
        m3 = Machine("foo:bar@baz")
        m4 = Machine("foo:bar@")

        self.assertEqual("foo", m2.user)
        self.assertEqual("bar", m2.name)
        self.assertEqual(None, m2.version)

        self.assertEqual("foo", m3.user)
        self.assertEqual("bar", m3.name)
        self.assertEqual("baz", m3.version)

        self.assertEqual("foo", m4.user)
        self.assertEqual("bar", m4.name)
        self.assertEqual(None, m4.version)

    def test_machine_parse_str_invalid(self):

        # empty string
        with self.assertRaises(ErrorInvalidMachine):
            Machine("")

        # pure whitespace
        with self.assertRaises(ErrorInvalidMachine):
            Machine(" ")

        # no user
        with self.assertRaises(ErrorInvalidMachine):
            Machine("foo")

        with self.assertRaises(ErrorInvalidMachine):
            Machine(":foo@bar")

        # no user or version
        with self.assertRaises(ErrorInvalidMachine):
            Machine(":foo@")

        # no name
        with self.assertRaises(ErrorInvalidMachine):
            Machine("foo:")


if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(MachineTestCase)
    unittest.TextTestRunner().run(suite)

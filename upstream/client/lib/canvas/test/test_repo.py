
#
# TESTS
#

from unittest import TestCase

from canvas.repository import Repository, RepoSet


class RepoTestCase(TestCase):

    def setUp(self):
        pass

    def test_repo_parse_empty(self):
        r1 = Repository({})

        self.assertEqual(None, r1.name)
        self.assertEqual(None, r1.stub)

        self.assertEqual(None, r1.baseurl)
        self.assertEqual(None, r1.mirrorlist)
        self.assertEqual(None, r1.metalink)

        self.assertEqual(None, r1.gpgkey)
        self.assertEqual(None, r1.enabled)
        self.assertEqual(None, r1.gpgcheck)
        self.assertEqual(None, r1.cost)
        self.assertEqual(False, r1.install)

        self.assertEqual(None, r1.exclude_packages)
        self.assertEqual(None, r1.include_packages)

        self.assertEqual(None, r1.priority)

        self.assertEqual(None, r1.meta_expired)

        self.assertEqual(r1.action, Repository.ACTION_INCLUDE)

    def test_repo_kwargs(self):
        pass

# https://github.com/rhinstaller/pykickstart/blob/master/docs/kickstart-docs.rst#repo
    def test_repo__parse_str_arg(self):
        # Double Quotes
        self.assertEqual(Repository._parse_str_arg('name="korora"', 'name='), 'korora')
        # No Quotes
        self.assertEqual(Repository._parse_str_arg('name=korora 23', 'name='), 'korora 23')
        # Single Quotes
        self.assertEqual(Repository._parse_str_arg("name='korora 23'", 'name='), 'korora 23')

    def test_repo_parse_str_name(self):
        r1 = Repository('repo --name="Korora 23 - i386 - Updates"')
        r2 = Repository('repo --baseurl=http://download1.rpmfusion.org/ --cost=1000')

        # Name set
        self.assertEqual('Korora 23 - i386 - Updates', r1.name)

        # Name unset
        self.assertEqual(None, r2.name)

    def test_repo_parse_str_baseurl(self):
        r1 = Repository('repo --baseurl="https://fakeurl"')
        r2 = Repository('repo --name="Korora 23 - i386 - Updates"')
        r3 = Repository('repo --baseurl="https://fakeurl,http://backupfakeurl"')

        # Set
        self.assertEqual(['https://fakeurl'], r1.baseurl)

        # Unset
        self.assertEqual(None, r2.baseurl)

        # List
        self.assertEqual(['https://fakeurl','http://backupfakeurl'], r3.baseurl)

    def test_repo_parse_str_mirrorlist(self):
        r1 = Repository('repo --mirrorlist="https://fakeurl"')
        r2 = Repository('repo --name="Korora 23 - i386 - Updates"')

        # Set
        self.assertEqual('https://fakeurl', r1.mirrorlist)

        # Unset
        self.assertEqual(None, r2.mirrorlist)

    def test_repo_parse_str_proxy(self):
        r1 = Repository('repo --proxy="https://fakeproxy"')
        r2 = Repository('repo --name="Korora 23 - i386 - Updates"')

        # Set
        self.assertEqual('https://fakeproxy', r1.proxy)

        # Unset
        self.assertEqual(None, r2.proxy)

    def test_repo_parse_str_ignoregroups(self):
        r1 = Repository('repo --name="Korora 23 - i386 - Updates" --ignoregroups=true')
        r2 = Repository('repo --name="Korora 23 - i386 - Updates" --ignoregroups')
        r3 = Repository('repo --name="Korora 23 - i386 - Updates"')

        # Set
        self.assertEqual(True, r1.ignoregroups)

        # fedora documentation implies that it must be --ignoregroups=true 
        self.assertEqual(False, r2.ignoregroups)

        # Unset
        self.assertEqual(False, r3.ignoregroups)


    def test_repo_parse_str_noverifyssl(self):
        r1 = Repository('repo --name="Korora 23 - i386 - Updates" --noverifyssl')
        r2 = Repository('repo --name="Korora 23 - i386 - Updates"')

        # Set
        self.assertEqual(True, r1.noverifyssl)

        # Unset
        self.assertEqual(False, r2.noverifyssl)

    def test_repo_parse_str_install(self):
        r1 = Repository('repo --name="Korora 23 - i386 - Updates" --install')
        r2 = Repository('repo --name="Korora 23 - i386 - Updates"')

        # Set
        self.assertEqual(True, r1.install)

        # Unset
        self.assertEqual(False, r2.install)


    def test_repo_parse_str_cost(self):
        r1 = Repository('repo --cost="1"')
        r2 = Repository('repo --name="Korora 23 - i386 - Updates"')

        # Double Quoted
        self.assertEqual('1', r1.cost)

        # Unset
        self.assertEqual(None, r2.cost)

    def test_repo_parse_str(self):
        # TODO: Full data population here in various orders r1 == r2
        # Attempting to see if name="Fedora--foo" breaks things
        pass

    def test_repo_equality(self):
        r1 = Repository({'s': 'foo'})
        r2 = Repository({'s': 'foo', 'bu': 'foo'})
        r3 = Repository({'s': 'bar', 'bu': 'foo'})
        r4 = Repository({'s': 'bar', 'bu': 'foo1'})
        r5 = Repository({'s': 'baz', 'bu': 'foo1'})

        # stub is the equality check
        self.assertEqual(r1, r2)
        self.assertNotEqual(r2, r3)
        self.assertEqual(r3, r4)
        self.assertNotEqual(r4, r5)

    def test_reposet_equality(self):
        r1 = Repository({'s': 'foo', 'bu': 'x'})
        r2 = Repository({'s': 'foo', 'bu': 'y'})

        l1 = RepoSet()
        l2 = RepoSet()

        l1.add(r1)
        l2.add(r2)
        self.assertEqual(l1, l2)

    def test_reposet_uniqueness(self):
        r1 = Repository({'s': 'foo', 'bu': 'x'})
        r2 = Repository({'s': 'foo', 'bu': 'y'})
        r3 = Repository({'s': 'bar', 'bu': 'x'})

        l1 = RepoSet()

        l1.add(r1)
        self.assertTrue(len(l1) == 1)

        l1.add(r2)
        self.assertTrue(len(l1) == 1)
        self.assertEqual(l1[0].baseurl, 'x')

        l1.add(r3)
        self.assertTrue(len(l1) == 2)

    def test_reposet_difference(self):
        r1 = Repository({'s': 'foo', 'bu': 'x'})
        r2 = Repository({'s': 'bar', 'bu': 'y'})
        r3 = Repository({'s': 'baz'})
        r4 = Repository({'s': 'car'})

        l1 = RepoSet([r1, r2, r3])
        l2 = RepoSet([r2, r3, r4])

        (luniq1, luniq2) = l1.difference(l2)

        self.assertEqual(RepoSet([r1]), luniq1)
        self.assertEqual(RepoSet([r4]), luniq2)


if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(RepoTestCase)
    unittest.TextTestRunner().run(suite)

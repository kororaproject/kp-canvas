
#
# TESTS
#

import dnf

from unittest import TestCase

from canvas.repository import Repository, RepoSet


class RepoTestCase(TestCase):

    def setUp(self):
        pass

    def test_repo_parse_empty(self):
        # Must match string, dnf repo, or dictionary
        with self.assertRaises(TypeError):
            Repository(1)

        r1 = Repository({'name':'testrepo'})

        self.assertEqual('testrepo', r1.name)
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

    # https://github.com/rhinstaller/pykickstart/blob/master/docs/kickstart-docs.rst#repo
    def test_package_parse_str_invalid(self):
        with self.assertRaises(TypeError):
            Repository.parse_str(1)


        with self.assertRaises(ValueError):
            Repository.parse_str('repo --mirrorlist=http://fakeurl --baseurl=http://alsofake')



    def test_package_parse_str_from_name(self):
        d1 = Repository.parse_str('validreponame')
        # Name set
        self.assertEqual('validreponame', d1['name'])

    def test_repo__parse_str_arg(self):
        # Double Quotes
        self.assertEqual(Repository._parse_str_arg('name="korora"', 'name='), 'korora')
        # No Quotes
        self.assertEqual(Repository._parse_str_arg('name=korora 23', 'name='), 'korora 23')
        # Single Quotes
        self.assertEqual(Repository._parse_str_arg("name='korora 23'", 'name='), 'korora 23')

    def test_repo_parse_str_name(self):
        r1 = Repository('repo --name="Korora 23 - i386 - Updates"')

        # Name set
        self.assertEqual('Korora 23 - i386 - Updates', r1.name)

    def test_repo_parse_str_baseurl(self):
        r1 = Repository('repo --name="Test" --baseurl="https://fakeurl"')
        r2 = Repository('repo --name="Korora 23 - i386 - Updates"')
        r3 = Repository('repo --name="Test" --baseurl="https://fakeurl,http://backupfakeurl"')

        # Set
        self.assertEqual(['https://fakeurl'], r1.baseurl)

        # Unset
        self.assertEqual(None, r2.baseurl)

        # List
        self.assertEqual(['https://fakeurl','http://backupfakeurl'], r3.baseurl)

    def test_repo_parse_str_mirrorlist(self):
        r1 = Repository('repo --name="Test" --mirrorlist="https://fakeurl"')
        r2 = Repository('repo --name="Korora 23 - i386 - Updates"')

        # Set
        self.assertEqual('https://fakeurl', r1.mirrorlist)

        # Unset
        self.assertEqual(None, r2.mirrorlist)

    def test_repo_parse_str_proxy(self):
        r1 = Repository('repo --name="Test" --proxy="https://fakeproxy"')
        r2 = Repository('repo --name="Korora 23 - i386 - Updates"')

        # Set
        self.assertEqual('https://fakeproxy', r1.proxy)

        # Unset
        self.assertEqual(None, r2.proxy)

    def test_repo_parse_str_ignoregroups(self):
        r1 = Repository('repo --name="Korora 23 - i386 - Updates" --ignoregroups=true')
        r3 = Repository('repo --name="Korora 23 - i386 - Updates"')

        # Set
        self.assertEqual(True, r1.ignoregroups)

        # fedora documentation implies that it must be --ignoregroups=true
        with self.assertRaises(ValueError):
            Repository('repo --name="Korora 23 - i386 - Updates" --ignoregroups')

        # Unset
        self.assertEqual(False, r3.ignoregroups)


    def test_repo_parse_str_excludepkgs(self):
        r1 = Repository('repo --name="Korora 23 - i386 - Updates" --excludepkgs=foo,bar,baz')
        r2 = Repository('repo --name="Korora 23 - i386 - Updates" --excludepkgs=foo')
        r3 = Repository('repo --name="Korora 23 - i386 - Updates" --excludepkgs=foo,')
        r4 = Repository('repo --name="Korora 23 - i386 - Updates"')

        # Set
        self.assertEqual(['foo','bar','baz'], r1.exclude_packages)

        # Single
        self.assertEqual(['foo'], r2.exclude_packages)

        # Hanging seperator
        self.assertEqual(['foo'], r3.exclude_packages)

        # Unset
        self.assertEqual(None, r4.exclude_packages)


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
        r1 = Repository('repo --name="Test" --cost="1"')
        r2 = Repository('repo --name="Korora 23 - i386 - Updates"')

        # Double Quoted
        self.assertEqual('1', r1.cost)

        # Unset
        self.assertEqual(None, r2.cost)

    def test_repo_parse_str_tilda(self):
        r1 = Repository('~repo --name="Korora 23 - i386 - Updates"')

        # Ensure that stub is parsed out of exclude format
        self.assertEqual('korora-23-i386-updates', r1.stub)

        # Repo is Excluded
        self.assertEqual(r1.action, Repository.ACTION_EXCLUDE)

    def test_repo_parse_str(self):
        # TODO: Full data population here in various orders r1 == r2
        # Attempting to see if name="Fedora--foo" breaks things
        pass

    def test_repo_parse_dnf_invalid(self):
        with self.assertRaises(TypeError):
            Repository.parse_dnf("notvalid")

    # String representation is the dnf pkg_spec format
    def test_repo___str__(self):
        r1 = Repository('repo --name="Korora 23 - i386 - Updates" --ignoregroups=true')
        self.assertEqual(str(r1), 'Repository: repo --name="Korora 23 - i386 - Updates" --ignoregroups=true')

    # Representation format is to_json format
    def test_repo___repr__(self):
        r1 = Repository('repo --name="Korora 23 - i386 - Updates" --ignoregroups=true')
        self.assertEqual(repr(r1),
                         'Repository: {"e":true,"i":false,"n":"Korora 23 - i386 - Updates","s":"korora-23-i386-updates","z":1}')


    def test_repo_equality(self):
        r1 = Repository({'n':'test', 's': 'foo'})
        r2 = Repository({'n':'test', 's': 'foo', 'bu': 'foo'})
        r3 = Repository({'n':'test', 's': 'bar', 'bu': 'foo'})
        r4 = Repository({'n':'test', 's': 'bar', 'bu': 'foo1'})
        r5 = Repository({'n':'test', 's': 'baz', 'bu': 'foo1'})

        # stub is the equality check
        self.assertEqual(r1, r2)
        self.assertNotEqual(r2, r3)
        self.assertEqual(r3, r4)
        self.assertNotEqual(r4, r5)
        self.assertNotEqual(r4, 'str')

    def test_repo_to_kickstart(self):
        repo_str_1 = 'repo --name=fedora --baseurl=http://fedoraproject.org/ --install'
        repo_str_2 = 'repo --name=fedora2 --mirrorlist=http://mirrors.fedoraproject.org/metalink?repo=fedora-$releasever&arch=$basearch'
        # TODO: Metalink cannot be specified in string mode

        repo_str_3 = 'repo --name=fedora3 --cost=1337 --excludepkgs=1'
        repo_str_4 = 'repo --name=fedora3 --excludepkgs=python,perl --proxy=http://fakeproxy:1337'

        repo_str_5 = 'repo --name=fedora3 --includepkgs=python --ignoregroups=true'
        repo_str_6 = 'repo --name=fedora3 --includepkgs=python,ruby --noverifyssl'

        repo1 = Repository(repo_str_1)
        repo2 = Repository(repo_str_2)
        repo3 = Repository(repo_str_3)
        repo4 = Repository(repo_str_4)
        repo5 = Repository(repo_str_5)
        repo6 = Repository(repo_str_6)

        ks1 = repo1.to_kickstart()
        ks2 = repo2.to_kickstart()
        ks3 = repo3.to_kickstart()
        ks4 = repo4.to_kickstart()
        ks5 = repo5.to_kickstart()
        ks6 = repo6.to_kickstart()

        # baseurl and install
        self.assertEqual(repo_str_1, ks1)
        # mirrorlist
        self.assertEqual(repo_str_2, ks2)

        # cost and exclude one package
        self.assertEqual(repo_str_3, ks3)
        # proxy and exclude multiple packages
        self.assertEqual(repo_str_4, ks4)

        # ignoregroups and include one package
        self.assertEqual(repo_str_5, ks5)
        # noverifyssl and include multiple packages
        self.assertEqual(repo_str_6, ks6)

    def test_reposet_equality(self):
        r1 = Repository({'n':'test', 's': 'foo', 'bu': 'x'})
        r2 = Repository({'n':'test', 's': 'foo', 'bu': 'y'})

        l1 = RepoSet()
        l2 = RepoSet()

        l1.add(r1)
        l2.add(r2)
        self.assertEqual(l1, l2)

    def test_reposet_uniqueness(self):
        r1 = Repository({'n':'test', 's': 'foo', 'bu': 'x'})
        r2 = Repository({'n':'test', 's': 'foo', 'bu': 'y'})
        r3 = Repository({'n':'test', 's': 'bar', 'bu': 'x'})

        l1 = RepoSet()

        l1.add(r1)
        self.assertTrue(len(l1) == 1)

        l1.add(r2)
        self.assertTrue(len(l1) == 1)
        self.assertEqual(l1[0].baseurl, 'x')

        l1.add(r3)
        self.assertTrue(len(l1) == 2)

    def test_reposet_difference(self):
        r1 = Repository({'n':'test', 's': 'foo', 'bu': 'x'})
        r2 = Repository({'n':'test', 's': 'bar', 'bu': 'y'})
        r3 = Repository({'n':'test', 's': 'baz'})
        r4 = Repository({'n':'test', 's': 'car'})

        l1 = RepoSet([r1, r2, r3])
        l2 = RepoSet([r2, r3, r4])

        (luniq1, luniq2) = l1.difference(l2)

        self.assertEqual(RepoSet([r1]), luniq1)
        self.assertEqual(RepoSet([r4]), luniq2)


if __name__ == "__main__":
    import unittest
    suite = unittest.TestLoader().loadTestsFromTestCase(RepoTestCase)
    unittest.TextTestRunner().run(suite)

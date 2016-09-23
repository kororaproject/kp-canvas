#
# Copyright (C) 2013-2016   Ian Firns   <firnsy@kororaproject.org>
#                           Chris Smart <csmart@kororaproject.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import dnf
import json

from canvas.set import CanvasSet

class Repository(object):
    """ A Canvas object that represents a Repository of packages. """

    # CONSTANTS
    ACTION_EXCLUDE          = 0x02
    ACTION_INCLUDE          = 0x01

    def __init__(self, repository):

        if isinstance(repository, str):
            repository = Repository.parse_str(repository)
        elif isinstance(repository, dnf.repo.Repo):
            repository = Repository.parse_dnf(repository)
        if not isinstance(repository, dict):
            raise TypeError("Repository must be a dict")

        self.name     = repository.get('name', repository.get('n', None))
        self.stub     = repository.get('stub', repository.get('s', None))

        self.baseurl    = repository.get('baseurl', repository.get('bu', None))
        self.mirrorlist = repository.get('mirrorlist', repository.get('ml', None))
        self.metalink   = repository.get('metalink', repository.get('ma', None))

        self.gpgkey     = repository.get('gpgkey', repository.get('gk', None))
        self.enabled    = repository.get('enabled', repository.get('e', None))
        self.gpgcheck   = repository.get('gpgcheck', repository.get('gc', None))
        self.cost       = repository.get('cost', repository.get('c', None))
        self.install    = repository.get('install', repository.get('i', False))

        self.ignoregroups = repository.get('ignoregroups', False)
        self.proxy        = repository.get('proxy', None)
        self.noverifyssl  = repository.get('noverifyssl', False)

        self.exclude_packages = repository.get('exclude_packages', repository.get('xp', None))
        self.include_packages = repository.get('include_packages', repository.get('ip', None))

        self.priority   = repository.get('priority', None)

        self.meta_expired = repository.get('meta_expired', repository.get('me', None))

        self.action   = repository.get('action', repository.get('z', self.ACTION_INCLUDE))

        if not self.name:
            raise ValueError("Name cannot be None")

    def __eq__(self, other):
        if isinstance(other, Repository):
            return (self.stub == other.stub)
        else:
            return False

    def __hash__(self):
        return hash(self.stub)

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __repr__(self):
        return 'Repository: %s' % (self.to_json())

    def __str__(self):
        return 'Repository: %s' % (self.to_kickstart())


    @staticmethod
    def _parse_str_arg(data, name):
        return data.replace(name, '').replace('"', '').replace("'", '').strip()

    @staticmethod
    def _format_string(string):
        """ Add double quotes to string if it contains at least one space """
        if ' ' in string:
            string = '"{}"'.format(string)

        return string

    @classmethod
    def parse_str(cls, repository):
        """ Generate a repo dictionary from a kickstart formated repository string.

        Note: Kickstart documentation can be found here:
            https://github.com/rhinstaller/pykickstart/blob/master/docs/kickstart-docs.rst#repo

        Args:
            cls: Holds the Repository class
            repository: A string representation of a repository in kickstart format

        Returns:
            The dictionary conversion of the repository string

        Raises:
            TypeError: If repository is not a string
            ValueError: If string does not match the kickstart format

        """

        if not isinstance(repository, str):
            raise TypeError("Repository must be a string")

        repository.strip()

        repo = {
            'enabled': True,
            'action': cls.ACTION_INCLUDE
        }

        # TODO: Do we need to support this here?
        if repository.startswith('~repo '):
            repository = repository[1:]
            repo['action'] = cls.ACTION_EXCLUDE

        if not repository.startswith('repo '):
            raise ValueError("Repository must start with '[~]repo '")

        for arg in repository.split("--"):
            if arg == 'repo' or arg == '' or arg == 'repo ':
                continue

            elif arg.startswith('name='):
                name = cls._parse_str_arg(arg, 'name=')

                repo['name'] = name
                repo['stub'] = name.replace(' ', '-').replace('---', '-').lower()

            elif arg.startswith('baseurl='):
                baseurl = cls._parse_str_arg(arg, 'baseurl=')
                repo['baseurl'] = list (filter(None, baseurl.split(',')))

            elif arg.startswith('mirrorlist='):

                # Not actually a comma-separated list just a url to a list
                repo['mirrorlist'] = cls._parse_str_arg(arg, 'mirrorlist=')

            elif arg.startswith('cost='):
                repo['cost'] = cls._parse_str_arg(arg, 'cost=')

            elif arg.startswith('excludepkgs='):
                exclude_packages = cls._parse_str_arg(arg, 'excludepkgs=').split(',')
                repo['exclude_packages'] = list (filter(None, exclude_packages))

            elif arg.startswith('includepkgs='):
                include_packages = cls._parse_str_arg(arg, 'includepkgs=').split(',')
                repo['include_packages'] = list (filter(None, include_packages))

            elif arg.startswith('proxy='):
                repo['proxy'] = cls._parse_str_arg(arg, 'proxy=')

            elif arg.startswith('ignoregroups=true'):
                repo['ignoregroups'] = True

            elif arg.startswith('noverifyssl'):
                repo['noverifyssl'] = True

            elif arg.startswith('install'):
                repo['install'] = True

            else:
                raise ValueError("Unsupported option '{}' in kickstart repo".format(arg))

        if 'baseurl' in repo and 'mirrorlist' in repo:
            raise ValueError("Kickstart format cannot have both baseurl and mirrorlist")

        return repo

    @classmethod
    def parse_dnf(cls, repository):

        if not isinstance(repository, dnf.repo.Repo):
            raise TypeError("Repository must be a dnf.repo.Repo")

        return {
            'name': repository.name,
            'stub': repository.id,

            'baseurl': repository.baseurl,
            'mirrorlist': repository.mirrorlist,
            'metalink': repository.metalink,

            'gpgkey': repository.gpgkey,
            'enabled': repository.enabled,
            'gpgcheck': repository.gpgcheck,
            'cost': repository.cost,
            'priority': repository.priority,

            'exclude_packages': repository.exclude,
            'include_packages': repository.include,
            # 'meta_expired': repository.meta_expired,

            'action': cls.ACTION_INCLUDE,
        }

    def to_kickstart(self):
        """ Generate a repo dictionary from a kickstart formated repository string.

        Note: Kickstart documentation can be found here:
            https://github.com/rhinstaller/pykickstart/blob/master/docs/kickstart-docs.rst#repo

        Args:
            cls: Holds the Repository class
            repository: A string representation of a repository in kickstart format
        Returns:
            The dictionary conversion of the repository string
        Raises:
            TypeError: If repository is not a string
            ValueError: If string does not match the kickstart format

        """

        repo = 'repo --name={0}'.format(Repository._format_string(self.name))
        url  = 'url '

        if self.baseurl is not None:
            repo += ' --baseurl={0}'.format(self.baseurl[0])
            url  += ' --url="{0}"'.format(self.baseurl[0])

        elif self.mirrorlist is not None:
            repo += ' --mirrorlist={0}'.format(self.mirrorlist)
            url  += ' --mirrorlist="{0}"'.format(self.mirrorlist)

        elif self.metalink is not None:
            repo += ' --mirrorlist={0}'.format(self.metalink)

        if self.cost is not None:
            repo += ' --cost={0}'.format(self.cost)

        if self.exclude_packages is not None:
            repo += ' --excludepkgs={0}'.format(','.join(self.exclude_packages))

        if self.include_packages is not None:
            repo += ' --includepkgs={0}'.format(','.join(self.include_packages))

        if self.proxy:
            repo += ' --proxy={0}'.format(self.proxy)
            url  += ' --proxy={0}'.format(self.proxy)

        if self.ignoregroups:
            repo += ' --ignoregroups=true'

        if self.noverifyssl:
            repo += ' --noverifyssl'
            url  += ' --noverifyssl'

        if self.install:
            repo += ' --install'

        return repo # + "\n" + url

    def to_json(self):
        return json.dumps(self.to_object(), separators=(',', ':'), sort_keys=True)

    def to_object(self):
        o = {
            's':  self.stub,
            'n':  self.name,
            'bu': self.baseurl,
            'ml': self.mirrorlist,
            'ma': self.metalink,
            'e':  self.enabled,
            'gc': self.gpgcheck,
            'gk': self.gpgkey,
            'me': self.meta_expired,
            'c':  self.cost,
            'p':  self.priority,
            'i':  self.install,
            'xp': self.exclude_packages,
            'ip': self.include_packages,
            'z':  self.action,
        }

        # only build with non-None values
        return {k: v for k, v in o.items() if v != None}

    def to_repo(self, cache_dir=None):
        if cache_dir is None:
            cli_cache = dnf.conf.CliCache('/var/tmp')
            cache_dir = cli_cache.cachedir

        r = dnf.repo.Repo('canvas_{0}'.format(self.stub), cache_dir)

        if self.name is not None:
            r.name = self.name

        if self.baseurl is not None:
            r.baseurl = self.baseurl

        if self.mirrorlist is not None:
            r.mirrorlist = self.mirrorlist

        if self.metalink is not None:
            r.metalink = self.metalink

        if self.gpgcheck is not None:
            r.gpgcheck = self.gpgcheck

        if self.gpgkey is not None:
            r.gpgkey = self.gpgkey

        if self.cost is not None:
            r.cost = self.cost

        if self.exclude_packages is not None:
            r.exclude = self.exclude_packages

        if self.include_packages is not None:
            r.include = self.include_packages

        if self.meta_expired is not None:
            r.meta_expired = self.meta_expired

        if self.enabled is not None and not self.enabled:
            r.disable()

        return r


class RepoSet(CanvasSet):
    def __init__(self, initvalue=()):
        CanvasSet.__init__(self, initvalue)

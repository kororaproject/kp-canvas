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

    def __init__(self, repository, template=None):

        if isinstance(repository, str):
            repository = Repository.parse_str(repository, template=template)

        elif isinstance(repository, dnf.repo.Repo):
            repository = Repository.parse_dnf(repository, template=template)

        if not isinstance(repository, dict):
            raise TypeError("Repository must be a dict")

        self._name     = repository.get('name', repository.get('n', None))
        self._stub     = repository.get('stub', repository.get('s', None))

        self._baseurl    = repository.get('baseurl', repository.get('bu', None))
        self._mirrorlist = repository.get('mirrorlist', repository.get('ml', None))
        self._metalink   = repository.get('metalink', repository.get('ma', None))

        self._gpgkey     = repository.get('gpgkey', repository.get('gk', None))
        self._enabled    = repository.get('enabled', repository.get('e', None))
        self._gpgcheck   = repository.get('gpgcheck', repository.get('gc', None))
        self._cost       = repository.get('cost', repository.get('c', None))
        self._install    = repository.get('install', repository.get('i', False))

        self._ignoregroups = repository.get('ignoregroups', False)
        self._proxy        = repository.get('proxy', None)
        self._noverifyssl  = repository.get('noverifyssl', False)

        self._exclude_packages = repository.get('exclude_packages', repository.get('xp', None))
        self._include_packages = repository.get('include_packages', repository.get('ip', None))

        self._priority   = repository.get('priority', None)

        self._meta_expired = repository.get('meta_expired', repository.get('me', None))

        self._template = repository.get('template', repository.get('t', template))

        self._action   = repository.get('action', repository.get('z', self.ACTION_INCLUDE))

        if not self._name:
            raise ValueError("Name cannot be None")

    def __eq__(self, other):
        if isinstance(other, Repository):
            return (self._stub == other.stub)
        else:
            return False

    def __hash__(self):
        return hash(self._stub)

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
    def parse_str(cls, repository, template=None):
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
            'action': cls.ACTION_INCLUDE,

            'template': template
        }

        # TODO: Do we need to support this here?
        if repository.startswith('~repo '):
            repository = repository[1:]
            repo['action'] = cls.ACTION_EXCLUDE

        if not repository.startswith('repo '):
            repo['name'] = repository
            repo['stub'] = repository.replace(' ', '-').replace('---', '-').lower()
            return repo

        for arg in repository.split("--"):
            if arg == 'repo' or arg == '' or arg == 'repo ':
                continue

            elif arg.startswith('name='):
                name = cls._parse_str_arg(arg, 'name=')

                repo['name'] = name
                repo['stub'] = name.replace(' ', '-').replace('---', '-').lower()

            elif arg.startswith('baseurl='):
                baseurl = cls._parse_str_arg(arg, 'baseurl=')
                repo['baseurl'] = list(filter(None, baseurl.split(',')))

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
    def parse_dnf(cls, repository, template=None):

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

            'template': template
        }

    #
    # PROPERTIES
    @property
    def action(self):
        return self._action

    @property
    def baseurl(self):
        return self._baseurl

    @baseurl.setter
    def baseurl(self, value):
        self._baseurl = value

    @property
    def cost(self):
        return self._cost

    @cost.setter
    def cost(self, value):
        self._cost= value

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, value):
        self._enabled = bool(value)

    @property
    def exclude_packages(self):
        return self._exclude_packages

    @property
    def gpgcheck(self):
        return self._gpgcheck

    @property
    def gpgkey(self):
        return self._gpgkey

    @property
    def ignoregroups(self):
        return self._ignoregroups

    @property
    def include_packages(self):
        return self._include_packages

    @property
    def install(self):
        return self._install

    @property
    def metalink(self):
        return self._metalink

    @metalink.setter
    def metalink(self, value):
        self._metalink = value

    @property
    def meta_expired(self):
        return self._meta_expired

    @property
    def mirrorlist(self):
        return self._mirrorlist

    @mirrorlist.setter
    def mirrorlist(self, value):
        self._mirrorlist = value

    @property
    def name(self):
        return self._name

    @property
    def noverifyssl(self):
        return self._noverifyssl

    @property
    def proxy(self):
        return self._proxy

    @property
    def priority(self):
        return self._priority

    @property
    def stub(self):
        return self._stub

    @property
    def template(self):
        return self._template

    #
    # PUBLIC METHODS
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

        repo = 'repo --name={0}'.format(Repository._format_string(self._name))
        url  = 'url '

        if self._baseurl is not None:
            repo += ' --baseurl={0}'.format(self._baseurl[0])
            url  += ' --url="{0}"'.format(self._baseurl[0])

        elif self._mirrorlist is not None:
            repo += ' --mirrorlist={0}'.format(self._mirrorlist)
            url  += ' --mirrorlist="{0}"'.format(self._mirrorlist)

        elif self._metalink is not None:
            repo += ' --mirrorlist={0}'.format(self._metalink)

        if self._cost is not None:
            repo += ' --cost={0}'.format(self._cost)

        if self._exclude_packages is not None:
            repo += ' --excludepkgs={0}'.format(','.join(self._exclude_packages))

        if self._include_packages is not None:
            repo += ' --includepkgs={0}'.format(','.join(self._include_packages))

        if self._proxy:
            repo += ' --proxy={0}'.format(self._proxy)
            url  += ' --proxy={0}'.format(self._proxy)

        if self._ignoregroups:
            repo += ' --ignoregroups=true'

        if self._noverifyssl:
            repo += ' --noverifyssl'
            url  += ' --noverifyssl'

        if self._install:
            repo += ' --install'

        return repo # + "\n" + url

    def to_json(self):
        return json.dumps(self.to_object(), separators=(',', ':'), sort_keys=True)

    def to_object(self):
        o = {
            's':  self._stub,
            'n':  self._name,
            'bu': self._baseurl,
            'ml': self._mirrorlist,
            'ma': self._metalink,
            'e':  self._enabled,
            'gc': self._gpgcheck,
            'gk': self._gpgkey,
            'me': self._meta_expired,
            'c':  self._cost,
            'p':  self._priority,
            'i':  self._install,
            'xp': self._exclude_packages,
            'ip': self._include_packages,
            'z':  self._action,
        }

        # only build with non-None values
        return {k: v for k, v in o.items() if v != None}

    def to_repo(self, conf=None):
        if conf is None:
            db = dnf.Base()
            conf = db.conf
            conf.cachedir = '/var/tmp'

        def _varSub(option, subs=conf.substitutions):
            for (k, v) in subs.items():
                option = option.replace('${0}'.format(k), v)

            return option

        r = dnf.repo.Repo('canvas-{0}'.format(self._stub), conf.cachedir)

        if self._name is not None:
            r.name = self._name

        if self._baseurl is not None:
            r.baseurl = [_varSub(u) for u in self._baseurl]

        if self._mirrorlist is not None:
            r.mirrorlist = _varSub(self._mirrorlist)

        if self._metalink is not None:
            r.metalink = _varSub(self._metalink)

        if self._gpgcheck is not None:
            r.gpgcheck = self._gpgcheck

        if self._gpgkey is not None:
            r.gpgkey = self._gpgkey

        if self._cost is not None:
            r.cost = self._cost

        if self._exclude_packages is not None:
            r.exclude = self._exclude_packages

        if self._include_packages is not None:
            r.include = self._include_packages

        if self._meta_expired is not None:
            r.meta_expired = self._meta_expired

        if self._enabled is not None and not self._enabled:
            r.disable()

        return r


class RepoSet(CanvasSet):
    def __init__(self, initvalue=()):
        CanvasSet.__init__(self, initvalue)

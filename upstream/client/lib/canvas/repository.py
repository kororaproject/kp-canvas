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

import collections
import dnf
import json


class Repository(object):
    """ A Canvas object that represents a Repository of packages. """

    # CONSTANTS
    ACTION_EXCLUDE          = 0x02
    ACTION_INCLUDE          = 0x01

    def __init__(self, *args, **kwargs):
        self.name     = kwargs.get('name', None)
        self.stub     = kwargs.get('stub', None)

        self.baseurl    = kwargs.get('baseurl', None)
        self.mirrorlist = kwargs.get('mirrorlist', None)
        self.metalink   = kwargs.get('metalink', None)

        self.gpgkey     = kwargs.get('gpgkey', None)
        self.enabled    = kwargs.get('enabled', None)
        self.gpgcheck   = kwargs.get('gpgcheck', None)
        self.cost       = kwargs.get('cost', None)
        self.install    = kwargs.get('install', None)

        self.exclude_packages = kwargs.get('exclude_packages', None)
        self.include_packages = kwargs.get('include_packages', None)

        self.priority   = kwargs.get('priority', None)

        self.meta_expired = kwargs.get('meta_expired', None)

        self.action   = kwargs.get('action', self.ACTION_INCLUDE)

        # parse all args package defined objects
        for arg in args:
            self.parse(arg)

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
        return 'Repository: %s ' % (self.to_json())

    def __str__(self):
        return 'Repository: %s ' % (self.to_kickstart())

    def parse(self, data):
        if isinstance(data, str):
            # check are we a kickstart formatted repo
            data.strip()

            if data.startswith('repo '):
                for a in data.split():
                    if a == 'repo' or a == '':
                        continue

                    elif a.startswith('--name='):
                        self.stub = a[7:].strip('"')

                    elif a.startswith('--baseurl='):
                        self.baseurl = a[10:]

                    elif a.startswith('--mirrorlist='):
                        self.mirrorlist = a[13:]

                self.action = self.ACTION_INCLUDE

            else:
                if data.startswith('~'):
                    self.stub = data[1:]
                    self.action = self.ACTION_EXCLUDE

                else:
                    self.stub = data
                    self.action = self.ACTION_INCLUDE

        elif isinstance(data, dnf.repo.Repo):
            self.name     = data.name
            self.stub     = data.id

            self.baseurl    = data.baseurl
            self.mirrorlist = data.mirrorlist
            self.metalink   = data.metalink

            self.gpgkey     = data.gpgkey
            self.enabled    = data.enabled
            self.gpgcheck   = data.gpgcheck
            self.cost       = data.cost
            self.priority   = data.priority

            self.exclude_packages = data.exclude
            self.include_packages = data.include
#        self.meta_expired = data.meta_expired

            self.action     = self.ACTION_INCLUDE

        elif isinstance(data, dict):
            self.name     = data.get('n', self.name)
            self.stub     = data.get('s', self.stub)

            self.baseurl    = data.get('bu', self.baseurl)
            self.mirrorlist = data.get('ml', self.mirrorlist)
            self.metalink   = data.get('ma', self.metalink)

            self.gpgkey     = data.get('gk', self.gpgkey)
            self.enabled    = data.get('e', self.enabled)
            self.gpgcheck   = data.get('gc', self.gpgcheck)
            self.cost       = data.get('c', self.cost)
            self.priority   = data.get('p', self.priority)
            self.install    = data.get('i', self.install)

            self.exclude_packages = data.get('xp', self.exclude_packages)
            self.include_packages = data.get('ip', self.include_packages)

            self.meta_expired = data.get('me', self.meta_expired)

            self.action  = data.get('z', self.ACTION_INCLUDE)

    def to_kickstart(self):
        r = 'repo'

        if self.name is not None:
            r += ' --name="{0}"'.format(self.name)

        if self.baseurl is not None and len(self.baseurl):
            r += ' --baseurl={0}'.format(self.baseurl)

        elif self.mirrorlist is not None:
            r += ' --mirrorlist={0}'.format(self.mirrorlist)

        elif self.metalink is not None:
            r += ' --mirrorlist={0}'.format(self.metalink)

        if self.cost is not None:
            r += ' --cost={0}'.format(self.cost)

        if self.exclude_packages is not None:
            r += ' --exclude_packages={0}'.format(self.exclude_packages.join(','))

        if self.include_packages is not None:
            r += ' --exclude_packages={0}'.format(self.include_packages.join(','))

        if self.install is not None:
            r += ' --install'

        return r

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
            if len(self.metalink):
                r.metalink = self.metalink[0]

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


class RepoSet(collections.MutableSet):
    def __init__(self, initvalue=()):
        self._set = []

        for x in initvalue:
            self.add(x)

    def __contains__(self, item):
        return item in self._set

    def __getitem__(self, index):
        return self._set[index]

    def __iter__(self):
        return iter(self._set)

    def __len__(self):
        return len(self._set)

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, self._set)

    def add(self, item):
        if not isinstance(item, Repository):
            raise TypeError('Not a Repository.')

        if item not in self._set:
            self._set.append(item)

    def discard(self, item):
        if not isinstance(item, Repository):
            raise TypeError('Not a Repository.')

        try:
            self._set.remove(item)

        except:
            pass

    def difference(self, other):
        if not isinstance(other, RepoSet):
            raise TypeError('Not a RepoSet.')

        uniq_self = RepoSet()
        uniq_other = RepoSet()

        # find unique items to self
        for x in self._set:
            if x not in other:
                uniq_self.add(x)

        # find unique items to other
        for x in other:
            if x not in self._set:
                uniq_other.add(x)

        return (uniq_self, uniq_other)

    def union(self, *args):
        if len(args) == 0:
            raise Exception('No RepoSets defined for union.')

        u = RepoSet(self._set)

        for o in args:
            if not isinstance(o, RepoSet):
                raise TypeError('Not a RepoSet.')

            # add takes care of uniqueness so let's use it
            for x in o:
                u.add(x)

        return u

    def update(self, *args):
        for o in args:
            if not isinstance(o, RepoSet):
                raise TypeError('Not a RepoSet.')

            # add takes care of uniqueness so let's use it
            for x in o:
                self.add(x)

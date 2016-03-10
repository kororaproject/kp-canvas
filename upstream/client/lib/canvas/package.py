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
import hawkey
import json
import re


RE_PACKAGE = re.compile("([+~])?([^#@:\s]+)(?:(?:#(\d+))?@([^-]+)-([^:]))?(?::(\w+))?")

class ErrorInvalidPackage(Exception):
  def __init__(self, reason, code=0):
    self.reason = reason.lower()
    self.code = code

  def __repr__(self):
    return str(self)

  def __str__(self):
    return 'error: {0}'.format(str(self.reason))

#
# CLASS DEFINITIONS / IMPLEMENTATIONS
#


class Package(object):
    """ A Canvas object that represents an installable Package. """

    # CONSTANTS
    ACTION_PIN              = 0x80
    ACTION_GROUP_OPTIONAL   = 0x40
    ACTION_GROUP_NODEFAULTS = 0x20
    ACTION_GROUP            = 0x10
    ACTION_EXCLUDE          = 0x02
    ACTION_INCLUDE          = 0x01

    def __init__(self, *args, **kwargs):
        self.name     = kwargs.get('name', None)
        self.epoch    = kwargs.get('epoch', None)
        self.version  = kwargs.get('version', None)
        self.release  = kwargs.get('release', None)
        self.arch     = kwargs.get('arch', None)
        self.action   = kwargs.get('action', self.ACTION_INCLUDE)

        # parse all args package defined objects
        for arg in args:
            self.parse(arg)

        # strip evr information as appropriate
        if not kwargs.get('evr', True):
            self.epoch = None
            self.version = None
            self.release = None

    def __eq__(self, other):
        if isinstance(other, Package):
            if (self.arch is None) or (other.arch is None):
                return (self.name == other.name)
            else:
                return (self.name == other.name) and (self.arch == other.arch)

        else:
            return False

    def __hash__(self):
        # package uniqueness is based on name and arch
        # this allows packages with different archs to be
        # specified in a template
        if self.arch is None:
            return hash(self.name)

        return hash('{0}.{1}'.format(self.name, self.arch))

    def __ne__(self, other):
        return (not self.__eq__(other))

    def __repr__(self):
        return 'Package: %s' % (self.to_pkg_spec())

    def __str__(self):
        return 'Package: %s' % (json.dumps(self.to_object(), separators=(',', ':')))

    def excluded(self):
        return self.action & (self.ACTION_EXCLUDE)

    def included(self):
        return self.action & (self.ACTION_INCLUDE)

    def parse(self, data):
        if isinstance(data, dnf.package.Package) or \
                isinstance(data, hawkey.Package):
            self.name    = data.name
            self.epoch   = data.epoch
            self.version = data.version
            self.release = data.release
            self.arch    = data.arch

        elif isinstance(data, dict):
            self.name    = data.get('n', self.name)
            self.epoch   = data.get('e', self.epoch)
            self.version = data.get('v', self.version)
            self.release = data.get('r', self.release)
            self.arch    = data.get('a', self.arch)
            self.action  = data.get('z', self.ACTION_INCLUDE)

        elif isinstance(data, str):
            m = RE_PACKAGE.match(data)

            if m is not None:
                if m.group(1) == '~':
                    self.action = self.ACTION_EXCLUDE

                else:
                    self.action = self.ACTION_INCLUDE

                self.name    = m.group(2)
                self.epoch   = m.group(3)
                self.version = m.group(4)
                self.release = m.group(5)
                self.arch    = m.group(6)

        # detect group packages
        if isinstance(self.name, str) and self.name.startswith('@'):
            self.action |= self.ACTION_GROUP

    def pinned(self):
        return self.action & (self.ACTION_PIN)

    def to_json(self):
        return json.dumps(self.to_object(), separators=(',', ':'))

    def to_object(self):
        o = {
            'n': self.name,
            'e': self.epoch,
            'v': self.version,
            'r': self.release,
            'a': self.arch,
            'z': self.action,
        }

        # only build with non-None values
        return {k: v for k, v in o.items() if v != None}

    def to_pkg_spec(self):
        # return empty string if no name (should never happen)
        if self.name is None:
            return ''

        f = self.name

        # calculate evr
        evr = None

        if self.epoch is not None:
            evr = self.epoch + ':'

        if self.version is not None and self.release is not None:
            evr += '{0}-{1}'.format(self.version, self.release)
        elif self.version is not None:
            evr += self.version

        # append evr if appropriate
        if evr is not None:
            f += evr

        # append arch if appropriate
        if self.arch is not None:
            f += '.' + self.arch

        return f

    def to_pkg(self, db=None):
        if not isinstance(db, dnf.Base):
            db = dnf.Base()
            try:
                db.fill_sack()

            except OSError as e:
                pass

        p_list = db.sack.query().installed().filter(name=self.name)

        return list(p_list)[0]


class PackageSet(collections.MutableSet):
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
        if not isinstance(item, Package):
            raise TypeError('Not a Package.')

        if item not in self._set:
            self._set.append(item)

        # add if new package has more explicit arch definition than existing
        elif item.arch is not None:
            for i, x in enumerate(self._set):
                if x.name == item.name and x.arch is None:
                    self._set[i] = item

    def discard(self, item):
        if not isinstance(item, Package):
            raise TypeError('Not a Package.')

        try:
            self._set.remove(item)

        except:
            pass

    def difference(self, other):
        if not isinstance(other, PackageSet):
            raise TypeError('Not a PackageSet.')

        uniq_self = PackageSet()
        uniq_other = PackageSet()

        # find unique items to self
        for x in self._set:
            if not x in other:
                uniq_self.add(x)

        # find unique items to other
        for x in other:
            if not x in self._set:
                uniq_other.add(x)

        return (uniq_self, uniq_other)

    def union(self, *args):
        if len(args) == 0:
            raise Exception('No PackageSets defined for union.')

        u = PackageSet(self._set)

        for o in args:
            if not isinstance(o, PackageSet):
                raise TypeError('Not a PackageSet.')

            # add takes care of uniqueness so let's use it
            for x in o:
                u.add(x)

        return u

    def update(self, *args):
        for o in args:
            if not isinstance(o, PackageSet):
                raise TypeError('Not a PackageSet.')

            # add takes care of uniqueness so let's use it
            for x in o:
                self.add(x)

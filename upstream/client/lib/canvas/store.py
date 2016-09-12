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
import hawkey
import json
import re

from canvas.set import CanvasSet

# name[[#epoch]@version-release][:arch]
RE_PACKAGE = re.compile("^([+~])?([^#@:\s]+)(?:(?:#(\d+))?@([^\s-]+)-([^:\s-]+))?(?::(\w+))?$")
RE_GROUP = re.compile("^([+~])?(@[\w ]+)$")


class ErrorInvalidStore(Exception):
    def __init__(self, reason, code=0):
        self.reason = reason.lower()
        self.code = code

    def __str__(self):
        return 'error: {0}'.format(str(self.reason))

#
# CLASS DEFINITIONS / IMPLEMENTATIONS
#


class Store(object):
    """ A Canvas object that represents an installable Store. """

    # CONSTANTS
    ACTION_PIN              = 0x80
    ACTION_GROUP_OPTIONAL   = 0x40
    ACTION_GROUP_NODEFAULTS = 0x20
    ACTION_GROUP            = 0x10
    ACTION_EXCLUDE          = 0x02
    ACTION_INCLUDE          = 0x01

    def __init__(self, *args, **kwargs):
        self.name     = kwargs.get('name', None)
        self.type     = kwargs.get('epoch', None)
        self.url      = kwargs.get('version', None)
        self.username = kwargs.get('release', None)
        self.password = kwargs.get('arch', None)
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
        if isinstance(other, Store):
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
        return 'Store: %s' % (self.to_json())

    def __str__(self):
        return 'Store: %s' % (self.to_pkg_spec())

    def excluded(self):
        return self.action & (self.ACTION_EXCLUDE) == self.ACTION_EXCLUDE

    def included(self):
        return self.action & (self.ACTION_INCLUDE) == self.ACTION_INCLUDE

    def parse(self, data):
        if isinstance(data, dnf.package.Store):
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
            g = RE_GROUP.match(data)

            if m is not None:
                regex = m
            elif g is not None:
                regex = g
            else:
                raise ErrorInvalidStore("package format invalid")

            if regex.group(1) == '~':
                self.action = self.ACTION_EXCLUDE
            else:
                self.action = self.ACTION_INCLUDE

            self.name    = regex.group(2)
            if regex is m:
                self.epoch   = regex.group(3)
                self.version = regex.group(4)
                self.release = regex.group(5)
                self.arch    = regex.group(6)

        # detect group packages
        if isinstance(self.name, str) and self.name.startswith('@'):
            self.action |= self.ACTION_GROUP

    def pinned(self):
        return self.action & (self.ACTION_PIN) == self.ACTION_PIN

    def to_json(self):
        return json.dumps(self.to_object(), separators=(',', ':'), sort_keys=True)

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
        evr = ''

        if self.epoch is not None or self.version is not None:
            f += '-'

        if self.epoch is not None:
            evr = self.epoch + ':'

        if self.version is not None and self.release is not None:
            db = dnf.Base()
            conf = db.conf.substitutions
            evr += '{0}-{1}.fc{2}'.format(self.version, self.release, conf['releasever'])
        elif self.version is not None:
            evr += self.version

        # append evr if appropriate
        if evr:
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

        if not p_list:
            return None

        return list(p_list)[0]

class StoreSet(CanvasSet):
    def __init__(self, initvalue=()):
        CanvasSet.__init__(self, initvalue)


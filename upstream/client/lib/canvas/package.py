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

import hawkey
import json
import re
import dnf

from canvas.set import CanvasSet

#
# CLASS DEFINITIONS / IMPLEMENTATIONS
#
class Package(object):
    """ A Canvas object that represents an installable Package. """

    # name[[#epoch]@version-release][:arch]
    RE_PACKAGE = re.compile(r"^([+~!])?([^#@:\s]+)(?:(?:#(\d+))?@([^\s-]+)-([^:\s-]+))?(?::(\w+))?$")
    RE_GROUP = re.compile(r"^([+~!])?(@[\w ]+)$")

    # CONSTANTS
    ACTION_PIN              = 0x80
    ACTION_GROUP_OPTIONAL   = 0x40
    ACTION_GROUP_NODEFAULTS = 0x20
    ACTION_GROUP            = 0x10
    ACTION_IGNORE           = 0x04
    ACTION_EXCLUDE          = 0x02 # Should we remove a package if it is installed
    ACTION_INCLUDE          = 0x01 # Should we install a package if it is missing
    # NOTE: Valid combinations of EXCLUDE and INCLUDE are as follows
    # INCLUDE | EXCLUDED
    #    T    |    F
    #    F    |    T
    #    F    |    F


    def __init__(self, package, evr=True, template=None):
        if isinstance(package, dnf.package.Package) or \
                isinstance(package, hawkey.Package):
            package = Package.parse_dnf(package, template=template)
        elif isinstance(package, str):
            package = Package.parse_str(package, template=template)

        if not isinstance(package, dict):
            raise TypeError("Package must be a dict")

        self.name     = package.get('n', None)
        self.epoch    = package.get('e', None)
        self.version  = package.get('v', None)
        self.release  = package.get('r', None)
        self.arch     = package.get('a', None)
        self.action   = package.get('z', self.ACTION_INCLUDE)
        self.template = package.get('t', template)

        if not self.name:
            raise ValueError("Name cannot be None")

        if (self.version and not self.release) or \
            (not self.version and self.release):
            raise ValueError("Both version and release must be specified")

        # fix all exclude actions of value 0
        if self.action == 0:
            self.action = self.ACTION_EXCLUDE

        # detect group packages
        if self.name.startswith('@'):
            self.action |= self.ACTION_GROUP

        # strip evr information as appropriate
        # NOTE: for things like pushing current state into a template
        if not evr:
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
        return not self.__eq__(other)

    def __repr__(self):
        return 'Package: %s' % (self.to_json())

    def __str__(self):
        return 'Package: %s' % (self.to_pkg_spec())

    @property
    def excluded(self):
        """ Is the package excluded from a template """
        return self.action & (self.ACTION_EXCLUDE) == self.ACTION_EXCLUDE

    @property
    def ignored(self):
        """ Is the package ignored """
        return self.action & (self.ACTION_IGNORE) == self.ACTION_IGNORE

    @property
    def included(self):
        """ Is the package included in a template """
        return self.action & (self.ACTION_INCLUDE) == self.ACTION_INCLUDE

    def is_group(self):
        return self.name[0] == '@'

    @classmethod
    def parse_dnf(cls, pkg, template=None):
        """ Generate a Package dictionary from a dnf package

        Note: String cannot support the pkg_spec format:
            name-[epoc:]version
            as revision must also be specified

        Args:
            cls: Holds the Package class
            package: DNF or hawkey package
        Returns:
            The dictionary conversion of the dnf package
        Raises:
            TypeError: If package is not a dnf or hawkey package

        """
        if not (isinstance(pkg, dnf.package.Package) or \
                isinstance(pkg, hawkey.Package)):
            raise TypeError("Pkg needs to be a DNF or hawkey package object")

        return {
            'n': pkg.name,
            'e': pkg.epoch,
            'v': pkg.version,
            'r': pkg.release,
            'a': pkg.arch,
            't': template
        }

    @classmethod
    def parse_str(cls, package, template=None):
        """ Generate a Package dictionary from a Package string.

        Note: String cannot support the pkg_spec format:
              name-[epoc:]version
              as revision must also be specified

        Args:
            cls: Holds the Package class
            package: String representation of a package
        Returns:
            The dictionary conversion of the package string
        Raises:
            TypeError: If package is not a string
            ValueError: If string does not match either the Package or groups formats

        """
        if not isinstance(package, str):
            raise TypeError("Package needs to be a string")

        pkg_match = cls.RE_PACKAGE.match(package)
        grp_match = cls.RE_GROUP.match(package)
        action = cls.ACTION_INCLUDE

        if pkg_match is not None:
            regex = pkg_match
        elif grp_match is not None:
            regex = grp_match
        else:
            raise ValueError

        if regex.group(1) == '~':
            action = cls.ACTION_EXCLUDE

        elif regex.group(1) == '!':
            action = cls.ACTION_IGNORE

        name = regex.group(2)

        if regex is pkg_match:
            epoch   = regex.group(3)
            version = regex.group(4)
            release = regex.group(5)
            arch    = regex.group(6)

            return {
                'n': name,
                'e': epoch,
                'v': version,
                'r': release,
                'a': arch,
                'z': action,
                't': template
            }

        return {'n': name, 'z': action, 't': template}

    @property
    def pinned(self):
        """ Is the package pinned to its version """
        return self.action & (self.ACTION_PIN) == self.ACTION_PIN

    def to_kickstart(self):
        """ Return a kickstart compatible string representation """
        if self.included:
            return self.name

        elif self.excluded:
            return "-" + self.name

        return ''

    def to_json(self):
        """ Return a json representation of the package object """
        return json.dumps(self.to_object(), separators=(',', ':'), sort_keys=True)

    def to_object(self):
        """ Return a dictionary representation of the package object """
        obj = {
            'n': self.name,
            'e': self.epoch,
            'v': self.version,
            'r': self.release,
            'a': self.arch,
            'z': self.action,
        }

        # only build with non-None values
        return {k: v for k, v in obj.items() if v != None}

    def to_pkg_spec(self):
        """ Return a dictionary representation of the package object """
        pkg = self.name

        # calculate evr
        evr = ''

        if self.epoch is not None or self.version is not None:
            pkg += '-'

        if self.epoch is not None:
            evr = self.epoch + ':'

        if self.version is not None and self.release is not None:
            db = dnf.Base()
            conf = db.conf.substitutions
            evr += '{0}-{1}.fc{2}'.format(self.version, self.release, conf['releasever'])
        # NOTE: This is valid according to DNF docs,
        # however current str form makes this impossible
        #elif self.version is not None:
        #    evr += self.version

        # append evr if appropriate
        if evr:
            pkg += evr

        # append arch if appropriate
        if self.arch is not None:
            pkg += '.' + self.arch

        return pkg

    def to_pkg(self, db=None):
        """ Convert this package into a DNF Package object.
        Args:
            db: A DNF Base object
        Returns:
            The DNF package object
        Raises:
            OSError: If errors are encountered in DNF

        """

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


class PackageSet(CanvasSet):
    def __init__(self, initvalue=()):
        CanvasSet.__init__(self, initvalue)

    def add(self, item):
        if item not in self._set:
            self._set.append(item)

        # add if new package has more explicit arch definition than existing
        elif item.arch is not None:
            for i, x in enumerate(self._set):
                if x.name == item.name and x.arch is None:
                    self._set[i] = item


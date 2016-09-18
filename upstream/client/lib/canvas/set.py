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

class CanvasSet(collections.MutableSet):
    def __init__(self, initvalue=()):
        self._set = []

        for value in initvalue:
            self.add(value)

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
        if item not in self._set:
            self._set.append(item)

    def as_list(self):
        return list(self._set)

    def discard(self, item):
        if item not in self._set:
            raise ValueError("item not in set")

        self._set.remove(item)

    def difference(self, other):
        if not isinstance(other, CanvasSet):
            raise NotImplementedError

        uniq_self = self.__class__()
        uniq_other = self.__class__()

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
            raise Exception('No CanvasSets defined for union.')

        u = self.__class__(self._set)

        for o in args:
            if not isinstance(o, CanvasSet):
                raise NotImplementedError

            # add takes care of uniqueness so let's use it
            for x in o:
                u.add(x)

        return u

    def update(self, *args):
        for o in args:
            if not isinstance(o, CanvasSet):
                raise TypeError('Not a CanvasSet %s %s.' % (type(o).__name__, type(self).__name__))

            # add takes care of uniqueness so let's use it
            for x in o:
                self.add(x)

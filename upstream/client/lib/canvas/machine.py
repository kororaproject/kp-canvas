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

import json
import re
import yaml

RE_MACHINE = re.compile("(?:(?P<user>[\w\.\-]+):)?(?P<name>[\w\.\-]+)(?!.*:)(?:@(?P<version>[\w\.\-]+))?")

class ErrorInvalidMachine(Exception):
    def __init__(self, reason, code=0):
        self.reason = reason.lower()
        self.code = code

    def __str__(self):
        return 'error: {0}'.format(str(self.reason))

class Machine(object):
    def __init__(self, machine=None, user=None, key=None):
        self._name        = None
        self._user        = user
        self._template    = None
        self._uuid        = None
        self._version     = None
        self._title       = ''
        self._description = ''
        self._key         = key

        self._stores   = []       # remote stores for machine
        self._archives = []       # archive definitions in machine
        self._history  = []       # history of machine
        self._meta     = {}

        self._parse_machine(machine)

    def __str__(self):
        return 'Machine: {0} (owner: {1})- S:{2}, A:{3}, H:{4}'.format(
            self._name,
            self._user,
            len(self._stores),
            len(self._archives),
            len(self._history)
            )

    def _parse_machine(self, machine):
        # parse the string short form
        if isinstance(machine, str):
            m = RE_MACHINE.match(machine)

            if m:
                print(m.groups())
                if m.group('user') is not None:
                    self._user = m.group('user').strip()

                if m.group('name') is not None:
                    self._name = m.group('name').strip()

                if m.group('version') is not None:
                    self._version = m.group('version').strip()

            else:
                raise ErrorInvalidMachine("machine format invalid")

            if not self._name or len(self._name) == 0:
                raise ErrorInvalidMachine("machine format invalid")


        # parse the dict form, the most common form and directly
        # relates to the json structures returned by canvas server
        elif isinstance(machine, dict):
            self._uuid = machine.get('uuid', self._uuid)
            self._template = machine.get('template', self._template)
            self._user = machine.get('user', machine.get('username', None))
            self._name = machine.get('stub', self._name)
            self._version = machine.get('version', None)
            self._title = machine.get('name', self._title)
            self._description = machine.get('description', None)

            self._stores   = machine.get('stores', [])
            self._archives = machine.get('archives', [])
            self._history  = machine.get('history', [])
            self._meta = machine.get('meta', {})

    #
    # PROPERTIES
    @property
    def archives(self):
        return self._archives

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value is None or len(str(value)) == 0:
            return

        self._description = str(value)

    @property
    def history(self):
        return self._history

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def stores(self):
        return self._stores

    @property
    def template(self):
        return self._template

    @template.setter
    def template(self, value):
        self._template = value

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def user(self):
        return self._user

    @property
    def uuid(self):
        return self._uuid

    @uuid.setter
    def uuid(self, value):
        self._uuid = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        if value is None or len(str(value)) == 0:
            return

        self._version = str(value)

    #
    # PUBLIC METHODS

    def to_json(self):
        return json.dumps(self.to_object(), separators=(',', ':'))

    def to_object(self):
        return {
            'uuid':        self._uuid,
            'template':    self._template,
            'name':        self._name,
            'user':        self._user,
            'title':       self._title,
            'description': self._description,
            'stores':      self._stores,
            'archives':    self._archives,
            'history':     self._history,
            'meta':        self._meta,
        }

    def to_yaml(self):
        return yaml.dump(self.to_object())

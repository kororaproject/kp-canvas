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

import configparser
import os


class Config(object):
    def __init__(self, path=None):
        self.config = configparser.ConfigParser()
        self.system_config_path = "/etc/canvas/canvas.conf"
        self.home_config_path = os.path.join(os.path.expanduser('~'), '.config', 'canvas.conf')

        # look for local user config
        if path is None:
            if os.path.exists(self.home_config_path):
                self.config.read(self.home_config_path)

            # also check for system config
            elif os.path.exists(self.system_config_path):
                self.config.read(self.system_config_path)
        else:
            # Overwrite defult home_config_path with passed value
            self.home_config_path = path
            if os.path.exists(path):
                self.config.read(self.home_config_path)

    def __repr__(self):
        print(self.config)

    def __str__(self):
        print(self.config)

    def get(self, section, key, default=None):
        if section not in self.config.sections():
            return default

        return self.config[section].get(key, default)

    def save(self):
        # always write to local config
        with open(self.home_config_path, 'w+') as configfile:
            self.config.write(configfile)

    def sections(self):
        return self.config.sections()

    def set(self, section, key, value):
        if section not in self.config.sections():
            self.config[section] = {}

        self.config[section][key] = value

    def unset(self, section, key):
        if section not in self.config.sections():
            return False

        return self.config.remove_option(section, key)

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

import getpass
import logging
import prettytable

from canvas.cli.commands import Command
from canvas.object import Object, ErrorInvalidObject
from canvas.service import Service, ServiceException
from canvas.template import Template

logger = logging.getLogger('canvas')


class ObjectCommand(Command):
    def configure(self, config, args, args_extra):
        # store loaded config
        self.config = config

        # create our canvas service object
        self.cs = Service(host=args.host, username=args.username)

        # store args for additional processing
        self.args = args

        # return false if any error, help, or usage needs to be shown
        return not args.help

    def help(self):
        # check for action specific help first
        if self.args.action is not None:
            try:
                command = getattr(self, 'help_{0}'.format(self.args.action))

                # show action specific if available
                if command:
                    return command()

            except:
                pass

        # fall back to general usage
        print("General usage: {0} [--version] [--help] [--verbose] object [<args>]\n"
              "\n"
              "Specific usage:\n"
              "{0} object add [user:]template[@version] [store:]object_name [--action=...]\n"
              "{0} object list [user:]template[@version] [--filter-store=...] [--filter-name=...]"
              "{0} object rm [user:]template[@version] store1:object_name1 store2:object_name2 ... storeN:object_nameN"
              "\n".format(self.prog_name))

    def help_add(self):
        print("Usage: {0} object add [user:]template[@version]\n"
              "           [store:]object_name --data=|--data-file=|--source= --action= [--action= ...]\n"
              "\n"
              "Availablle actions are: \n"
              "  copy\n"
              "  copy-once\n"
              "  extract\n"
              "  extract-once\n"
              "  execute\n"
              "  execute-once\n"
              "  ks-pre\n"
              "  ks-pre-install\n"
              "  ks-post\n"
              "\n".format(self.prog_name))

    def run(self):
        command = None
        # search for our function based on the specified action
        try:
            command = getattr(self, 'run_{0}'.format(self.args.action))

        except:
            self.help()
            return 1

        if not command:
            print('error: action is not reachable.')
            return

        return command()

    def run_add(self):
        t = Template(self.args.template, user=self.args.username)

        print(self.args)

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            print(e)
            return 1

        try:
            obj = Object(data=self.args.data, data_file=self.args.data_file, source=self.args.source)
        except ErrorInvalidObject as e:
            print (e)
            return 1

        t.add_object(obj)

        # describe process for dry runs
        if self.args.dry_run:
            print('The following object would be added to the template: {0}'.format(t.name))

            print('  - ' + str(obj))
            print()

        return 0

        # push our updated template
        try:
            res = self.cs.template_update(t)

        except ServiceException as e:
            print(e)
            return 1

        return 0

    def run_list(self):
        t = Template(self.args.template, user=self.args.username)

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            print(e)
            return 1


    def run_rm(self):
        t = Template(self.args.template, user=self.args.username)

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            print(e)
            return 1

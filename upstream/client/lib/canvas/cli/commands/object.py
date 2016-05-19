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
              "{0} object add [user:]template[@version] store1:object_name1 store2:object_name2 ... storeN:object_nameN\n"
              "{0} object list [user:]template[@version] [--filter-store=...] [--filter-name=...]"
              "{0} object rm [user:]template[@version] store1:object_name1 store2:object_name2 ... storeN:object_nameN"
              "\n".format(self.prog_name))

    def help_add(self):
        print("Usage: {0} object add [user:]template[@version]"
              "           store1:object_name1 store2:object_name2 ... storeN:object_nameN\n"
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

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            print(e)
            return 1

        for o in self.args.objects:
            try:
                pkg = Object(o)
            except ErrorInvalidObject as e:
                print (e)
                return 1

            t.add_object(pkg)

        objects = list(t.objects_delta)
        objects.sort(key=lambda x: x.name)

        # describe process for dry runs
        if self.args.dry_run:
            if len(objects):
                print('The following would be added to the template: {0}'.format(t.name))

                for o in objects:
                    print('  - ' + str(o))

                print()
                print('Summary:')
                print('  - Object(s): %d' % (len(objects)))
                print()

            else:
                print('No template changes required.')

            print('No action peformed during this dry-run.')
            return 0

        if not len(objects):
            print('info: no changes detected, template up to date.')
            return 0

        # push our updated template
        try:
            res = self.cs.template_update(t)

        except ServiceException as e:
            print(e)
            return 1

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

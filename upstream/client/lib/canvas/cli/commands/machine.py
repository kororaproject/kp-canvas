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
import logging
import yaml
import sys

from canvas.cli.commands import Command
from canvas.machine import Machine
from canvas.package import Package
from canvas.repository import Repository
from canvas.service import Service, ServiceException
from canvas.template import Template
from canvas.texttable import TextTable

logger = logging.getLogger('canvas')


class MachineCommand(Command):
    def configure(self, config, args, args_extra, parsers):
        if args.action == None:
            parsers.machine.print_help()
            sys.exit(1)

        # store loaded config
        self.config = config

        # create our canvas service object
        self.cs = Service(host=args.host, username=args.username)

        # store args for additional processing
        self.args = args

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
        print("General usage: {0} [--version] [--help] [--verbose] machine [<args>]\n"
              "{0} machine add [user:]name [--description=] [--location=] [--name=] [--template=]\n"
              "{0} machine update [user:]name [--description=] [--location=] [--name=] [--template=]\n"
              "{0} machine list [user] [--filter-name] [--filter-description]\n"
              "{0} machine rm [user:]name\n"
              "{0} machine diff [user:]name [--output=path]\n"
              "{0} machine connect [user:]name\n"
              "{0} machine cmd [user:]name command arg1 arg2 ... argN\n"
              "{0} machine sync [user:]name [--pull [[user:]template]] | --push [user:]template]\n"
              "{0} machine disconnect [user:]name\n"
              "\n".format(self.prog_name))

    def help_add(self):
        print("Usage: {0} machine add [user:]machine [user:]template [--title] [--description]\n"
              "\n".format(self.prog_name))

    def help_cmd(self):
        pass

    def help_connect(self):
        pass

    def help_disconnect(self):
        pass

    def help_diff(self):
        pass

    def help_list(self):
        pass

    def help_rm(self):
        pass

    def help_sync(self):
        pass

    def help_update(self):
        pass

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
        m = Machine(self.args.machine, user=self.args.username)
        t = Template(self.args.template, user=self.args.username)

        # grab the template we're associating to the machine
        try:
            t = self.cs.template_get(t, auth=True, resolve_includes=False)

        except ServiceException as e:
            print(e)
            return 1

        # add template uuid to machine
        m.template = t.uuid

        # add machine bits that are specified
        if self.args.description is not None:
            m.description = self.args.description

        try:
            res = self.cs.machine_create(m)

        except ServiceException as e:
            print(e)
            return 1

        print(res)

        # update config with our newly added (registered) machine
        self.config.set('machine', 'uuid', res['uuid'])
        self.config.set('machine', 'key', res['key'])
        self.config.save()

        print('info: machine added.')
        return 0

    def run_cmd(self):
        print('MACHINE CMD')

    def run_diff(self):
        uuid = self.config.get('machine', 'uuid')
        key = self.config.get('machine', 'key')

        try:
            res = self.cs.machine_sync(uuid, key, template=True)

        except ServiceException as e:
            print(e)
            return 1

        m = Machine(res['template'])
        t = Template(res['template'])

        ts = Template.from_system()

        (l_r, r_l) = t.package_diff(ts.packages_all)

        print("In template not in system:")

        for p in l_r:
            print(" - {0}".format(p.name))

        print()
        print("On system not in template:")

        for p in r_l:
            print(" + {0}".format(p.name))

        print()

    def run_list(self):
        # fetch all accessible/available templates
        try:
            machines = self.cs.machine_list(
                user=self.args.filter_user,
                name=self.args.filter_name,
                description=self.args.filter_description
            )

        except ServiceException as e:
            print(e)
            return 1

        if len(machines):
            l = TextTable(['[USER:]NAME', 'TITLE'])

            # add table items and print
            for m in machines:
                l.add_row(["{0}:{1}".format(m['username'], m['stub']), m['name']])

            print(l)

            # print summary
            print('\n{0} machine(s) found.'.format(len(machines)))

        else:
            print('0 machines found.')

    def run_rm(self):
        m = Machine(self.args.machine, user=self.args.username)

        try:
            res = self.cs.machine_delete(m)

        except ServiceException as e:
            print(e)
            return 1

        self.config.unset('machine', 'uuid')
        self.config.unset('machine', 'key')
        self.config.save()

        print('info: machine removed.')
        return 0

    def run_sync(self):
        uuid = self.config.get('machine', 'uuid')
        key = self.config.get('machine', 'key')

        try:
            res = self.cs.machine_sync(uuid, key, template=True)

        except ServiceException as e:
            print(e)
            return 1

        m = Machine(res['template'])
        t = Template(res['template'])

        t.system_prepare()

        # describe process for dry runs
        if self.args.dry_run:
            tx = t.system_transaction()
            packages_install = list(tx.install_set)
            packages_install.sort(key=lambda x: x.name)

            packages_remove = list(tx.remove_set)
            packages_remove.sort(key=lambda x: x.name)
            if len(packages_install) or len(packages_remove):
                print('The following would be installed to (+) and removed from (-) the system:')

                for p in packages_install:
                    print('  + ' + str(p))

                for p in packages_remove:
                    print('  - ' + str(p))

                print()
                print('Summary:')
                print('  - Package(s): %d' % (len(packages_install)+len(packages_remove)))
                print()

            else:
                print('No system changes required.')

            print('No action peformed during this dry-run.')
            return 0

        # TODO: progress for download, install and removal
        t.to_system_apply(clean=False)

        print('info: machine synced.')

        return 0

    def run_update(self):
        m = Machine(self.args.machine, user=self.args.username)

        try:
            m = self.cs.machine_get(m)

        except ServiceException as e:
            print(e)
            return 1

        # add machine bits that are specified for update
        if self.args.template:
            t = Template(self.args.template, user=self.args.username)

            try:
                t = self.cs.template_get(t, resolve_includes=False)

            except ServiceException as e:
                print(e)
                return 1

            m.template = t.uuid

        if self.args.name is not None:
            m.name = self.args.name

        if self.args.title is not None:
            m.title = self.args.title

        if self.args.title is not None:
            m.title = self.args.title

        if self.args.description is not None:
            m.description = self.args.description

        try:
            res = self.cs.machine_update(m)

        except ServiceException as e:
            print(e)
            return 1

        print('info: machine updated.')
        return 0

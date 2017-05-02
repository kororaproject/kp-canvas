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

import logging
import sys

from canvas.cli.commands import Command
from canvas.package import Package
from canvas.service import Service, ServiceException
from canvas.template import Template
from canvas.texttable import TextTable

logger = logging.getLogger('canvas')


class PackageCommand(Command):
    def configure(self, config, args, args_extra, parsers):
        if args.action == None:
            parsers.package.print_help()
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
        print("General usage: {0} [--version] [--help] [--verbose] package [<args>]\n"
              "\n"
              "Specific usage:\n"
              "{0} package add [user:]template[@version] [--nodeps] package1 packagelist1 package2 ... packageN\n"
              "{0} package list [user:]template[@version] [--filter-name] [--filter-summary] [--filter-description] [--filter-arch] [--filter-repo] [--output=path]\n"
              "{0} package rm [user:]template[@version] [--nodeps] package1 package2 ... packageN\n"
              "{0} package update [user:]template[@version] [--nodeps] package1 packagelist1 package2 ... packageN\n"
              "\n".format(self.prog_name))

    def help_add(self):
        print("Usage: {0} package add [user:]template[@version] [--nodeps]\n"
              "           package1 packagelist1 package2 ... packageN\n"
              "\n"
              "Options:\n"
              "  --nodeps       Do not automatically remove dependencies\n"
              "\n".format(self.prog_name))

    def help_list(self):
        pass

    def help_rm(self):
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
        t = Template(self.args.template, user=self.args.username)

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            print(e)
            return 1

        for p in self.args.package:
            try:
                pkg = Package(p)
            except TypeError as e:
                print (e)
                return 1

            t.add_package(pkg)

        packages = list(t.packages_delta)
        packages.sort(key=lambda x: x.name)

        # describe process for dry runs
        if self.args.dry_run:
            if len(packages):
                print('The following would be added to the template: {0}'.format(t.name))

                for p in packages:
                    print('  - ' + str(p))

                print()
                print('Summary:')
                print('  - Package(s): %d' % (len(packages)))
                print()

            else:
                print('No template changes required.')

            print('No action peformed during this dry-run.')
            return 0

        if not len(packages):
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

        packages = list(t.packages_all)
        packages.sort(key=lambda x: x.name)

        if len(packages):
            l = TextTable(header=['PACKAGE', 'EPOCH', 'VERSION', 'RELEASE', 'ARCH', 'ACTION'])

            for p in packages:
                if p.epoch is None:
                    p.epoch = '-'

                if p.version is None:
                    p.version = '-'

                if p.release is None:
                    p.release = '-'

                if p.arch is None:
                    p.arch = '-'

                if p.included:
                    p.action = '+'

                else:
                    p.action = '-'

                l.add_row([p.name, p.epoch, p.version, p.release, p.arch, p.action])

            print(l)
            print()

        else:
            print('0 packages defined.')

    def run_rm(self):
        t = Template(self.args.template, user=self.args.username)

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            print(e)
            return 1

        packages = []

        for p in self.args.package:
            p = Package(p)
            if t.remove_package(p):
                packages.append(p)

        packages.sort(key=lambda x: x.name)

        # describe process for dry runs
        if self.args.dry_run:
            if len(packages):
                print('The following would be removed from the template: {0}'.format(t.name))

                for p in packages:
                    print('  - ' + str(p))

                print()
                print('Summary:')
                print('  - Package(s): %d' % (len(packages)))
                print()

            else:
                print('No template changes required.')

            print('No action peformed during this dry-run.')
            return 0

        if not len(packages):
            print('info: no changes detected, template up to date.')
            return 0

        # push our updated template
        try:
            res = self.cs.template_update(t)

        except ServiceException as e:
            print(e)
            return 1

    def run_update(self):
        t = Template(self.args.template, user=self.args.username)

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            print(e)
            return 1

        # track updates to determine server update
        updated = False

        for p in self.args.package:

            # parse new and find old
            pn = Package(p)

            print(pn)

            if pn not in t.packages:
                print('warn: package is not defined in template.')
                continue

            # update with new and track
            if t.update_package(pn):
                updated = True

        if not updated:
            print('info: no changes detected.')
            return 0

        # push our updated template
        try:
            res = self.cs.template_update(t)

        except ServiceException as e:
            print(e)
            return 1

        print('info: package(s) updated.')
        return 0

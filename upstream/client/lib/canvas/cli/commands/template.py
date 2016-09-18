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
import getpass
import json
import logging
import os
import prettytable
import subprocess
import yaml

from functools import reduce

from canvas.cli.commands import Command
from canvas.package import Package
from canvas.repository import Repository
from canvas.service import Service, ServiceException
from canvas.template import Template

logger = logging.getLogger('canvas')


class TemplateCommand(Command):
    def configure(self, config, args, args_extra):
        # store loaded config
        self.config = config

        # create our canvas service object
        self.cs = Service(host=args.host, username=args.username)

        try:
            # expand includes
            if args.includes is not None:
                args.includes = args.includes.split(',')
        except:
            pass

        # eval public
        try:
            if args.public is not None:
                args.public = (args.public.lower() in ['1', 'true', 'yes', 'y'])
        except:
            pass

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
        print("General usage: {0} [--version] [--help] [--verbose] template [<args>]\n"
              "\n"
              "Specific usage:\n"
              "{0} template add [user:]template[@version] [--title] [--description] [--includes] [--public]\n"
              "{0} template update [user:]template[@version] [--title] [--description] [--includes] [--public]\n"
              "{0} template rm [user:]template[@version]\n"
              "{0} template push [user:]template[@version] [--all]\n"
              "{0} template pull [user:]template[@version] [--clean]\n"
              "{0} template diff [user:]template[@version]\n"
              "{0} template copy [user_from:]template_from[@version] [[user_to:]template_to[@version]]\n"
              "{0} template list [--public]\n"
              "\n".format(self.prog_name))

    def help_add(self):
        print("Usage: {0} template add [user:]template[@version] [--title] [--description]\n"
              "                           [--includes] [--public]\n"
              "\n"
              "Options:\n"
              "  --title        TITLE     Define the pretty TITLE of template\n"
              "  --description  TEXT      Define descriptive TEXT of the template\n"
              "  --includes     TEMPLATE  Comma separated list of TEMPLATEs to include\n"
              "\n"
              "\n".format(self.prog_name))

    def help_copy(self):
        pass

    def help_diff(self):
        pass

    def help_iso(self):
        pass

    def help_list(self):
        pass

    def help_pull(self):
        pass

    def help_push(self):
        pass

    def help_update(self):
        print("Usage: {0} template update [user:]template[@version] [--title] [--description]\n"
              "                           [--includes] [--public]\n"
              "\n"
              "Options:\n"
              "  --title        TITLE     Define the pretty TITLE of template\n"
              "  --description  TEXT      Define descriptive TEXT of the template\n"
              "  --includes     TEMPLATE  Comma separated list of TEMPLATEs to include\n"
              "\n"
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

        # add template bits that are specified
        if self.args.title is not None:
            t.title = self.args.title

        if self.args.description is not None:
            t.description = self.args.description

        if self.args.includes is not None:
            t.includes = self.args.includes

        if self.args.public is not None:
            t.public = self.args.public

        try:
            res = self.cs.template_create(t)

        except ServiceException as e:
            print(e)
            return 1

        print('info: template added.')
        return 0

    def run_copy(self):
        t = Template(self.args.template_from, user=self.args.username)

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            print(e)
            return 1

        # reparse for template destination
        t.parse(self.args.template_to)

        try:
            res = self.cs.template_create(t)

        except ServiceException as e:
            print(e)
            return 1

        print('info: template copied.')
        return 0

    def run_diff(self):
        t = Template(self.args.template_from, user=self.args.username)

        # grab the template we're pushing to
        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            print(e)
            return 1

        # fetch template to compare to
        if self.args.template_to is not None:
            ts = Template(self.args.template_to, user=self.args.username)

            try:
                ts = self.cs.template_get(ts)

            except ServiceException as e:
                print(e)
                return 1

        # otherwise build from system
        else:
            ts = Template.from_system()

        (l_r, r_l) = t.package_diff(ts.packages_all)

        if len(l_r):
            print('In template and not marked for install in system:')

            for p in l_r:
                print(" * {0}".format(p.name))

            print()

        if len(r_l):
            print('Marked for install on system and not in template:')

            for p in r_l:
                print(" * {0}".format(p.name))

        print()

    def run_dump(self):
        t = Template(self.args.template, user=self.args.username)

        try:
            t = self.cs.template_get(t, resolve_includes=not self.args.no_resolve_includes)

        except ServiceException as e:
            print(e)
            return 1

        if self.args.kickstart:
            print(t.to_kickstart(resolved=not self.args.no_resolve_includes))
            return 0

        elif self.args.yaml:
            print(yaml.dump(t.to_object(resolved=not self.args.no_resolve_includes), indent=4))
            return 0

        elif self.args.json:
            print(json.dumps(t.to_object(resolved=not self.args.no_resolve_includes), indent=4, sort_keys=True))
            return 0

        # pretty general information
        print('Name: {0} ({1})'.format(t.name, t.user))

        if t.description is not None and len(t.description):
            print('Description:\n{0}\n'.format(t.description))

        # pretty print includes
        if len(t.includes):
            print('Includes:')
            for i in t.includes:
                print(' - {0}'.format(i))
            print()

        # pretty print packages
        repos = list(t.repos_all)
        repos.sort(key=lambda x: x.stub)

        if len(repos):
            l = prettytable.PrettyTable(['repo', 'name', 'priority', 'cost', 'enabled'])
            l.min_table_width = 120
            l.hrules = prettytable.HEADER
            l.vrules = prettytable.NONE
            l.align = 'l'
            l.padding_witdth = 1

            for r in repos:
                if r.cost is None:
                    r.cost = '-'

                if r.priority is None:
                    r.priority = '-'

                if r.enabled:
                    r.enabled = 'Y'

                else:
                    r.enabled = 'N'

                l.add_row([r.stub, r.name, r.priority, r.cost, r.enabled])

            print(l)
            print()

        # pretty print packages
        packages = list(t.packages_all)
        packages.sort(key=lambda x: x.name)

        if len(packages):
            l = prettytable.PrettyTable(['package', 'epoch', 'version', 'release', 'arch', 'action'])
            l.min_table_width = 120
            l.hrules = prettytable.HEADER
            l.vrules = prettytable.NONE
            l.align = 'l'
            l.padding_witdth = 1

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

        return 0

    def run_iso(self):
        t = Template(self.args.template, user=self.args.username)

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            print(e)
            return 1

        # calculate name and title for use if not specified
        arch = os.uname()[4]

        if arch in ['i386', 'i686']:
            arch_pretty = '32 bit'
            arch_pretty_long = '32 bit (%s)' % (arch)
        elif arch in ['x86_64']:
            arch_pretty = '64 bit'
            arch_pretty_long = '64 bit (%s)' % (arch)

        # we'll use version in our names
        if self.args.releasever is None:
            if t.version is None or t.version is '':
                self.args.releasever = 'HEAD'
            else:
                self.args.releasever = t.version

        name              = "{0}-{1}-{2}".format(t.name, self.args.releasever, arch)
        name_pretty       = "{0}-{1}-{2}".format(t.name, self.args.releasever, arch_pretty)
        title             = "{0} - {1} - {2}".format(t.title, self.args.releasever, arch_pretty)
        title_pretty_long = "{0} - {1} - {2}".format(t.title, self.args.releasever, arch_pretty_long)

        # build missing strings
        if self.args.resultdir is None:
            self.args.resultdir = "/var/tmp/canvas/isos/{0}".format(name.lower())

        if self.args.iso_name is None:
            self.args.iso_name = "{0}.iso".format(name.lower())

        if self.args.project is None:
            self.args.project = title

        if self.args.volid is None:
            self.args.volid = name.lower()

        if self.args.title is None:
            self.args.title = title_pretty_long

        if self.args.logfile is None:
            self.args.logfile = "/var/tmp/canvas/{0}.log".format(name.lower())

        # build kickstart file
        ks_file = "canvas-{0}.ks".format(t.uuid)
        ks_path = os.path.join("/var/tmp/canvas/ks", ks_file)

        # ensure our resultdir exists
        if not os.path.exists(os.path.dirname(ks_path)):
            os.makedirs(os.path.dirname(ks_path))

        with open(ks_path, 'w') as f:
            f.write(t.to_kickstart())

        env = os.environ.copy()

        # livemedia-creator
        if self.args.use_livemedia_creator:
            args = [
                    'livemedia-creator',
                    '--no-virt',
                    '--make-iso',
                    '--iso-only',
                    '--macboot',
                    '--ks',         ks_path,
                    '--resultdir',  self.args.resultdir,
                    '--project',    self.args.project,
                    '--volid',      self.args.volid,
                    '--iso-name',   self.args.iso_name,
                    '--releasever', self.args.releasever,
                    '--title',      self.args.title,
                    '--logfile',    self.args.logfile
                ]

        # livecd-creator
        else:
            args = [
                    'livecd-creator',
                    '--verbose',
                    '--config',     ks_path,
                    '--fslabel',    self.args.iso_name,
                    '--title',      self.args.title,
                    '--releasever', self.args.releasever,
                    '--product',    self.args.project,
                    '--cache',      self.args.resultdir,
                    '--logfile',    self.args.logfile
                ]

            env["setarch"] = arch

        subprocess.run(args, env=env)

        return 0

    def run_list(self):

        # fetch all accessible/available templates
        try:
            templates = self.cs.template_list(
                user=self.args.filter_user,
                name=self.args.filter_name,
                description=self.args.filter_description,
                public=self.args.public_only
            )

        except ServiceException as e:
            print(e)
            return 1

        if len(templates):
            l = prettytable.PrettyTable(["user:name", "title"])
            l.hrules = prettytable.HEADER
            l.vrules = prettytable.NONE
            l.align = 'l'
            l.padding_witdth = 1

            # add table items and print
            for t in templates:
                l.add_row(["{0}:{1}".format(t['username'], t['stub']), t['name']])

            print(l)

            # print summary
            print('\n{0} template(s) found.'.format(len(templates)))

        else:
            print('0 templates found.')

    def run_pull(self):
        # am i effectively root
        if os.geteuid() != 0:
            print('You need to have root privileges to modify the system.')
            return 0

        t = Template(self.args.template, user=self.args.username)

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            print(e)
            return 1

        t.system_prepare(clean=self.args.pull_clean)

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

        t.system_apply()

    def run_push(self):
        t = Template(self.args.template, user=self.args.username)

        # grab the template we're pushing to
        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            print(e)
            return 1

        if self.args.push_clean:
            t.clear()

        if self.args.kickstart is not None:
            print('info: parsing kickstart ...')
            t.from_kickstart(self.args.kickstart)

        else:
            # prepare dnf
            print('info: analysing system ...')
            db = dnf.Base()
            db.read_all_repos()
            db.read_comps()

            try:
                db.fill_sack()

            except OSError as e:
                pass

            db_list = db.iter_userinstalled()

            if self.args.push_all:
                db_list = db.sack.query().installed()

            # add our user installed packages
            for p in db_list:
                # no need to store versions
                t.add_package(Package(p, evr=False))

            # add only enabled repos
            for r in db.repos.enabled():
                t.add_repo(Repository(r))

        objects = list(t.objects_delta)
        objects.sort(key=lambda x: x.name)

        packages = list(t.packages_delta)
        packages.sort(key=lambda x: x.name)

        repos = list(t.repos_delta)
        repos.sort(key=lambda x: x.name)

        # describe process for dry runs
        if self.args.dry_run:
            if len(packages) or len(repos):
                print('The following would be added to the template: {0}'.format(t.name))

                for r in repos:
                    print('  - ' + str(r))

                for p in packages:
                    print('  - ' + str(p))

                for o in objects:
                    print('  - ' + str(o))

                print()
                print('Summary:')
                print('  - Repo(s): %d' % (len(repos)))
                print('  - Package(s): %d' % (len(packages)))
                print('  - Object(s): %d' % (len(objects)))
                print()

            else:
                print('No template changes required.')

            print('No action peformed during this dry-run.')
            return 0

        if self.args.kickstart is None and not len(packages) and not len(repos):
            print('info: no changes detected, template up to date.')
            return 0

        # push our updated template
        try:
            res = self.cs.template_update(t)

        except ServiceException as e:
            print(e)
            return 1

        print('info: template pushed.')
        return 0

    def run_rm(self):
        t = Template(self.args.template, user=self.args.username)

        try:
            res = self.cs.template_delete(t)

        except ServiceException as e:
            print(e)
            return 1

        print('info: template removed.')
        return 0

    def run_update(self):
        t = Template(self.args.template, user=self.args.username)

        try:
            t = self.cs.template_get(t, resolve_includes=False)

        except ServiceException as e:
            print(e)
            return 1

        # add template bits that are specified for update
        if self.args.title is not None:
            t.title = self.args.title

        if self.args.description is not None:
            t.description = self.args.description

        if self.args.includes is not None:
            t.includes = self.args.includes

        if self.args.public is not None:
            t.public = self.args.public

        try:
            res = self.cs.template_update(t)

        except ServiceException as e:
            print(e)
            return 1

        print('info: template updated.')
        return 0

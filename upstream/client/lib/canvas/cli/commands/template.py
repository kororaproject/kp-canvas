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
import sys
import random
import string
import subprocess
import yaml

from functools import reduce

from canvas.cli.commands import Command
from canvas.package import Package
from canvas.repository import Repository
from canvas.service import Service, ServiceException
from canvas.template import Template
from canvas.texttable import TextTable

logger = logging.getLogger('canvas')


class TemplateCommand(Command):
    def configure(self, config, args, args_extra, parsers):
        if args.action == None:
            parsers.template.print_help()
            sys.exit(1)

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

    def run(self):
        command = None

        # search for our function based on the specified action
        try:
            command = getattr(self, 'run_{0}'.format(self.args.action))

        except:
            self.help()
            return 1

        if not command:
            logging.error('Action is not reachable.')
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
            logging.exception(e)
            return 1

        logging.info('Template added.')
        return 0

    def run_copy(self):
        t = Template(self.args.template_from, user=self.args.username)

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            logging.exception(e)
            return 1

        # reparse for template destination
        t.parse(self.args.template_to)

        try:
            res = self.cs.template_create(t)

        except ServiceException as e:
            logging.exception(e)
            return 1

        logging.info('Template copied.')
        return 0

    def run_diff(self):
        t = Template(self.args.template_from, user=self.args.username)

        # grab the template we're pushing to
        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            logging.exception(e)
            return 1

        # fetch template to compare to
        if self.args.template_to is not None:
            ts = Template(self.args.template_to, user=self.args.username)

            try:
                ts = self.cs.template_get(ts)

            except ServiceException as e:
                logging.exception(e)
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
            logging.exception(e)
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
        print('TEMPLATE: {0} ({1})\n'.format(t.name, t.user))

        if t.description is not None and len(t.description):
            print('Description:\n{0}\n'.format(t.description))

        # pretty print includes
        if len(t.includes):
            l = TextTable(header=['INCLUDE'])
            for i in t.includes:
                l.add_row([i])

            print(l)
            print()

        # pretty print packages
        repos = list(t.repos_all)
        repos.sort(key=lambda x: x.stub)

        if len(repos):
            l = TextTable(header=["REPO", "NAME", "ENABLED"])

            for r in repos:
                cost = r.cost
                if cost is None:
                    cost = '-'

                priority = r.priority
                if priority is None:
                    priority = '-'

                enabled = 'N'
                if r.enabled:
                    enabled = 'Y'

                #l.add_row([r.stub, r.name, priority, cost, enabled])
                l.add_row([r.stub, r.name, enabled])

            print(l)
            print()

        # pretty print packages
        packages = list(t.packages_all)
        packages.sort(key=lambda x: x.name)

        if len(packages):
            l = TextTable(header=["PACKAGE", "ACTION", "TEMPLATE"])

            for p in packages:
                if p.included:
                    p.action = '+'

                elif p.excluded:
                    p.action = '-'

                elif p.ignored:
                    p.action = '!'

                else:
                    p.action = '?'

                # no template specified indicates it's part of this template
                if p.template == t.unv:
                    p.template = ''

                l.add_row([p.name, p.action, p.template])

            print(l)
            print()

        return 0

    def run_iso(self):

        t = Template(self.args.template, user=self.args.username)

        if self.args.use_livecd_creator:
            iso_creator = 'livecd-creator'
            install_package = 'livecd-tools'

        else:
            iso_creator = 'livemedia-creator'
            install_package = 'lorax'

        # check for required software
        try:
            subprocess.run([iso_creator, "--help"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        except FileNotFoundError:
            logging.error('You need to install the "{0}" package to create ISOs using {1}.'.format(install_package, iso_creator))
            return 1

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            logging.exception(e)
            return 1


        # calculate name and title for use if not specified
        arch = os.uname()[4]

        if arch in ['i386', 'i686']:
            arch_pretty = '32 bit'
            arch_pretty_long = '32 bit (%s)' % (arch)

        elif arch in ['x86_64']:
            arch_pretty = '64 bit'
            arch_pretty_long = '64 bit (%s)' % (arch)

        # we'll use the release version in our names
        if self.args.releasever is None:
            if t.version is None or t.version is '':
                # default to release ver of installed system at /
                self.args.releasever = dnf.rpm.detect_releasever('/')

            else:
                self.args.releasever = t.version

        name              = "{0}".format(t.name)
        name_long         = "{0}-{1}-{2}".format(t.name, self.args.releasever, arch)
        name_pretty       = "{0}-{1}-{2}".format(t.name, self.args.releasever, arch_pretty)
        title             = "{0}".format(t.title)
        title_long        = "{0} - {1} - {2}".format(t.title, self.args.releasever, arch_pretty)
        title_pretty_long = "{0} - {1} - {2}".format(t.title, self.args.releasever, arch_pretty_long)

        # build missing strings
        if self.args.build_dir is None:
            self.args.build_dir = "/var/tmp/canvas/{0}-{1}".format(name_long.lower(), t.uuid)

        tmp_dir = os.path.join(self.args.build_dir, 'tmp')

        if self.args.result_dir is None:
            self.args.result_dir = os.path.join(self.args.build_dir, 'iso')

        if self.args.cache_dir is None:
            self.args.cache_dir = os.path.join(self.args.build_dir, 'cache')

        if self.args.iso_name is None:
            self.args.iso_name = "{0}.iso".format(name_long.lower())

        if self.args.project is None:
            self.args.project = title_pretty_long

        if self.args.volid is None:
            self.args.volid = name_long.lower()

        if self.args.title is None:
            self.args.title = title

        if self.args.logfile is None:
            self.args.logfile = os.path.join(self.args.build_dir, "{0}.log".format(name_long.lower()))


        # build kickstart file
        ks_file = "canvas-{0}.ks".format(t.uuid)
        ks_path = os.path.join(self.args.build_dir, "ks", ks_file)

        try:
            # ensure our result_dir exists
            if not os.path.exists(os.path.dirname(ks_path)):
                os.makedirs(os.path.dirname(ks_path))

            with open(ks_path, 'w') as f:
                f.write(t.to_kickstart(resolved=True))

        except IOError as e:
            logging.error('You need root privileges to build iso at this location.')
            return 1

        env = os.environ.copy()

        logging.info('Build directory:  {0}'.format(self.args.build_dir))
        logging.info('Cache directory:  {0}'.format(self.args.cache_dir))
        logging.info('Result directory: {0}'.format(self.args.result_dir))
        logging.info('Log file:         {0}'.format(self.args.logfile))
        logging.info('ISO name:         {0}'.format(self.args.iso_name))

        logging.info('Project:          {0}'.format(self.args.project))
        logging.info('Title:            {0}'.format(self.args.title))
        logging.info('Volumne ID:       {0}'.format(self.args.volid))

        working_dir = None

        # livecd-creator
        if self.args.use_livecd_creator:
            logging.info('Building via livecd-creator ...')
            working_dir = self.args.result_dir

            args = [
                    iso_creator,
                    '--verbose',
                    '--config',     ks_path,
                    '--fslabel',    name_long.lower(),
                    '--title',      self.args.title,
                    '--releasever', self.args.releasever,
                    '--product',    self.args.project,
                    '--cache',      self.args.cache_dir,
                    '--tmpdir',     tmp_dir,
                    '--logfile',    self.args.logfile
                ]

            env["setarch"] = arch

        # livemedia-creator
        else:
            logging.info('Building via livemedia-creator ...')
            args = [
                    iso_creator,
                    '--no-virt',
                    '--make-iso',
                    '--iso-only',
                    '--macboot',
                    '--ks',         ks_path,
                    '--resultdir',  self.args.result_dir,
                    '--project',    self.args.project,
                    '--volid',      self.args.volid,
                    '--iso-name',   self.args.iso_name,
                    '--releasever', self.args.releasever,
                    '--title',      self.args.title,
                    '--logfile',    self.args.logfile
                ]

        logging.debug('Build args:', args)

        # ensure working directory exists if set
        if working_dir is not None:
            os.makedirs(working_dir, exist_ok=True)

        subprocess.run(args, cwd=working_dir, env=env)

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
            logging.exception(e)
            return 1

        if len(templates):
            l = TextTable(header=["[USER:]NAME", "TITLE"])

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
        if not self.args.dry_run and os.geteuid() != 0:
            logging.error('You need to have root privileges to modify the system.')
            return 0

        t = Template(self.args.template, user=self.args.username)

        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            logging.exception(e)
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

                if len(packages_install):
                    print('  - %d package(s) installed' % (len(packages_install)))

                if len(packages_remove):
                    print('  - %d package(s) removed' % (len(packages_remove)))

                print()

            else:
                print('No system changes required.')

            logging.info('No action peformed during this dry-run.')
            return 0

        t.system_apply()

    def run_push(self):
        t = Template(self.args.template, user=self.args.username)

        # grab the template we're pushing to
        try:
            t = self.cs.template_get(t)

        except ServiceException as e:
            logging.exception(e)
            return 1

        if self.args.push_clean:
            t.clear()

        if self.args.kickstart is not None:
            logging.info('Parsing kickstart ...')
            t.from_kickstart(self.args.kickstart)

        else:
            # prepare dnf
            logging.info('Analysing system ...')
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

            logging.info('No action peformed during this dry-run.')
            return 0

        if self.args.kickstart is None and not len(packages) and not len(repos):
            logging.info('No changes detected, template up to date.')
            return 0

        # push our updated template
        try:
            res = self.cs.template_update(t)

        except ServiceException as e:
            logging.exception(e)
            return 1

        logging.info('Template pushed.')
        return 0

    def run_rm(self):
        t = Template(self.args.template, user=self.args.username)

        try:
            res = self.cs.template_delete(t)

        except ServiceException as e:
            logging.exception(e)
            return 1

        logging.info('Template removed.')
        return 0

    def run_update(self):
        t = Template(self.args.template, user=self.args.username)

        try:
            t = self.cs.template_get(t, resolve_includes=False)

        except ServiceException as e:
            logging.exception(e)
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
            logging.exception(e)
            return 1

        logging.info('Template updated.')
        return 0

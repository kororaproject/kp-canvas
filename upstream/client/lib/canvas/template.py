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
import sys
import yaml

from canvas.package import Package, PackageSet
from canvas.repository import Repository, RepoSet

import pykickstart
import pykickstart.parser
from pykickstart.i18n import _
from pykickstart.version import DEVEL, makeVersion

#
# CLASS DEFINITIONS / IMPLEMENTATIONS
#


class Template(object):
    def __init__(self, template=None, user=None):
        self._name = None
        self._user = user
        self._uuid = None
        self._title = ''
        self._description = ''

        self._includes = []           # includes in template
        self._includes_resolved = []  # data structs for all includes in template
        self._meta = {}

        self._repos = RepoSet()           # repos in template
        self._includes_repos = RepoSet()  # repos from includes in template
        self._delta_repos = RepoSet()     # repos to add/remove in template

        self._packages = PackageSet()           # packages in template
        self._includes_packages = PackageSet()  # packages from includes in template
        self._delta_packages = PackageSet()     # packages to add/remove in template

        self._stores   = []  # remote stores for machine
        self._archives = []  # archive definitions in machine

        self._parse_template(template)

    def __str__(self):
        return 'Template: %s (owner: %s) - R: %d, P: %d' % (self._name, self._user, len(self.repos_all), len(self.packages_all))

    def _flatten(self):
        for tr in self._includes_resolved:
            t = Template(tr)

            self._includes_repos.update(t.repos_all)
            self._includes_packages.update(t.packages_all)

    def _parse_kickstart(self, path):
        """
        Loads the template with information from the supplied kickstart path.

        Kickstarts currently populate the meta tag, similar to the following:
          'kickstart': {
            'platform': '',
            'version':  'DEVEL',
            'language': 'en_US.UTF-8',
            'keyboard': 'us'
            'timezone': 'US/Eastern'
            'auth':     '--useshadow --passalgo=sha512
            'selinux':  '--enforcing'
            'firewall': '--enabled --service=mdns
            'xconfig':  '--startxonboot'
            'part':     '/ --size 4096 --fstype ext4',
            'services': '--enabled=NetworkManager,ModemManager --disabled=network,sshd'
            'commands': [
            ],
            'scripts': [
            ]
            'packages': [
            ]
          },
        }

        Args:
          path: Path to existing kickstart file.

        Returns:
          Nothing.

        Raises:
          IOError: An error occurred accessing the kickstart file.
        """

        ksversion = makeVersion(DEVEL)
        ksparser = pykickstart.parser.KickstartParser(ksversion)

        try:
            ksparser.readKickstart(path)

        except IOError as msg:
            print("Failed to read kickstart file '%(filename)s' : %(error_msg)s" % {"filename": path, "error_msg": msg}, file=sys.stderr)
            return

        except pykickstart.errors.KickstartError as e:
            print("Failed to parse kickstart file '%(filename)s' : %(error_msg)s" % {"filename": path, "error_msg": e}, file=sys.stderr)
            return

        handler = ksparser.handler

        meta = {}

        if handler.platform:
            meta['platform'] = handler.platform
            meta['version'] = versionToString(handler.version)

        lst = list(handler._writeOrder.keys())
        lst.sort()

        if len(lst):
            meta['commands'] = []
            for prio in lst:
                for c in handler._writeOrder[prio]:
                    # we don't store null commands (why pykickstart? why?)
                    if c.currentCmd == '':
                        continue

                    elif c.currentCmd == 'repo':
                        for r in c.__str__().split('\n'):
                            # ignore blank lines
                            if len(r.strip()) == 0:
                                continue

                            self._repos.add(Repository(r))

                    else:
                        meta['commands'].append({
                            'command':  c.currentCmd,
                            'priority': c.writePriority,
                            'data':     c.__str__()
                        })

        # parse pykickstart script
        if len(handler.scripts):
            meta['scripts'] = []

            for s in handler.scripts:
                meta['scripts'].append({
                    'data':          s.script,
                    'type':          s.type,
                    'interp':        s.interp,
                    'in_chroot':     s.inChroot,
                    'line_no':       s.lineno,
                    'error_on_fail': s.errorOnFail,
                })

        # parse pykickstart packages
        packages = handler.packages

        meta['packages'] = {
            'default':        packages.default,
            'exclude_docs':   packages.excludeDocs,
            'no_base':        not packages.addBase,
            'no_core':        packages.nocore,
            'handle_missing': (packages.handleMissing == pykickstart.constants.KS_MISSING_IGNORE),
            'install_langs':  packages.instLangs,
            'multi_lib':      packages.multiLib
        }

        if not packages.default:
            if packages.environment:
                meta['package']['environment'] = "@^{0}".format(packages.environment)

            grps = packages.groupList
            grps.sort()
            for g in grps:
                self._packages.add(Package({'n': g.__str__(), 'z': 1}))

            pkgs = packages.packageList
            pkgs.sort()
            for p in pkgs:
                self._packages.add(Package({'n': p.__str__(), 'z': 1}))

            grps = packages.excludedGroupList
            grps.sort()
            for g in grps:
                self._packages.add(Package({'n': g.__str__(), 'z': 0}))

            pkgs = packages.excludedList
            pkgs.sort()
            for p in pkgs:
                self._packages.add(Package({'n': p.__str__(), 'z': 0}))

        self._meta['kickstart'] = meta

    def _parse_template(self, template):
        # parse the string short form
        if isinstance(template, str):
            parts = template.split(':')

            if len(parts) == 1:
                self._name = parts[0]

            elif len(parts) == 2:
                self._user = parts[0]
                self._name = parts[1]

        # parse the dict form, the most common form and directly
        # relates to the json structures returned by canvas server
        elif isinstance(template, dict):
            self._uuid = template.get('uuid', None)
            self._user = template.get('user', template.get('username', None))
            self._name = template.get('stub', None)
            self._title = template.get('name', self._name)
            self._description = template.get('description', None)

            self._includes = template.get('includes', [])
            self._includes_resolved = template.get('includes_resolved', [])

            self._repos    = RepoSet(Repository(r) for r in template.get('repos', []))
            self._packages = PackageSet(Package(p) for p in template.get('packages', []))

            self._stores   = template.get('stores', [])
            self._archives = template.get('archives', [])

            self._meta = template.get('meta', {})

            # resolve includes
            self._flatten()

    #
    # PROPERTIES
    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        if value is None or len(str(value)) == 0:
            return

        self._description = str(value)

    @property
    def uuid(self):
        return self._uuid

    @property
    def includes(self):
        return self._includes

    @includes.setter
    def includes(self, value):
        if ',' in value:
            value = value.split(',')

        self._includes = value

    @property
    def name(self):
        return self._name

    @property
    def packages(self):
        return self._packages.union(self._delta_packages)

    @property
    def packages_all(self):
        return self._packages.union(self._includes_packages, self._delta_packages)

    @property
    def packages_delta(self):
        return self._delta_packages

    @property
    def public(self):
        return self._meta.get('public', False)

    @public.setter
    def public(self, state):
        if state:
            self._meta['public'] = True

        else:
            self._meta.pop('public', None)

    @property
    def repos(self):
        return self._repos.union(self._delta_repos)

    @property
    def repos_all(self):
        return self._repos.union(self._includes_repos).union(self._delta_repos)

    @property
    def repos_delta(self):
        return self._delta_repos

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value

    @property
    def user(self):
        return self._user

    #
    # PUBLIC METHODS
    def add_package(self, package):
        if package not in self.packages:
            self._delta_packages.add(package)

    def add_repo(self, repo):
        if not isinstance(repo, Repository):
            raise TypeError('Not a Repository object')

        if repo not in self.repos:
            self._delta_repos.add(repo)

    def find_package(self, name):
        return [p for p in self.packages if p.name == name]

    def find_repo(self, repo_id):
        return [r for r in self.repos if r.stub == repo_id]

    def from_kickstart(self, path):
        self._parse_kickstart(path)

    def from_system(self, all=False):
        db = dnf.Base()
        try:
            db.fill_sack()

        except OSError as e:
            pass

        if all:
            p_list = db.sack.query().installed()

        else:
            p_list = db.iter_userinstalled()

        for p in p_list:
            self.add_package(Package(p, evr=False))

        for r in db.repos.enabled():
            self.add_repo(Repository(r))

    def package_diff(self, packages):
        return self.packages_all.difference(packages)

    def parse(self, template):
        self._parse_template(template)

    def repo_diff(self, repos):
        return self.repos_all.difference(repos)

    def repos_to_repodict(self, cache_dir=None):
        rd = dnf.repodict.RepoDict()

        if cache_dir is None:
            cli_cache = dnf.conf.CliCache('/var/tmp')
            cache_dir = cli_cache.cachedir

        for r in self.repos_all:
            dr = r.to_repo(cache_dir)

            # load the repo
            dr.load()

            # add it to the dict
            rd.add(dr)

        return rd

    def remove_package(self, package):
        if not isinstance(package, Package):
            raise TypeError('Not a Package object')

        if package in self._delta_packages:
            self._packages.discard(package)
            return True

        elif package in self._packages:
            self._packages.discard(package)
            return True

        return False

    def remove_repo(self, repo):
        if not isinstance(repo, Repository):
            raise TypeError('Not a Repository object')

        if repo in self._delta_repos:
            self._delta_repos.remove(repo)
            return True

        elif repo in self._repos:
            self._repos.remove(repo)
            return True

        return False

    def to_json(self):
        return json.dumps(self.to_object(), separators=(',', ':'))

    def to_kickstart(self):
        """
        Represent the template as a kickstart file.

        Args:
          None

        Returns:
          Kickstart formatted file.
        """
        ksversion = makeVersion(DEVEL)
        ksparser = pykickstart.parser.KickstartParser(ksversion)

        handler = ksparser.handler
        packages = handler.packages

        if 'kickstart' in self._meta:
            # populate general

            # populate commands
            if 'commands' in self._meta['kickstart']:
                for c in self._meta['kickstart']['commands']:
                    ksparser.readKickstartFromString(c['data'], reset=False)

            # populate scripts
            if 'scripts' in self._meta['kickstart']:
                for s in self._meta['kickstart']['scripts']:
                    handler.scripts.append(
                        pykickstart.parser.Script(s['data'], interp=s['interp'], inChroot=s['in_chroot'], type=s['type'],
                            lineno=s['line_no'], errorOnFail=s['error_on_fail'])
                    )

            # populate general package parameters
            if 'packages' in self._meta['kickstart']:
                mp = self._meta['kickstart']['packages']

                if 'default' in mp:
                    packages.default = mp['default']

                if 'exclude_docs' in mp:
                    packages.excludeDocs = mp['exclude_docs']

                if 'no_base' in mp:
                    packages.addBase = not mp['no_base']

                if 'no_core' in mp:
                    packages.nocore = mp['no_core']

        #       if 'handle_missing' in mp:
        #           packages.handleMissing = pykickstart.constants.KS_MISSING_IGNORE

                if 'install_langs' in mp:
                    packages.instLangs = mp['install_langs']

                if 'multi_lib' in mp:
                    packages.multiLib = mp['multi_lib']

        # populate repos (technically commands)
        for r in self.repos:
            ksparser.readKickstartFromString(r.to_kickstart(), reset=False)

        # process packages
        for p in self.packages:
            if p.action == 1:
                packages.packageList.append(p.name)

            else:
                packages.excludedList.append(p.name)

        template = ('# Canvas generated template - {1}\n'
                    '# UUID: {0}\n'
                    '# Author: {2}\n'
                    '# Title: {3}\n'
                    '# Description:\n'
                    "# {4}\n\n").format(
                        self._uuid, self._name, self._user, self._title, self._description
                    )

        template += ksparser.handler.__str__()

        return template

    def to_object(self):
        # sort packages and repos
        packages = list(self.packages)
        packages.sort(key=lambda x: x.name)

        repos = list(self.repos)
        repos.sort(key=lambda x: x.stub)

        return {
            'uuid':        self._uuid,
            'name':        self._name,
            'user':        self._user,
            'title':       self._title,
            'description': self._description,
            'includes':    self._includes,
            'packages':    [p.to_object() for p in packages],
            'repos':       [r.to_object() for r in repos],
            'stores':      self._stores,
            'archives':    self._archives,
            'meta':        self._meta
        }

    def to_yaml(self):
        return yaml.dump(self.to_object())

    def update_package(self, package):
        if not isinstance(package, Package):
            raise TypeError('Not a Package object')

        if package in self._delta_packages:
            self._delta_packages.update(package)
            return True

        elif package in self._packages:
            self._packages.update(package)
            return True

        return False

    def update_repo(self, repo):
        if not isinstance(repo, Repository):
            raise TypeError('Not a Repository object')

        if repo in self._delta_repos:
            self._delta_repos.remove(repo)
            self._delta_repos.add(repo)
            return True

        elif repo in self._repos:
            self._repos.remove(repo)
            self._repos.add(repo)
            return True

        return False

    def union(self, template):
        if not isinstance(template, Template):
            TypeError('template is not of type Template')

        if self._name is None:
            self._name = template.name

        if self._user is None:
            self._user = template.user

        if self._description is None:
            self._description = template.description

        self._repos.update(template.repos)
        self._packages.update(template.packages)

class Machine(object):
    def __init__(self, machine=None, user=None, key=None):
        self._name        = None
        self._user        = user
        self._template    = None
        self._uuid        = None
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
            parts = machine.split(':')

            if len(parts) == 1:
                self._name = parts[0]

            elif len(parts) == 2:
                self._user = parts[0]
                self._name = parts[1]

        # parse the dict form, the most common form and directly
        # relates to the json structures returned by canvas server
        elif isinstance(machine, dict):
            self._uuid = machine.get('uuid', self._uuid)
            self._template = machine.get('template', self._template)
            self._user = machine.get('user', machine.get('username', None))
            self._name = machine.get('stub', self._name)
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

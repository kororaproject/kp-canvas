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
import hashlib
import json
import logging
import re
import sys
import yaml

from canvas.object import Object, ObjectSet
from canvas.package import Package, PackageSet
from canvas.repository import Repository, RepoSet

import pykickstart
import pykickstart.constants
import pykickstart.parser
from pykickstart.i18n import _
from pykickstart.version import DEVEL, makeVersion

from dnf.cli.progress import MultiFileProgressMeter

# [user:]name[@version]
RE_TEMPLATE = re.compile("(?:(?P<user>[\w\.\-]*):)?(?P<name>[\w\.\-]+)(?!.*:)(?:@(?P<version>[\w\.\-]+))?")

#
# CLASS DEFINITIONS / IMPLEMENTATIONS
#


class Template(object):
    def __init__(self, template=None, user=None):
        self._name = None
        self._user = user
        self._uuid = None
        self._version = None
        self._title = None
        self._description = None

        self._includes = []           # includes in template
        self._includes_resolved = []  # data structs for all includes in template
        self._meta = {}

        self._repos = RepoSet()           # repos in template
        self._includes_repos = RepoSet()  # repos from includes in template
        self._delta_repos = RepoSet()     # repos to add/remove in template

        self._packages = PackageSet()           # packages in template
        self._includes_packages = PackageSet()  # packages from includes in template
        self._delta_packages = PackageSet()     # packages to add/remove in template

        self._stores   = []           # remote stores for machine

        self._objects  = ObjectSet()           # archive definitions in machine
        self._includes_objects  = ObjectSet()  # archive definitions in machine
        self._delta_objects  = ObjectSet()     # archive definitions in machine

        self._db = None

        self._parse_template(template)

    def __str__(self):
        return 'Template: %s (owner: %s) - R: %d, P: %d' % (self._name, self._user, len(self.repos_all), len(self.packages_all))

    def _flatten(self):
        # iterate the includes in reverse order for packages and repos due to
        # higher level templates prioritising lower levels
        for t in reversed(self._includes_resolved):
            self._includes_repos.update(t.repos_all)
            self._includes_packages.update(t.packages_all)

        # iterate the includes in normal order for objects
        for t in reversed(self._includes_resolved):
            self._includes_objects.update(t.objects_all)

    def _parse_kickstart(self, path):
        """
        Loads the template with information from the supplied kickstart path.

        Kickstarts predominately populate the meta tag, similar to the following:
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
          },
        }

        Currently scripts are converted to canvas objects, repo commands are converted to canvas
        repos and packages are converted to canvas packages.

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
            logging.error("Failed to read kickstart file '{0}' : {1}".format(path, msg))
            return

        except pykickstart.errors.KickstartError as e:
            logging.error("Failed to parse kickstart file '{0}' : {1}".format(path, msg))
            return

        handler = ksparser.handler

        meta = {}

        if handler.platform:
            meta['platform'] = handler.platform
            meta['version'] = versionToString(handler.version)

        lst = list(handler._writeOrder.keys())
        lst.sort()

        for prio in lst:
            for c in handler._writeOrder[prio]:
                # we don't store null commands (why pykickstart? why?)
                if c.currentCmd.strip() == '':
                    continue

                # store repo commands as canvas templates
                elif c.currentCmd == 'repo':
                    for r in c.__str__().split('\n'):
                        # ignore blank lines
                        if len(r.strip()) == 0:
                            continue

                        self.add_repo(Repository(r))

                # otherwise store commands as canvas objects
                else:
                    self.add_object(Object(c))

        # convert scripts into canvas objects
        # sort on line number seen
        for s in sorted(handler.scripts, key=lambda x:x.lineno):
            self.add_object(Object(s))

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
                self.add_package(Package({'n': g.__str__(), 'z': 1}, template=self.unv))

            pkgs = packages.packageList
            pkgs.sort()
            for p in pkgs:
                self.add_package(Package({'n': p.__str__(), 'z': 1}, template=self.unv))

            grps = packages.excludedGroupList
            grps.sort()
            for g in grps:
                self.add_package(Package({'n': g.__str__(), 'z': 0}, template=self.unv))

            pkgs = packages.excludedList
            pkgs.sort()
            for p in pkgs:
                self.add_package(Package({'n': p.__str__(), 'z': 0}, template=self.unv))

        self._meta['kickstart'] = meta

    def _parse_template(self, template):
        # parse the string short form
        if isinstance(template, str):
            (user, name, version) = self._parse_unv(template)

            if user:
                self._user = user

            if name:
                self._name = name

            if version:
                self._version = version

            if not self._user or len(self._user) == 0:
                raise ValueError("template format invalid")

            if not self._name or len(self._name) == 0:
                raise ValueError("template format invalid")

        # parse the dict form, the most common form and directly
        # relates to the json structures returned by canvas server
        elif isinstance(template, dict):
            self._uuid = template.get('uuid', None)
            self._user = template.get('user', template.get('username', None))
            self._name = template.get('stub', None)
            self._version = template.get('version', None)
            self._title = template.get('name', self._name)
            self._description = template.get('description', None)

            self._includes = template.get('includes', [])

            self._repos    = RepoSet(Repository(r, template=self.unv) for r in template.get('repos', []))
            self._packages = PackageSet(Package(p, template=self.unv) for p in template.get('packages', []))

            self._stores   = template.get('stores', [])
            self._objects  = ObjectSet(Object(o) for o in template.get('objects', []))

            self._meta = template.get('meta', {})

    def _parse_unv(self, value):
        if isinstance(value, str):
            m = RE_TEMPLATE.match(value.strip())

            if m:
                return m.groups()

        return (None, None, None)

    def _unv_to_str(self, value):
        if isinstance(value, str):
            m = RE_TEMPLATE.match(value.strip())

            if m:
                (user, name, version) = m.groups()

                if user is None:
                    user = self._user

                if user and name and version:
                    return "{0}:{1}@{2}".format(user, name, version)
                elif user and name:
                    return "{0}:{1}".format(user, name)

        return None

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
    def includes(self):
        return self._includes

    @includes.setter
    def includes(self, value):
        # process string by splitting on `,`
        if isinstance(value, str):
            value = value.split(',')

        # return early if not dealing with a list from here
        if not isinstance(value, list):
            return

        includes = []
        includes_resolved = []

        for v in value:
            if isinstance(v, str):
                sv = self._unv_to_str(v)
                # attempt to sanitise the UNV string
                if sv is not None:
                    includes.append(sv)

            elif isinstance(v, Template):
                if v.unv is not None:
                    includes.append(v.unv)

                includes_resolved.append(v)

        if len(includes):
            self._includes = includes

        if len(includes_resolved):
            self._includes_resolved = includes_resolved

        # flatten template
        self._flatten()

    @property
    def name(self):
        return self._name

    @property
    def objects(self):
        return self._objects.union(self._delta_objects)

    @property
    def objects_all(self):
        # order is important
        return self._includes_objects.union(self._objects, self._delta_objects)

    @property
    def objects_delta(self):
        return self._delta_objects

    @property
    def packages(self):
        return self._packages.union(self._delta_packages)

    @property
    def packages_all(self):
        return self._packages.union(self._delta_packages, self._includes_packages)

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
        return self._repos.union(self._delta_repos, self._includes_repos)

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
    def unv(self):
        if self._user and self._name and self._version:
            return "{0}:{1}@{2}".format(self._user, self._name, self._version)
        elif self._user and self._name:
            return "{0}:{1}".format(self._user, self._name)

        return None

    @property
    def user(self):
        return self._user

    @property
    def uuid(self):
        return self._uuid

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
    def add_object(self, object):
        if not isinstance(object, Object):
            raise TypeError('Not an Object object')

        if object not in self.objects:
            self._delta_objects.add(object)

    def add_package(self, package):
        if package not in self.packages:
            self._delta_packages.add(package)

    def add_repo(self, repo):
        if not isinstance(repo, Repository):
            raise TypeError('Not a Repository object')

        if repo not in self.repos:
            self._delta_repos.add(repo)

    def clear(self):
        """
        Clears all includes, objects, packages, repos and stores from the
        template. Also removes all kickstart meta information.

        Args:
          None

        Returns:
          Nothing.
        """

        self._includes = []           # includes in template
        self._includes_resolved = []  # data structs for all includes in template
        self._repos = RepoSet()           # repos in template
        self._includes_repos = RepoSet()  # repos from includes in template
        self._delta_repos = RepoSet()     # repos to add/remove in template

        self._packages = PackageSet()           # packages in template
        self._includes_packages = PackageSet()  # packages from includes in template
        self._delta_packages = PackageSet()     # packages to add/remove in template

        self._stores   = []           # remote stores for machine

        self._objects  = ObjectSet()           # archive definitions in machine
        self._includes_objects  = ObjectSet()  # archive definitions in machine
        self._delta_objects  = ObjectSet()     # archive definitions in machine

        if 'kickstart' in self._meta:
            del self._meta['kickstart']


    def find_package(self, name):
        return [p for p in self.packages if p.name == name]

    def find_repo(self, repo_id):
        return [r for r in self.repos if r.stub == repo_id]

    def from_kickstart(self, path):
        self._parse_kickstart(path)

    @classmethod
    def from_system(cls, all=False):
        system_template = cls('local:system')
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
            system_template.add_package(Package(p, evr=False))

        for r in db.repos.enabled():
            system_template.add_repo(Repository(r))
        return system_template

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

    def remove_object(self, object):
        if not isinstance(object, Object):
            raise TypeError('Not an Object object')

        if object in self._delta_objects:
            self._objects.discard(object)
            return True

        elif object in self._objects:
            self._objects.discard(object)
            return True

        return False

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

    def system_apply(self, clean=True):
        """
        Applies the transaction (configured by prepare) to the system.

        Args:
          db: dnf.Base object to use for preparation.
          clean: specify wheter system packages not defined in the template are removed.

        Returns:
          Nothing.
        """

        if not isinstance(self._db, dnf.Base):
            return

        db = self._db

        if db.transaction is not None and \
            (len(db.transaction.install_set) or len(db.transaction.remove_set)):
            logging.info('Downloading packages ...')
            db.download_packages(list(db.transaction.install_set), progress=MultiFileProgressMeter())

            logging.info('Performing package transaction ...')
            db.do_transaction()

        if len(self.packages_all):
            logging.info('Syncing history ...')

            for p in self.packages_all:
                if p.included:
                    pkg = p.to_pkg();
                    if pkg is not None:
                        db.yumdb.get_package(pkg).reason = 'user'

        # check all non-ks objects
        if len(self.objects_all):
            # find all non local object sources and fetch
            external_sources = [o for o in self.objects_all if o.source != 'raw']

            if len(external_sources):
                logging.info('Downloading objects ...')

            for o in external_sources:
                logging.info('Downloading: {0}'.format(o.source))
                o.download()


            # apply non-ks actions only
            for o in self.objects_all:
                logging.info('Applying: {0}'.format(o.source))
                o.apply_actions()

    def system_prepare(self, clean=False, db=dnf.Base()):
        """
        Prepares the system for applying template configuration.

        Args:
          db: dnf.Base object to use for preparation.
          clean: specify wheter system packages not defined in the template are removed.

        Returns:
          Nothing.
        """

        if not isinstance(self._db, dnf.Base):
            self._db = db

        else:
            self._db.reset(goal=True, repos=True)

        # prepare dnf
        logging.info('Analysing system ...')

        # install repos from template
        if len(self.repos_all):
            for r in self.repos_all:
                dr = r.to_repo(conf=self._db.conf)
                dr.set_progress_bar(dnf.cli.progress.MultiFileProgressMeter())
                db.repos.add(dr)

        # indicate we're using sytem repos if we're mangling packages
        elif len(self.packages_all):
            logging.info('No template repos specified, using available system repos.')
            db.read_all_repos()

        db.read_comps()

        try:
            db.fill_sack()

        except OSError as e:
            pass

        q_installed = db.sack.query().installed()

        # check we have packages to assess
        if len(self.packages_all) == 0:
            return

        multilib_policy = db.conf.multilib_policy
        clean_deps = db.conf.clean_requirements_on_remove

        logging.info('Preparing package transaction ...')
        # process all packages in template
        for p in self.packages_all:
            # handle package groups
            if p.is_group:
                if p.included:
                    try:
                        db.group_install(p.name, 'default')

                    except:
                        logging.error('Package group does not exist {0}'.format(str(p)))

                elif p.excluded:
                    try:
                        db.group_remove(p.name)

                    except:
                        logging.debug('Package not installed: {0}'.format(str(p)))

            # handle packages
            else:
                p_spec = p.to_pkg_spec()

                # TODO: improve matching on all p_spec params (not just name)
                p_installed = list(q_installed.filter(name__glob=p_spec))

                if p.included and len(p_installed) == 0:
                    try:
                        db.install(p_spec)

                    except:
                        logging.error('Package does not exist {0}'.format(str(p)))

                elif p.excluded and len(p_installed) > 0:
                    try:
                        for pi in p_installed:
                            db.remove(pi)

                    except:
                        logging.debug('Package not installed: {0}'.format(str(p)))

                else:
                    pass

        logging.info('Resolving package actions ...')
        db.resolve(allow_erasing=True)

    def system_transaction(self):
        """
        System transaction that specifies all package installations and removals.

        Args:
          None

        Returns:
          dnf.Transaction

        Raises:
          IOError: An error occurred accessing the kickstart file.
        """

        if isinstance(self._db, dnf.Base):
            return self._db.transaction

        return None

    def to_json(self, resolved=False):
        return json.dumps(self.to_object(resolved=resolved), separators=(',', ':'))

    def to_kickstart(self, resolved=False):
        """
        Represent the template as a kickstart file.

        Args:
          None

        Returns:
          Kickstart formatted file.
        """

        if resolved:
            _packages = self.packages_all
            _repos    = self.repos_all
            _objects  = self.objects_all

        else:
            _packages = self.packages
            _repos    = self.repos
            _objects  = self.objects

        template = ('# Canvas generated template - {1}\n'
                    '# UUID: {0}\n'
                    '# Author: {2}\n'
                    '# Title: {3}\n'
                    '# Description:\n'
                    "# {4}\n\n").format(
                        self._uuid, self._name, self._user, self._title, self._description
                    )

        # populate repos (technically commands)
        # since repos commands have writePriority 0 we'll put them up top
        if len(_repos):
            for r in _repos:
                template += r.to_kickstart() + "\n"

            template += "\n"



        # first kickstart command seen has highest priority
        ks_commands = {}
        ks_commands_append = ['part', 'partition']

        # populate objects (ie ks specific commands)
        # first build a map of commands considering those that can be defined
        # multiple times
        for o in _objects:
            if o.is_ks_command():
                cmd = o.get_ks_command()
                if cmd in ks_commands_append:
                    ks_commands.setdefault(cmd, []).append(o)

                else:
                    ks_commands[cmd] = [o]

        # sort on priority order then add to template
        for oo in sorted(ks_commands.values(), key=lambda x: x[0].get_ks_command_priority()):
            for o in oo:
                template += o.to_kickstart() + "\n"

        # populate objects (ie ks-specific scripts)
        for o in _objects:
            if o.is_ks_script():
                template += o.to_kickstart() + "\n"

        # process packages
        if len(_packages) > 0:
            package_header = "%packages"

            mp = self._meta.get('kickstart', {}).get('packages', None)

            if mp is not None:
                if mp.get('exclude_docs', False):
                    package_header += ' --excludedocs'

                if mp.get('no_base', False):
                    package_header += ' --nobase'

                if mp.get('no_core', False):
                    package_header += ' --nocore'

                if mp.get('install_langs', False):
                    package_header += ' --installlangs'

                if mp.get('multi_lib', False):
                    package_header += ' --multilib'

                #if 'handle_missing' in mp:
                #    package_header += ' --handlemissing'


            template += package_header + "\n\n"

            packages_included = sorted([p.to_kickstart() for p in _packages if p.included])
            packages_excluded = sorted([p.to_kickstart() for p in _packages if not p.included])

            template += "\n".join(packages_included)
            template += "\n"
            template += "\n".join(packages_excluded)

            template += "\n%end\n"

        return template

    def to_object(self, resolved=False):
        if resolved:
            _packages = list(self.packages_all)
            _repos    = list(self.repos_all)
            _objects  = self.objects_all

        else:
            _packages = list(self.packages)
            _repos    = list(self.repos)
            _objects  = self.objects

        # sort packages and repos
        _packages.sort(key=lambda x: x.name)
        _repos.sort(key=lambda x: x.stub)

        # we don't sort objects as insertion order is important

        return {
            'uuid':        self._uuid,
            'name':        self._name,
            'user':        self._user,
            'version':     self._version,
            'title':       self._title,
            'description': self._description,
            'includes':    self._includes,
            'packages':    [p.to_object() for p in _packages],
            'repos':       [r.to_object() for r in _repos],
            'stores':      self._stores,
            'objects':     [o.to_object() for o in _objects],
            'meta':        self._meta
        }

    def to_yaml(self, resolved=False):
        return yaml.dump(self.to_object(resolved=resolved))

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

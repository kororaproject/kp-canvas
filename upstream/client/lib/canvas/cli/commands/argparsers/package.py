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

import argparse

def build(subparsers, **kwargs):

    package_parser = subparsers.add_parser(
        'package',
        description='Find, add and packages objects in templates.',
        help='Find, add and remove packages in templates.'
    )

    subparsers_package = package_parser.add_subparsers(
        dest='action',
        description='TODO'        
    )

    packages = argparse.ArgumentParser(add_help=False)
    packages.add_argument(
        'package',
        nargs='+',
        help='package name'
    )

    #
    # ADD ARGUMENTS
    #
    package_add_parser = subparsers_package.add_parser(
        'add',
        description='Add packages to a template.',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            packages
        ],
        help='add packages to a template'
    )
    package_add_parser.add_argument(
        '--with-deps',
        dest='with_deps',
        help='do not automatically remove dependencies'
    )

    #
    # UPDATE ARGUMENTS
    #
    package_update_parser = subparsers_package.add_parser(
        'update',
        description='Update packages in a template.',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            packages
        ],
        help='update packages to a template'
    )

    #
    # LIST ARGUMENTS
    #
    package_list_parser = subparsers_package.add_parser(
        'list',
        description='List packages in a template.',
        parents=[
            kwargs["output"],
            kwargs["template"],
            kwargs["connection_overrides"]
        ],
        help='list packages in a template'
    )

    #
    # REMOVE ARGUMENTS
    #
    package_remove_parser = subparsers_package.add_parser(
        'rm',
        description='Remove packages to a template.',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            packages
        ],
        help='remove packages to a template'
    )

    return package_parser

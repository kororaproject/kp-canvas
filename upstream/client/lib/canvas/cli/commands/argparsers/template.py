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
    template_parser = subparsers.add_parser(
        'template',
        description='List, create or delete templates.',
        help='List, create or delete templates.'
    )

    subparsers_template = template_parser.add_subparsers(
        dest='action',
        description=(
            'The following commands allow adding, removing, modifying, '
            'querying, and synchronising Canvas templates.'
        )
    )

    # common add/update arguments
    template_add_update_parser = argparse.ArgumentParser(add_help=False)
    template_add_update_parser.add_argument(
        '--title',
        help='define the pretty TITLE of template'
    )
    template_add_update_parser.add_argument(
        '--description',
        help='define descriptive TEXT of the template'
    )
    template_add_update_parser.add_argument(
        '--includes',
        #metavar='[user]:template[@version]',
        help='comma separated list of TEMPLATEs to include'
    )
    template_add_update_parser.add_argument(
        '--public',
        choices=['0', '1', 'false', 'true'],
        help='marks template as public if set to true'
    )

    #
    # ADD ARGUMENTS
    #
    template_add_parser = subparsers_template.add_parser(
        'add',
        description='Add a new Canvas template.',
        parents=[
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            template_add_update_parser
        ],
        help='add new template'
    )

    #
    # COPY ARGUMENTS
    #
    template_copy_parser = subparsers_template.add_parser(
        'copy',
        description='Copy an existing template to a new one.',
        parents=[
            kwargs["verbose"],
            kwargs["connection_overrides"],
        ],
        help='copy an existing template to a new one'
    )
    template_copy_parser.add_argument(
        'template_from',
        help='source template in the form [user:]template[@version]'
    )
    template_copy_parser.add_argument(
        'template_to',
        nargs='?',
        help=(
            'destination template in the form [user:]template[@version], '
            'if ommitted the destination template will retain the same '
            'name as the source template'
        )
    )

    #
    # DIFF ARGUMENTS
    #
    template_diff_parser = subparsers_template.add_parser(
        'diff',
        description=(
            'View the difference between existing templates '
            'and/or the current system configuration'
        ),
        parents=[
            kwargs["output"],
            kwargs["connection_overrides"]
        ],
        help='view differences between templates and/or the current system'
    )
    template_diff_parser.add_argument(
        'template_from',
        help='template in the form [user:]template[@version] to diff from'
    )
    template_diff_parser.add_argument(
        'template_to',
        nargs='?',
        help=(
            'template in the form [user:]template[@version] to diff to, '
            'if not supplied compare to the current system configuration'
        )
    )

    #
    # DUMP ARGUMENTS
    #
    template_dump_parser = subparsers_template.add_parser(
        'dump',
        description='Output the contents of a template.',
        parents=[
            kwargs["template"],
            kwargs["connection_overrides"],
        ],
        help='output the contents of a template'
    )
    template_dump_parser.add_argument(
        '--json',
        action='store_true',
        help='output the template in JSON'
    )
    template_dump_parser.add_argument(
        '--yaml',
        action='store_true',
        help='output the template in YAML'
    )
    template_dump_parser.add_argument(
        '--kickstart',
        action='store_true',
        help='output the template in kickstart file format'
    )
    template_dump_parser.add_argument(
        '--no-resolve-includes',
        action='store_true',
        dest='no_resolve_includes',
        help='do not resolve any template includes'
    )

    # ISO ARGUMENTS
    template_iso_parser = subparsers_template.add_parser(
        'iso',
        description='Build a Live ISO from a template.',
        parents=[
            kwargs["template"],
            kwargs["connection_overrides"]
        ],
        help='build a Live ISO from a template'
    )
    template_iso_parser.add_argument(
        '--project',
        help='substituted for @PROJECT@ in bootloader config files'
    )
    template_iso_parser.add_argument(
        '--volid',
        help='volume ID'
    )
    template_iso_parser.add_argument(
        '--logfile',
        help=(
            'name and path for primary logfile, other logs will be '
            'created in the same directory'
        )
    )
    template_iso_parser.add_argument(
        '--iso-name',
        dest='iso_name',
        help='filename of the resulting ISO'
    )
    template_iso_parser.add_argument(
        '--releasever',
        help='set the value of $releasever'
    )
    template_iso_parser.add_argument(
        '--title',
        help='substituted for @TITLE@ in bootloader config files'
    )
    template_iso_parser.add_argument(
        '--resultdir',
        help='directory to the resulting images and iso into'
    )
    template_iso_parser.add_argument(
        '--livecd-creator',
        action="store_true",
        dest='use_livecd_creator',
        help='use livecd-creator instead of default livemedia-creator'
    )

    # LIST ARGUMENTS
    template_list_parser = subparsers_template.add_parser(
        'list',
        description='List available Canvas templates.',
        parents=[
            kwargs["connection_overrides"]
        ],
        help='list templates'
    )
    template_list_parser.add_argument(
        'filter_user',
        nargs='?',
        help='list templates for the specified user only'
    )
    template_list_parser.add_argument(
        '--public',
        action='store_true',
        dest='public_only',
        help='only list public templates'
    )
    template_list_parser.add_argument(
        '--filter-name',
        dest='filter_name',
        metavar='NAME',
        help='list templates that match the specified name filter'
    )
    template_list_parser.add_argument(
        '--filter-description',
        dest='filter_description',
        metavar='STRING',
        help='list templates that match the specified description filter'
    )

    #
    # PULL ARGUMENTS
    #
    template_pull_parser = subparsers_template.add_parser(
        'pull',
        description='Apply a template to the local machine',
        parents=[
            kwargs["template"],
            kwargs["dry_run"],
            kwargs["connection_overrides"]
        ],
        help='apply a template to the local machine',
    )
    template_pull_parser.add_argument(
        '--clean',
        action='store_true',
        dest='pull_clean',
        help='remove local packages and repos not in the template'
    )

    #
    # PUSH ARGUMENTS
    #
    template_push_parser = subparsers_template.add_parser(
        'push',
        description='Synchronise templates on the server with local data.',
        parents=[
            kwargs["template"],
            kwargs["dry_run"],
            kwargs["connection_overrides"]
        ],
        help='synchronise templates on the server with local data'
    )
    template_push_parser.add_argument(
        '--all',
        action='store_true',
        dest='push_all',
        help='include all packages and repos not just those added by the user'
    )
    template_push_parser.add_argument(
        '--clean',
        action='store_true',
        dest='push_clean',
        help=(
            'delete repos, packages, and objects from the template before '
            'pushing the local machine state'
        )
    )
    template_push_parser.add_argument(
        '--kickstart',
        metavar='FILE',
        help='push the content of a kickstart file'
    )

    #
    # REMOVE ARGUMENTS
    #
    template_remove_parser = subparsers_template.add_parser(
        'rm',
        description='Remove a template.',
        parents=[
            kwargs["template"],
            kwargs["connection_overrides"]
        ],
        help='remove a template'
    )

    #
    # UPDATE ARGUMENTS
    #
    template_update_parser = subparsers_template.add_parser(
        'update',
        description='Update an existing Canvas template.',
        parents=[
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            template_add_update_parser
        ],
        help='update existing template'
    )

    return template_parser

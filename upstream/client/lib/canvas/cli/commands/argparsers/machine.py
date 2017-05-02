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
    machine_parser = subparsers.add_parser(
        'machine',
        description='List, create or delete machines.',
        help='List, create or delete machines.'
    )

    subparsers_machine = machine_parser.add_subparsers(
        dest='action',
        description='TODO: Description of machine commands goes here'
    )

    # common add/update arguments
    machine_add_update = argparse.ArgumentParser(add_help=False)
    machine_add_update.add_argument(
        '--title',
        help=''
    )
    machine_add_update.add_argument(
        '--description',
        help=''
    )

    machine = argparse.ArgumentParser(add_help=False)
    machine.add_argument(
        'machine',
        help=''
    )

    #
    # ADD ARGUMENTS
    #
    machine_add_parser = subparsers_machine.add_parser(
        'add',
        description='TODO',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["connection_overrides"],
            machine_add_update,
            machine,
            kwargs["template"],
        ],
        help='TODO'
    )

    #
    # UPDATE ARGUMENTS
    #
    machine_update_parser = subparsers_machine.add_parser(
        'update',
        description='TODO',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["connection_overrides"],
            machine_add_update,
            machine
        ],
        help='TODO'
    )
    machine_update_parser.add_argument(
        '--name',
        help='TODO'
    )
    machine_update_parser.add_argument(
        '--template',
        help='TODO'
    )

    #
    # LIST ARGUMENTS
    #
    machine_list_parser = subparsers_machine.add_parser(
        'list',
        description='TODO',
        parents=[
            kwargs["connection_overrides"],
        ]
    )
    machine_list_parser.add_argument(
        'filter_user',
        nargs='?',
        help='TODO'
    )
    machine_list_parser.add_argument(
        '--public',
        action='store_true',
        dest='public_only',
        help='TODO'
    )
    machine_list_parser.add_argument(
        '--filter-name',
        dest='filter_name',
        help='TODO'
    )
    machine_list_parser.add_argument(
        '--filter-description',
        dest='filter_description',
        help='TODO'
    )

    #
    # REMOVE ARGUMENTS
    #
    machine_remove_parser = subparsers_machine.add_parser(
        'rm',
        description='TODO',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["connection_overrides"],
            machine
        ],
        help='TODO'
    )

    #
    # DIFF ARGUMENTS
    #
    machine_diff_parser = subparsers_machine.add_parser(
        'diff',
        description='TODO',
        parents=[
            kwargs["connection_overrides"],
            machine
        ],
        help='TODO'
    )

    #
    # SYNC ARGUMENTS
    #
    machine_sync_parser = subparsers_machine.add_parser(
        'sync',
        description='TODO',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["connection_overrides"],
            machine
        ],
        help='TODO'
    )
    machine_sync_parser_group = machine_sync_parser.add_mutually_exclusive_group(
        required=True
    )
    machine_sync_parser_group.add_argument(
        '--pull',
        action='store_true',
        help='TODO'
    )
    machine_sync_parser_group.add_argument(
        '--push',
        action='store_true',
        help='TODO'
    )

    #
    # COMMAND ARGUMENTS
    #
    machine_command_parser = subparsers_machine.add_parser(
        'cmd',
        description='TODO',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["connection_overrides"],
            machine
        ],
        help='TODO'
    )
    machine_command_parser.add_argument(
        'cmd',
        help='TODO'
    )
    machine_command_parser.add_argument(
        'args',
        nargs='*',
        help='TODO'
    )

    return machine_parser

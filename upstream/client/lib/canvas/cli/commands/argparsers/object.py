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
    object_parser = subparsers.add_parser(
        'object',
        description='Find, add and remove objects in templates.',
        help='Find, add and remove objects in templates.'
    )

    subparsers_object = object_parser.add_subparsers(
        dest='action',
        description='TODO'
    )

    object_arg = argparse.ArgumentParser(add_help=False)
    object_arg.add_argument(
        'object',
        help='object identifier in the form [store:]object_name'
    )

    objects = argparse.ArgumentParser(add_help=False)
    objects.add_argument(
        'object',
        nargs='+',
        help='object identifiers in the form [store:]object_name'
    )

    #
    # ADD ARGUMENTS
    #
    object_add_parser = subparsers_object.add_parser(
        'add',
        description='Add an object to a template.',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            object_arg,
        ],
        help='add an object to a template'
    )
    object_add_data_parser = object_add_parser.add_mutually_exclusive_group(
        required=True
    )
    object_add_data_parser.add_argument(
        '--source',
        help='TODO'
    )
    object_add_data_parser.add_argument(
        '--data',
        help='TODO'
    )
    object_add_data_parser.add_argument(
        '--data-file',
        help='TODO'
    )
    object_add_parser.add_argument(
        '--xsum',
        help='TODO'
    )
    object_add_parser.add_argument(
        '--action',
        dest='actions',
        action='append',
        help='TODO'
    )

    #
    # UPDATE ARGUMENTS
    #
    object_update_parser = subparsers_object.add_parser(
        'update',
        description='Update an object in a template.',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            objects
        ],
        help='update objects in a template'
    )

    #
    # LIST ARGUMENTS
    #
    object_list_parser = subparsers_object.add_parser(
        'list',
        description='List objects in a template.',
        parents=[
            kwargs["template"],
            kwargs["connection_overrides"],
            kwargs["output"],
        ],
        help='list objects in a template.'
    )

    #
    # REMOVE ARGUMENTS
    #
    object_remove_parser = subparsers_object.add_parser(
        'rm',
        description='Remove objects from a template.',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            objects
        ],
        help='remove objects from a template'
    )

    return object_parser

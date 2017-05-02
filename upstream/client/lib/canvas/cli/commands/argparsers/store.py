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
    store_parser = subparsers.add_parser(
        'store',
        description='Find, add and remove stores in templates.',
        help='Find, add and remove stores in templates.'
    )

    subparsers_store = store_parser.add_subparsers(
        dest='action',
        description='TODO: Description of store commands goes here'
    )

    store= argparse.ArgumentParser(add_help=False)
    store.add_argument(
        'store',
        nargs='+',
        help='TODO'
    )


    #
    # ADD ARGUMENTS
    #
    store_add_parser = subparsers_store.add_parser(
        'add',
        description='TODO',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            store
        ],
        help='TODO'
    )
    store_add_parser.add_argument(
        '--with-deps',
    )

    #
    # UPDATE ARGUMENTS
    #
    store_update_parser = subparsers_store.add_parser(
        'update',
        description='TODO',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            store
        ],
        help='TODO'
    )

    #
    # LIST ARGUMENTS
    #
    store_list_parser = subparsers_store.add_parser(
        'list',
        description='TODO',
        parents=[
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
        ],
        help='TODO'
    )
    store_list_parser.add_argument(
        '--output',
        help=''
    )

    #
    # REMOVE ARGUMENTS
    #
    store_update_parser = subparsers_store.add_parser(
        'rm',
        description='TODO',
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            store
        ],
        help='TODO'
    )

    return store_parser

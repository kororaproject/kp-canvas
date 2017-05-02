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
    repo_parser = subparsers.add_parser(
        'repo',
        description='Find, add and remove repos in templates.',
        help='Find, add and remove repos in templates.'
    )

    subparsers_repo = repo_parser.add_subparsers(
        dest='action',
        description='TODO: Description of repo commands goes here'
    )

    # common args to add and update
    repo_add_update = argparse.ArgumentParser(add_help=False)
    repo_add_update.add_argument(
        'repo',
        help='TODO'
    )
    repo_add_update.add_argument(
        '--name',
        help='TODO'
    )
    repo_add_update.add_argument(
        '--cost',
        type=int,
        help='TODO',
    )
    repo_add_update.add_argument(
        '--baseurl',
        nargs='+',
        help='TODO'
    )
    repo_add_update.add_argument(
        '--enabled',
        choices=['0',
        '1',
        'false',
        'true'],
        help='TODO'
    )
    repo_add_update.add_argument(
        '--gpgkey',
        nargs='+',
        help='TODO'
    )
    repo_add_update.add_argument(
        '--metalink',
        nargs='+',
        help='TODO'
    )
    repo_add_update.add_argument(
        '--mirrorlist',
        nargs='+',
        help='TODO'
    )
    repo_add_update.add_argument(
        '--gpgcheck',
        type=bool,
        help='TODO'
    )
    repo_add_update.add_argument(
        '--priority',
        type=int,
        help='TODO'
    )
    repo_add_update.add_argument(
        '--exclude',
        nargs='+',
        help='TODO'
    )
    repo_add_update.add_argument(
        '--skip-if-unavailable',
        type=bool,
        dest='skip',
        help='TODO'
    )

    #
    # ADD ARGUMENTS
    #
    repo_add_parser = subparsers_repo.add_parser(
        'add',
        description="Add a repo to a template.",
                parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            repo_add_update
        ],
        help='add a repo to a template'
    )

    #
    # UPDATE ARGUMENTS
    #
    repo_add_parser = subparsers_repo.add_parser(
        'update',
        description="Update a repo in a template.",
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
            repo_add_update
        ],
        help='update a repo in a template'
    )
    
    #
    # LIST ARGUMENTS
    #
    repo_list_parser = subparsers_repo.add_parser(
        'list',
        description="List repos in a template.",
        parents=[
            kwargs["template"],
            kwargs["connection_overrides"],
        ],
        help='list a repos in a template'
    )

    #
    # REMOVE ARGUMENTS
    #
    repo_remove_parser = subparsers_repo.add_parser(
        'rm',
        description="Remove a repo from a template.",
        parents=[
            kwargs["dry_run"],
            kwargs["verbose"],
            kwargs["template"],
            kwargs["connection_overrides"],
        ],
        help='remove a repo from a template'
    )
    repo_remove_parser.add_argument(
        'repo',
        nargs='+',
        help='TODO'
    )

    return repo_parser

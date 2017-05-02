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

def build(subparsers, **kwargs):
    parser = subparsers.add_parser(
        'config',
        description='Get and set configuration elements.',
        help='Get and set configuration elements.'
    )
    parser.add_argument(
        '--unset',
        action='store_true',
        help='remove the item from the configuration'
    )
    parser.add_argument(
        'name',
        metavar='option.name',
        help='configuration section and the key separated by a dot'
    )
    parser.add_argument(
        'value',
        nargs='?',
        help='value to set option.name to'
    )

    return parser

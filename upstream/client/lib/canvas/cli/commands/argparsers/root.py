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
import os

PROG_VERSION = '1.0'
PROG_NAME = 'Canvas'

def build(config, **kwargs):
    parser = argparse.ArgumentParser(
        prog='canvas',
        parents=[kwargs["connection_overrides"]],
        description=(
            'Canvas simplifies the composition, distribution '
            'and management of customised Korora (and Fedora) systems.'
        )
    )

    parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0} - {1}'.format(PROG_NAME, PROG_VERSION)
    )

    return parser

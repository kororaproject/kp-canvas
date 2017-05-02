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

import argcomplete
import argparse
import logging
import os
import sys

import canvas.cli.commands.argparsers.root
import canvas.cli.commands.argparsers.config
import canvas.cli.commands.argparsers.template
import canvas.cli.commands.argparsers.store
import canvas.cli.commands.argparsers.object
import canvas.cli.commands.argparsers.package
import canvas.cli.commands.argparsers.repo
import canvas.cli.commands.argparsers.machine

# set default log level
if os.environ.get('CANVAS_DEBUG', '0').lower() in ('1', 'true'):
    logging.basicConfig(level=logging.DEBUG)

else:
    logging.basicConfig(level=logging.INFO)

#PROG_VERSION = '1.0'
#PROG_NAME = 'Canvas'

CANVAS_HOST = 'https://canvas.kororaproject.org'
# CANVAS_HOST='http://localhost:3000'

# establish invoking user
CANVAS_USER = os.environ.get('SUDO_USER', os.getlogin())

class LogFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno in (logging.WARNING, logging.ERROR, logging.CRITICAL):
            record.msg = '[%s] %s' % (record.levelname, record.msg)

        return super(LogFormatter, self).format(record)

def buildCommandLineParser(config):
    parsers = argparse.Namespace()

    #
    # Args that are seen more than once are generated here and given
    # as parents to each subparser as required. This ensures that args
    # usage is consistent across all commands
    #
    # N.B. Common is defined as having the same name or flags and help values.
    #

    connection_overrides = argparse.ArgumentParser(add_help=False)
    connection_overrides.add_argument(
        '-U', '--user',
        dest='username',
        metavar='ID',
        default=config.get('user', 'name', CANVAS_USER),
        help='username used to authenticate to the canvas server'
    )
    connection_overrides.add_argument(
        '-H', '--host',
        default=config.get('core', 'host', CANVAS_HOST),
        help='url of the canvas server'
    )

    verbose = argparse.ArgumentParser(add_help=False)
    verbose.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='more verbose output'
    )

    template = argparse.ArgumentParser(add_help=False)
    template.add_argument(
        'template',
        # For nicer output it would be useful to set metavar but it causes an
        # assertion error when the help string is being generated, due to
        # special handling of '[' and ']'
        #metavar='[user]:template[@version]',
        help='template identifier in the form [user:]template[@version]'
    )

    dry_run = argparse.ArgumentParser(add_help=False)
    dry_run.add_argument(
        '-n', '--dry-run',
        action='store_true',
        help='do not make any actual changes'
    )

    output = argparse.ArgumentParser(add_help=False)
    output.add_argument(
        '--output',
        metavar='PATH',
        help=(
            'save the output to a file in the specified path. '
            'If the file already exists, it will be replaced'
        )
    )

    #
    # ROOT
    #
    parsers.main = canvas.cli.commands.argparsers.root.build(
        config,
        connection_overrides=connection_overrides
    )

    # SUB COMMANDS
    subparsers = parsers.main.add_subparsers(
        dest='command',
        description=(
            'The Canvas cli provides a number of subcommands '
            'used to manage and manipulate templates'
        )
    )

    # CONFIG COMMANDS
    parsers.config = canvas.cli.commands.argparsers.config.build(
        subparsers,
        
    )

    # TEMPLATE COMMANDS
    parsers.template = canvas.cli.commands.argparsers.template.build(
        subparsers,
        output=output,
        dry_run=dry_run,
        verbose=verbose,
        template=template,
        connection_overrides=connection_overrides
    )

    # STORE COMMANDS
    parsers.store = canvas.cli.commands.argparsers.store.build(
        subparsers,
        dry_run=dry_run,
        verbose=verbose,
        template=template,
        connection_overrides=connection_overrides
    )

    # OBJECT COMMANDS
    parsers.object = canvas.cli.commands.argparsers.object.build(
        subparsers,
        output=output,
        dry_run=dry_run,
        verbose=verbose,
        template=template,
        connection_overrides=connection_overrides
    )

    # PACKAGE COMMANDS
    parsers.package = canvas.cli.commands.argparsers.package.build(
        subparsers,
        output=output,
        dry_run=dry_run,
        verbose=verbose,
        template=template,
        connection_overrides=connection_overrides
    )

    # REPO COMMANDS
    parsers.repo = canvas.cli.commands.argparsers.repo.build(
        subparsers,
        output=output,
        dry_run=dry_run,
        verbose=verbose,
        template=template,
        connection_overrides=connection_overrides
    )

    # MACHINE COMMANDS
    parsers.machine = canvas.cli.commands.argparsers.machine.build(
        subparsers,
        output=output,
        dry_run=dry_run,
        verbose=verbose,
        template=template,
        connection_overrides=connection_overrides
    )

    return parsers


def parseCommandLine(config):
    parsers = buildCommandLineParser(config)

    args = None
    args_extra = None

    argcomplete.autocomplete(parsers.main)
    args, args_extra = parsers.main.parse_known_args()

    return (parsers, args, args_extra)


def general_usage(prog_name='canvas'):
    return
    print("Usage: {0} [--version] [--help] [--verbose] <command> [<args>]\n"
          "\n"
          "The available canvas commands are:\n"
          "  template  List, create or delete templates\n"
          "  package   Find, add and remove packages in templates\n"
          "  repo      Find, add and remove repos in templates\n"
          "  store     Find, add and remove stores in templates\n"
          "  object    Find, add and remove objects in templates\n"
          "  machine   List, create or delete machines\n"
          "  config    Get and set configuration elements\n".format(prog_name))


class Command(object):
    def __init__(self, prog_name='canvas'):
        self.prog_name = prog_name

    def configure(self, config, args, args_extra):
        pass

    def help(self):
        pass

    def run(self):
        pass

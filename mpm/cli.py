#!/bin/env python
"""Command-line interface (CLI)


SCL <scott@rerobots.net>
Copyright (c) 2019 rerobots, Inc.
"""
from __future__ import absolute_import
from __future__ import print_function
import argparse
import sys

from .__init__ import __version__


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    argparser = argparse.ArgumentParser(description='package (skill) manager for Misty', add_help=False)
    argparser.add_argument('-h', '--help', dest='print_help',
                           action='store_true', default=False,
                           help='print this help message and exit')
    argparser.add_argument('-V', '--version', dest='print_version',
                           action='store_true', default=False,
                           help='print version number and exit.')

    subparsers = argparser.add_subparsers(dest='command')

    init_parser = subparsers.add_parser('init', help='create a new (empty) skill', add_help=False)
    init_parser.add_argument('NAME', help='name of the skill')
    init_parser.add_argument('-h', '--help', dest='print_init_help',
                             action='store_true', default=False,
                             help='print this help message and exit')

    build_parser = subparsers.add_parser('build', help='create bundle ready for upload to Misty robot', add_help=False)
    build_parser.add_argument('-h', '--help', dest='print_build_help',
                             action='store_true', default=False,
                             help='print this help message and exit')

    subparsers.add_parser('version', help='print version number and exit.', add_help=False)
    help_parser = subparsers.add_parser('help', help='print this help message and exit', add_help=False)
    help_parser.add_argument('help_target_command', metavar='COMMAND', type=str, nargs='?')

    # Workaround for Python 2.7 argparse, which does not accept empty COMMAND:
    # If `--help` or `-h` present and every argument before it begins with `-`,
    # then convert it to `help`.
    # If `-V` or `--version` present and every argument before it begins with `-`,
    # then convert it to `version.
    if sys.version_info.major < 3:
        try:
            ind = argv.index('--help')
        except ValueError:
            try:
                ind = argv.index('-h')
            except ValueError:
                ind = None
        if ind is not None:
            for k in range(ind):
                if argv[k][0] != '-':
                    ind = None
                    break
            if ind is not None:
                argv[ind] = 'help'
        try:
            ind = argv.index('--version')
        except ValueError:
            try:
                ind = argv.index('-V')
            except ValueError:
                ind = None
        if ind is not None:
            for k in range(ind):
                if argv[k][0] != '-':
                    ind = None
                    break
            if ind is not None:
                argv[ind] = 'version'

    args = argparser.parse_args(argv)
    if args.print_version or args.command == 'version':
        print(__version__)
        return 0

    if args.print_help or args.command is None or args.command == 'help':
        if hasattr(args, 'help_target_command') and args.help_target_command is not None:
            if args.help_target_command == 'init':
                init_parser.print_help()
            elif args.help_target_command == 'build':
                build_parser.print_help()
            else:
                print('Unrecognized command. Try `--help`.')
                return 1
        else:
            argparser.print_help()
        return 0

    if args.command == 'init':
        if args.print_init_help:
            init_parser.print_help()
            return 0
        skillmeta = {
            'Name': args.NAME,
        }
        # TODO

    elif args.command == 'build':
        if args.print_build_help:
            build_parser.print_help()
            return 0
        # TODO

    else:
        print('Unrecognized command. Try `--help`.')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

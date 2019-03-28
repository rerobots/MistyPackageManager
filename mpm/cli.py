#!/bin/env python
"""Command-line interface (CLI)


SCL <scott@rerobots.net>
Copyright (c) 2019 rerobots, Inc.
"""
from __future__ import absolute_import
from __future__ import print_function
import argparse
import glob
import json
import os
import os.path
import sys
import uuid
import zipfile

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

        # Preconditions
        skillmeta_path = os.path.join('src', '{}.json'.format(args.NAME))
        if os.path.exists(skillmeta_path):
            print('ERROR: cannot initialize '
                  'because path already exists: {}'.format(skillmeta_path))
            return 1
        mainjs_path = os.path.join('src', '{}.js'.format(args.NAME))
        if os.path.exists(mainjs_path):
            print('ERROR: cannot initialize '
                  'because path already exists: {}'.format(mainjs_path))
            return 1

        skillmeta = {
            'Name': args.NAME,
            'UniqueId': str(uuid.uuid4()),
            'Description': '',
            'StartupRules': ['Manual', 'Robot'],
            'Language': 'javascript',
            'BroadcastMode': 'verbose',
            'TimeoutInSeconds': 60,
            'CleanupOnCancel': True,
            'WriteToLog': False,
        }

        # Write results
        if not os.path.exists('src'):
            os.mkdir('src')
        with open(skillmeta_path, 'wt') as fp:
            json.dump(skillmeta, fp, indent=2)
        with open(mainjs_path, 'wt') as fp:
            pass

    elif args.command == 'build':
        if args.print_build_help:
            build_parser.print_help()
            return 0

        # Preconditions
        candidate_metafiles = glob.glob(os.path.join('src', '*.json'))
        candidate_metafiles += glob.glob(os.path.join('src', '*.JSON'))

        skillname = None
        for candidate_metafile in candidate_metafiles:
            candidate_skillname = os.path.basename(candidate_metafile)
            if candidate_skillname.endswith('.json') or candidate_skillname.endswith('.JSON'):
                candidate_skillname = candidate_skillname[:-len('.json')]
            else:
                continue
            candidate_mainjsfile = os.path.join('src', '{}.js'.format(candidate_skillname))
            if not os.path.exists(candidate_mainjsfile):
                candidate_mainjsfile = os.path.join('src', '{}.JS'.format(candidate_skillname))
                if not os.path.exists(candidate_mainjsfile):
                    continue
            skillname = candidate_skillname
            skillmeta_path = candidate_metafile
            mainjs_path = candidate_mainjsfile
            break
        if skillname is None:
            print('ERROR: no meta file found in src/')
            return 1

        zipout_path = '{}.zip'.format(skillname)
        if os.path.exists(zipout_path):
            print('WARNING: destination file {} already exits. overwriting...'.format(zipout_path))
        zp = zipfile.ZipFile(zipout_path, mode='w')
        zp.write(skillmeta_path, arcname='{}.json'.format(skillname))
        zp.write(mainjs_path, arcname='{}.js'.format(skillname))
        zp.close()

    else:
        print('Unrecognized command. Try `--help`.')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

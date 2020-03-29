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

# Backwards-compatibility with Python 2.7
try:
    input = raw_input
except NameError:
    pass

import requests

from .__init__ import __version__
from . import config


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

    init_help = 'create a new (empty) skill'
    init_parser = subparsers.add_parser('init', description=init_help, help=init_help, add_help=False)
    init_parser.add_argument('NAME', help='name of the skill')
    init_parser.add_argument('-h', '--help', dest='print_init_help',
                             action='store_true', default=False,
                             help='print this help message and exit')

    build_help = 'create bundle ready for upload to Misty robot'
    build_parser = subparsers.add_parser('build', description=build_help, help=build_help, add_help=False)
    build_parser.add_argument('-h', '--help', dest='print_build_help',
                             action='store_true', default=False,
                             help='print this help message and exit')

    clean_help = 'clean distribution files generated by `mpm build`'
    clean_parser = subparsers.add_parser('clean', description=clean_help, help=clean_help, add_help=False)
    clean_parser.add_argument('-h', '--help', dest='print_clean_help',
                              action='store_true', default=False,
                              help='print this help message and exit')

    config_help = 'manage local configuration'
    config_parser = subparsers.add_parser('config', description=config_help, help=config_help, add_help=False)
    config_parser.add_argument('-h', '--help', dest='print_config_help',
                               action='store_true', default=False,
                               help='print this help message and exit')
    config_parser.add_argument('--addr', dest='config_addr',
                               default=None, metavar='ADDRESS',
                               help='declare address of Misty robot')
    config_parser.add_argument('--ping', dest='config_ping',
                               action='store_true', default=False,
                               help='check that Misty robot can be reached')
    config_parser.add_argument('--rm', dest='delete_config',
                               action='store_true', default=False,
                               help='delete local configuration data')

    list_help = 'list skills currently on Misty robot'
    list_parser = subparsers.add_parser('list', description=list_help, help=list_help, add_help=False)
    list_parser.add_argument('-h', '--help', dest='print_list_help',
                              action='store_true', default=False,
                              help='print this help message and exit')

    upload_help = 'upload skill to Misty robot'
    upload_parser = subparsers.add_parser('upload', description=upload_help, help=upload_help, add_help=False)
    upload_parser.add_argument('-h', '--help', dest='print_upload_help',
                              action='store_true', default=False,
                              help='print this help message and exit')

    remove_help = 'remove skill from Misty robot'
    remove_parser = subparsers.add_parser('remove', description=remove_help, help=remove_help, add_help=False)
    remove_parser.add_argument('remove_ID', metavar='ID', default=None, nargs='?',
                               help=('uniqueId of skill to remove from robot; '
                                     'if none given, and only 1 skill is on robot, '
                                     'then remove it.'))
    remove_parser.add_argument('-h', '--help', dest='print_remove_help',
                               action='store_true', default=False,
                               help='print this help message and exit')

    mversion_help = 'print (YAML format) identifiers and version numbers of Misty robot and exit.'
    mversion_parser = subparsers.add_parser('mistyversion', description=mversion_help, help=mversion_help, add_help=False)
    mversion_parser.add_argument('-h', '--help', dest='print_mversion_help',
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
            elif args.help_target_command == 'clean':
                clean_parser.print_help()
            elif args.help_target_command == 'config':
                config_parser.print_help()
            elif args.help_target_command == 'list':
                list_parser.print_help()
            elif args.help_target_command == 'upload':
                upload_parser.print_help()
            elif args.help_target_command == 'remove':
                remove_parser.print_help()
            elif args.help_target_command == 'mistyversion':
                mversion_parser.print_help()
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

        # Write results
        if not os.path.exists('dist'):
            os.mkdir('dist')
        zipout_path = os.path.join('dist', '{}.zip'.format(skillname))
        if os.path.exists(zipout_path):
            print('WARNING: destination file {} already exists. overwriting...'.format(zipout_path))
        zp = zipfile.ZipFile(zipout_path, mode='w')
        zp.write(skillmeta_path, arcname='{}.json'.format(skillname))
        zp.write(mainjs_path, arcname='{}.js'.format(skillname))
        zp.close()

    elif args.command == 'clean':
        if args.print_clean_help:
            clean_parser.print_help()
            return 0
        for fname in glob.glob(os.path.join('dist', '*')):
            os.unlink(fname)
        os.rmdir('dist')

    elif args.command == 'config':
        if args.print_config_help:
            config_parser.print_help()
            return 0
        if args.delete_config:
            print('Do you want to delete all local configuration data? [y/N]')
            decision = input()
            if decision.lower() not in ['y', 'yes']:
                return 1
            try:
                config.delete()
            except Exception as e:
                print('Failed to remove configuration: {}'.format(e))
                return 1
            return 0

        cfg = config.load(init_if_missing=True)
        if args.config_addr:
            cfg['addr'] = args.config_addr
            config.save(cfg)
        if args.config_ping:
            addr = cfg.get('addr')
            if addr is None:
                print('ERROR: Misty address is not known!')
                print('add it using `mpm config --addr`')
                return 1
            if not addr.startswith('http'):
                addr = 'http://' + addr
            try:
                pong = requests.get(addr + '/api/battery').ok
            except requests.exceptions.ConnectionError:
                pong = False
            if pong:
                print('success!')
                return 0
            else:
                print('failed to ping the Misty robot!')
                return 1

        else:
            out = config.pprint(cfg)
            if len(out) == 0:
                print('(empty)')
            else:
                print(out)

    elif args.command == 'list':
        if args.print_list_help:
            list_parser.print_help()
            return 0
        cfg = config.load()
        addr = cfg.get('addr')
        if not addr.startswith('http'):
            addr = 'http://' + addr
        try:
            slist = requests.get(addr + '/api/skills').json()
        except requests.exceptions.ConnectionError:
            print('failed to connect to the Misty robot!')
            print('check connection with `mpm config --ping`')
            return 1
        if slist['status'] != 'Success':
            print('Misty returned failure status: {}'.format(slist['status']))
            return 1
        slist = slist['result']
        for skilldata in slist:
            print('{}  {}'.format(skilldata['uniqueId'], skilldata['name']))

    elif args.command == 'upload':
        if args.print_upload_help:
            upload_parser.print_help()
            return 0
        dist_files = glob.glob(os.path.join('dist', '*'))
        if len(dist_files) > 1:
            print('ERROR: more than one file under dist/')
            print('perhaps `mpm clean`, then `mpm build` again')
            return 1
        fp = open(dist_files[0], 'rb')
        cfg = config.load()
        addr = cfg.get('addr')
        if not addr.startswith('http'):
            addr = 'http://' + addr
        try:
            res = requests.request(method='POST', url=addr + '/api/skills', files={
                'File': (dist_files[0], fp, 'application/zip'),
                'ImmediatelyApply': (None, 'false'),
                'OverwriteExisting': (None, 'true'),
            })
        except requests.exceptions.ConnectionError:
            print('failed to connect to the Misty robot!')
            print('check connection with `mpm config --ping`')
            return 1
        fp.close()
        if not res.ok:
            print('failed to upload skill to robot')
            return 1
        print(res.text)

    elif args.command == 'remove':
        if args.print_remove_help:
            remove_parser.print_help()
            return 0
        cfg = config.load()
        addr = cfg.get('addr')
        if not addr.startswith('http'):
            addr = 'http://' + addr
        if args.remove_ID is None:
            try:
                slist = requests.get(addr + '/api/skills').json()
            except requests.exceptions.ConnectionError:
                print('failed to connect to the Misty robot!')
                print('check connection with `mpm config --ping`')
                return 1
            if slist['status'] != 'Success':
                print('Misty returned failure status: {}'.format(slist['status']))
                return 1
            slist = slist['result']
            if len(slist) == 0:
                print('no skills on the robot; nothing to remove.')
                return 1
            if len(slist) > 1:
                print('more than 1 skill on the robot!')
                print('specify which skill to remove explicitly in `mpm remove ID`')
                return 1
            remove_ID = slist[0]['uniqueId']
        else:
            remove_ID = args.remove_ID

        try:
            res = requests.delete(addr + '/api/skills?Skill={}'.format(remove_ID))
        except requests.exceptions.ConnectionError:
            print('failed to connect to the Misty robot!')
            print('check connection with `mpm config --ping`')
            return 1
        if not res.ok:
            print('failed to remove skill {} from robot'.format(remove_ID))
            return 1

    elif args.command == 'mistyversion':
        if args.print_mversion_help:
            mversion_parser.print_help()
            return 0
        cfg = config.load()
        addr = cfg.get('addr')
        if not addr.startswith('http'):
            addr = 'http://' + addr
        try:
            devinfo = requests.get(addr + '/api/device').json()
        except requests.exceptions.ConnectionError:
            print('failed to connect to the Misty robot!')
            print('check connection with `mpm config --ping`')
            return 1
        if devinfo['status'] != 'Success':
            print('Misty returned failure status: {}'.format(devinfo['status']))
            return 1
        devinfo = devinfo['result']
        print('sku:', devinfo['sku'])
        print('serial number:', devinfo['serialNumber'])
        print('robotId:', devinfo['robotId'])
        for k in ['robotVersion', 'sensoryServiceAppVersion', 'androidOSVersion', 'windowsOSVersion']:
            print('{}: {}'.format(k, devinfo[k]))
        hardware_info = devinfo['hardwareInfo']
        for k in hardware_info:
            print('{}:'.format(k))
            for subk in hardware_info[k]:
                print('    {}: {}'.format(subk, hardware_info[k][subk]))

    else:
        print('Unrecognized command. Try `--help`.')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

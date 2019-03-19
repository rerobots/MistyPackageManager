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

    argparser = argparse.ArgumentParser(description='package (skill) manager for Misty')
    argparser.add_argument('-V', '--version', dest='print_version',
                           action='store_true', default=False,
                           help='print version number and exit.')
    args = argparser.parse_args(argv)
    if args.print_version:
        print(__version__)
        return 0

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))

"""Routines for managing configurations


SCL <scott@rerobots.net>
Copyright (c) 2020 rerobots, Inc.
"""
import configparser
import os.path


def load(path=None, init_if_missing=False):
    if path is None:
        path = os.path.join(os.path.expanduser('~'), '.mistypackagemanager')
    if os.path.exists(path):
        cfg = configparser.ConfigParser()
        cfg.read(path)
    else:
        if not init_if_missing:
            raise ValueError('configuration file does not exist at {}'.format(path))
        cfg = configparser.ConfigParser()
        cfg['DEFAULT'] = dict()
        with open(path, 'wt') as fp:
            cfg.write(fp)
    return cfg['DEFAULT']


def pprint(cfg):
    """Create string that presents ("pretty prints") the configuration
    """
    out = ''
    addr = cfg.get('addr')
    if addr is not None:
        out += 'Misty robot address\t{}\n'.format(addr)
    return out

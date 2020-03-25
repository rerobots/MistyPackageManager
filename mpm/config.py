"""Routines for managing configurations


SCL <scott@rerobots.net>
Copyright (c) 2020 rerobots, Inc.
"""
import configparser
import os.path


def _path_or_default(path=None):
    if path is None:
        path = os.path.join(os.path.expanduser('~'), '.mistypackagemanager')
    return path


def load(path=None, init_if_missing=False):
    path = _path_or_default(path)
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


def save(cfg, path=None):
    path = _path_or_default(path)
    full_cfg = configparser.ConfigParser()
    full_cfg['DEFAULT'] = cfg
    with open(path, 'wt') as fp:
        full_cfg.write(fp)


def pprint(cfg):
    """Create string that presents ("pretty prints") the configuration
    """
    out = ''
    addr = cfg.get('addr')
    if addr is not None:
        out += 'Misty robot address\t{}\n'.format(addr)
    return out

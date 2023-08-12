#!/usr/bin/env python3

# Backup a list of remote git repositories

# SPDX-FileCopyrightText: © 2023 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later

import configargparse
import logging
import os
import subprocess
import sys


log = logging.getLogger(__name__)

def parse_args():
    prefix = '/usr'
    prog   = 'backup-git'
    p = configargparse.ArgParser(
            default_config_files=[f'{prefix}/lib/{prog}/config.ini',
                f'/etc/{prog}.ini', f'~/.config/{prog}.ini'])
    p.add('-c', '--config', is_config_file=True, help='config file')
    p.add('list', nargs=1, metavar='FILE.LST', help='List of repository urls')
    args = p.parse_args()
    args.list = args.list[0]
    return args


def backup(url):
    base = url[url.rindex('/')+1:]
    if not base.endswith('.git'):
        base += '.git'
    log.info(f'Backing up {url} to {base} ...')
    if os.path.exists(base):
        log.info(f'Refreshing {base} ...')
        t = os.getcwd()
        os.chdir(base)
        subprocess.run(['git', 'remote', 'update'], check=True)
        os.chdir(t)
    else:
        log.info(f'Cloning {url} ...')
        subprocess.run(['git', 'clone', '--mirror', url, base], check=True)


def main():
    log_format      = '%(asctime)s - %(levelname)-8s - %(message)s'
    log_date_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(format=log_format, datefmt=log_date_format,
                        level=logging.INFO)
    args = parse_args()
    r = 0
    for line in open(args.list):
        i = line.find('#')
        if i != -1:
            line = line[:i]
        line = line.strip()
        if not line:
            continue
        try:
            backup(line)
        except Exception as e:
            log.error(f'Failed to mirror {line}: {e}')
            r = 1
    log.info('done')
    return r


if __name__ == '__main__':
    sys.exit(main())



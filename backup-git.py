#!/usr/bin/env python3

# Backup a list of remote git repositories

# SPDX-FileCopyrightText: © 2023 Georg Sauthoff <mail@gms.tf>
# SPDX-License-Identifier: GPL-3.0-or-later

import configargparse
import github
import gitlab
import logging
import os
import pathlib
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
    p.add('--list', metavar='FILE.LST', help='List of repository urls')
    p.add('--gh-starred', metavar='USER', help='Backup all starred github repositories')
    p.add('--gl-starred', metavar='USER', help='Backup all starred gitlab repositories')
    args = p.parse_args()
    return args


def url2dir(url):
    url = url.strip()
    if not url:
        raise RuntimeError('Passed empty URL')
    s = url[url.index('//')+2:]
    if not s:
        raise RuntimeError('Passed empty URL RHS')
    xs = s.split('/')
    if any(not x for x in xs):
        raise RuntimeError(f'URL contains empty component: {url}')
    if any(x == '.' for x in xs):
        raise RuntimeError(f'URL contains . component: {url}')
    if any(x == '..' for x in xs):
        raise RuntimeError(f'URL contains .. component: {url}')
    if not xs[-1].endswith('.git'):
        xs[-1] += '.git'
    return pathlib.Path('/'.join(xs))

def backup(url):
    base = url2dir(url)
    log.info(f'Backing up {url} to {base} ...')
    if os.path.exists(base):
        log.info(f'Refreshing {base} ...')
        t = os.getcwd()
        os.chdir(base)
        subprocess.run(['git', 'remote', 'update'], check=True)
        os.chdir(t)
    else:
        log.info(f'Cloning {url} ...')
        os.makedirs(base.parent, exist_ok=True)
        subprocess.run(['git', 'clone', '--mirror', url, str(base)], check=True)

def backup_list(lst):
    log.info(f'Backing up repositories listed in {lst} ...')
    r = 0
    for line in open(lst):
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
    return r

def backup_gh_starred(user):
    log.info(f'Backing up github repositories starred by {user} ...')
    g = github.Github()
    x = 0
    for r in g.get_user(user).get_starred():
        if r.owner.login == user:
            continue
        url = r.clone_url
        try:
            backup(url)
        except Exception as e:
            log.error(f'Failed to mirror {url}: {e}')
            x = 1
    return x

def backup_gl_starred(user):
    log.info(f'Backing up gitlab repositories starred by {user} ...')
    gl = gitlab.Gitlab()
    u = gl.users.list(username=user)[0]
    x = 0
    for r in u.starred_projects.list(all=True, as_list=False):
        url = r.http_url_to_repo
        try:
            backup(url)
        except Exception as e:
            log.error(f'Failed to mirror {url}: {e}')
            x = 1
    return x

def main():
    log_format      = '%(asctime)s - %(levelname)-8s - %(message)s'
    log_date_format = '%Y-%m-%d %H:%M:%S'
    logging.basicConfig(format=log_format, datefmt=log_date_format,
                        level=logging.INFO)
    args = parse_args()
    r = 0
    if args.list:
        r = max(r, backup_list(args.list))
    if args.gh_starred:
        r = max(r, backup_gh_starred(args.gh_starred))
    if args.gl_starred:
        r = max(r, backup_gl_starred(args.gl_starred))

    log.info('done')
    return r


if __name__ == '__main__':
    sys.exit(main())



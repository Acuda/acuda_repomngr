#!./venv_acuda_repomngr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Björn Eistel
# Contact: <eistel@gmail.com>
#
# THIS SOURCE-CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED. IN NO  EVENT WILL THE AUTHOR BE HELD LIABLE FOR ANY DAMAGES ARISING FROM
# THE USE OF THIS SOURCE-CODE. USE AT YOUR OWN RISK.

import argparse

def get_arg_parser():
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('--cfile', default='/opt/acuda_repomngr/config.yaml', help='configuration file')
    parser.add_argument('-v', action="store_true", default=False, dest='verbose')
    parser.add_argument('--verbose', action="store_true", default=False, dest='verbose')

    sub_parser = parser.add_subparsers(help='section')

    dev_sub_parser = sub_parser.add_parser('dev', help='TBD')
    dev_sub_parser.set_defaults(section='dev')
    dev_sub_parser.add_argument('action', choices=('config', 'args'), help='TBD')

    deb_sub_parser = sub_parser.add_parser('deb', help='TBD')
    deb_sub_parser.set_defaults(section='deb')
    deb_sub_parser.add_argument('action', choices=('copy', 'build', 'delete'), help='TBD')

    repo_sub_parser = sub_parser.add_parser('repo', help='TBD')
    repo_sub_parser.set_defaults(section='repo')
    repo_sub_parser.add_argument('action', choices=('init', 'includeall', 'delete'), help='TBD')

    auto_sub_parser = sub_parser.add_parser('auto', help='TBD')
    auto_sub_parser.set_defaults(section='auto')
    auto_sub_parser.set_defaults(action='auto')

    return parser

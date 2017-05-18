#!/opt/acuda_repomngr/venv_acuda_repomngr/bin/python3
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Author: Björn Eistel
# Contact: <eistel@gmail.com>
#
# THIS SOURCE-CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED. IN NO  EVENT WILL THE AUTHOR BE HELD LIABLE FOR ANY DAMAGES ARISING FROM
# THE USE OF THIS SOURCE-CODE. USE AT YOUR OWN RISK.

import time

import sys

from acuda_repomngr.ConfigurationManager import ConfigurationManager

from acuda_repomngr.colors import ColorPrinter
from acuda_repomngr.ParserExecute import ParserExecute

import argparse

def get_arg_parser():
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('--cfile', default='~/PycharmProjects/acuda_repomngr/etc/acurep/configuration.yaml', help='configuration file')
    parser.add_argument('-v', action="store_true", default=False, dest='verbose', help="verbose output")
    parser.add_argument('--verbose', action="store_true", default=False, dest='verbose', help="verbose output")

    sub_parser = parser.add_subparsers(help='section')

    dev_sub_parser = sub_parser.add_parser('dev', help='TBD')
    dev_sub_parser.set_defaults(section='dev')
    dev_sub_parser.add_argument('action', choices=('config', 'args', 'cpconfig', 'pkg', 'reinstall'), help='TBD')

    deb_sub_parser = sub_parser.add_parser('deb', help='TBD')
    deb_sub_parser.set_defaults(section='deb')
    deb_sub_parser.add_argument('action', choices=('copy', 'build', 'delete'), help='TBD')

    repo_sub_parser = sub_parser.add_parser('repo', help='TBD')
    repo_sub_parser.set_defaults(section='repo')
    repo_sub_parser.add_argument('action', choices=('init', 'includeall', 'delete'), help='TBD')

    apt_sub_parser = sub_parser.add_parser('aptgen', help='generate apt configuration (/etc/apt/sources.lost.d/)')
    apt_sub_parser.set_defaults(section='aptgen')
    apt_sub_parser.add_argument('action', choices=('local',), help='TBD')

    auto_sub_parser = sub_parser.add_parser('auto', help='TBD')
    auto_sub_parser.set_defaults(section='auto')
    auto_sub_parser.set_defaults(action='auto')

    return parser


def main():
    parser = get_arg_parser()
    argparse_result = parser.parse_args(sys.argv[1:])
    ParserExecute.execute(parser, argparse_result)

    #parser = argparse.get_arg_parser()
    #argparse_result = parser.parse_args(sys.argv[1:])
    #ParserExecute.execute(parser, argparse_result)


    #cprint.rst().out('Bye now...')






if __name__ == '__main__':
    main()



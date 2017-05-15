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

from core import argparse
from core.ParserExecute import ParserExecute
import sys

def main():
    parser = argparse.get_arg_parser()
    argparse_result = parser.parse_args(sys.argv[1:])
    ParserExecute.execute(parser, argparse_result)

if __name__ == '__main__':
    main()



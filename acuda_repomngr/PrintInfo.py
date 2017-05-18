#!./venv_acuda_repomngr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Björn Eistel
# Contact: <eistel@gmail.com>
#
# THIS SOURCE-CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED. IN NO  EVENT WILL THE AUTHOR BE HELD LIABLE FOR ANY DAMAGES ARISING FROM
# THE USE OF THIS SOURCE-CODE. USE AT YOUR OWN RISK.

import traceback
from enum import IntEnum
import sys

from acuda_repomngr.colors import ColorPrinter
from acuda_repomngr.GenericContextManager import ContextManager

class PIL(IntEnum):
    ERROR = 0
    WARN = 1
    INFO = 2
    VERBOSE = 3
    DEBUG = 4

__PILCOLORS = {
    PIL.ERROR: ColorPrinter().cfg('r', st='bx'),
    PIL.WARN: ColorPrinter().cfg('y'),
    PIL.INFO: ColorPrinter(),
    PIL.VERBOSE: ColorPrinter().cfg('c'),
    PIL.DEBUG: ColorPrinter().cfg('g'),
}

def __init():
    pcm = ContextManager(section='PIL')
    if not hasattr(pcm, '_print_info_log_level'):
        pcm._print_info_log_level = PIL.DEBUG
__init()


def printf_info(fmt, *args, **kwargs):
    loglevel = PIL.INFO
    if isinstance(fmt, PIL):
        loglevel = fmt
        fmt = args[0]
        args = args[1:]

    s = fmt % args
    print_info(loglevel, s, **kwargs)

def printn_info(fmt, *args, **kwargs):
    loglevel = PIL.INFO
    if isinstance(fmt, PIL):
        loglevel = fmt
        fmt = args[0]
        args = args[1:]

    s = fmt.format(*args, **kwargs)
    print_info(loglevel, s, **kwargs)


def print_info(*args, **kwargs):
    sep = kwargs.get('sep', ' ')
    end = kwargs.get('end', '')
    indent = kwargs.get('indent', 0)
    #doPrint = kwargs.get('print', True)
    pilfmt = kwargs.get('pilfmt', '%s: %s')

    loglevel = PIL.INFO
    if isinstance(args[0], PIL):
        loglevel = args[0]
        args = args[1:]

    if loglevel > ContextManager(section='PIL')._print_info_log_level:
        return

    args = ['%s' % a for a in args]
    s = sep.join(args) + end
    #s = pilfmt % (loglevel, s)

    print(
        __PILCOLORS[loglevel].fmt('{!s:<12}'.format(str(loglevel)+':')),
        __PILCOLORS[loglevel].fmt('{}{!s:<12}'.format('    '*indent, s))
    )

    #if loglevel == PIL.ERROR:
    #    print(s, file=sys.stderr, flush=True)
    #else:
    #    print(s, flush=True)

def print_info_demo():
    for x in PIL:
        print_info(x, 'DEMOTEXT')

def print_exception(ex):
    print_info(PIL.ERROR, '| %s:' % type(ex).__name__, ex.__doc__)
    print_info(PIL.DEBUG, '| %s' % ex.args)
    print_info(PIL.DEBUG, '|', traceback.format_exc().replace('\n', '\n'+' '*13 + '| '))



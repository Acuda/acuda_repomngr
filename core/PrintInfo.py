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

from core.GenericContextManager import ContextManager

class PIL(IntEnum):
    ERROR = 0
    WARN = 1
    INFO = 2
    VERBOSE = 3
    DEBUG = 4


def __init():
    pcm = ContextManager(section='PIL')
    if not hasattr(pcm, '_print_info_log_level'):
        pcm._print_info_log_level = PIL.INFO
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
    doPrint = kwargs.get('print', True)
    pilfmt = kwargs.get('pilfmt', '%s: %s')

    loglevel = PIL.INFO
    if isinstance(args[0], PIL):
        loglevel = args[0]
        args = args[1:]


    if loglevel > ContextManager(section='PIL')._print_info_log_level:
        return

    args = ['%s' % a for a in args]
    s = sep.join(args) + end
    s = pilfmt % (PIL(loglevel), s)

    #ContextManager(section='gui').send_signal('print_info(QString)', s)
    #ContextManager(section='gui')._info.append(s)
    if doPrint: print(s)


def print_exception(ex):
    print_info(PIL.ERROR, '| %s:' % type(ex).__name__, ex.__doc__)
    print_info(PIL.DEBUG, '| %s' % ex.message)
    print_info(PIL.DEBUG, '|', traceback.format_exc().replace('\n', '\n| '))

def pop_info():
    gcm = ContextManager(section='PIL')
    return [gcm._info.pop(0) for _ in range(len(gcm._info))]


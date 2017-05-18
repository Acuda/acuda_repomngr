#!./venv_acuda_repomngr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Björn Eistel
# Contact: <eistel@gmail.com>
#
# THIS SOURCE-CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED. IN NO  EVENT WILL THE AUTHOR BE HELD LIABLE FOR ANY DAMAGES ARISING FROM
# THE USE OF THIS SOURCE-CODE. USE AT YOUR OWN RISK.

import os
import sys
import shutil
import subprocess

import yaml
from acuda_repomngr.PrintInfo import *
from acuda_repomngr.GenericContextManager import ContextManager
from acuda_repomngr.ConfigurationManager import FileName
from acuda_repomngr.ConfigurationManager import ConfigurationManager
from acuda_repomngr.ConfigurationManager import PackageEntry


class ParserExecute(object):
    @staticmethod
    def _resolve_callback_by_attr(attrnamelist):
        if not isinstance(attrnamelist, list):
            return ParserExecute._resolve_callback_name_by_attr([attrnamelist])
        cbname = '_'.join(['%s_%s' % (attrname, getattr(ContextManager().argparse_result, attrname))
                           for attrname in attrnamelist])
        return getattr(ParserExecute, cbname)

    @staticmethod
    def _check_argparse_result(parser, argparse_result):
        res = [argname in argparse_result for argname in ['section', 'action']]
        if not all(res):
            parser.print_usage()
            parser.exit(1)

    @staticmethod
    def execute(parser, argparse_result):
        ctx = ContextManager()
        ctx.verbose = argparse_result.verbose
        if ctx.verbose:
            ctx.PIL._print_info_log_level = PIL.VERBOSE
        ctx.argparse_result = argparse_result

        print_info(PIL.DEBUG, ('\n%s'%(' '*13)).join(['{:=^27}']*3).format('', '   START EXECUTION   ', ''))
        ParserExecute._check_argparse_result(parser, argparse_result)

        ctx.cm = ConfigurationManager()
        ctx.cm.load_configuration_file(FileName(argparse_result.cfile).fullfilename)
        ctx.cm.load_additional_configuration()

        try:
            fnccb = ParserExecute._resolve_callback_by_attr(['section', 'action'])
        except AttributeError as ex:
            print_exception(ex)
            exit(-1)

        try:
            fnccb()
        except Exception as ex:
            print_exception(ex)
            exit(-1)


    #############################
    #   S E C T I O N   D E V   #
    #############################

    @staticmethod
    def section_dev_action_config():
        pass

    @staticmethod
    def section_dev_action_args():
        pass

    @staticmethod
    def section_dev_action_cpconfig():
        pass

    @staticmethod
    def section_dev_action_pkg():

        width = 100
        lblwidth = 20
        cntwidth = width - lblwidth - 3
        c1 = c2 = c3 = 60

        cpl = ColorPrinter().cfg('c', st='bu')
        cps = ColorPrinter().cfg('m', st='b')

        ColorPrinter().cfg('g', st='b').out(('{:=^%d}' % width).format(''))
        for x in ContextManager().cm.packages:
            ColorPrinter().cfg('g', st='br').out(('{:^%d}' % width).format(x.identifier))
            ColorPrinter().cfg('g', st='b').out(('{:-^%d}' % width).format(''))

            print(cpl.fmt(('{:<%d}:' % lblwidth).format('src_relative_to')), x.src_relative_to)
            print(cpl.fmt(('{:<%d}:' % lblwidth).format('dst_relative_to')), x.dst_relative_to)

            print()
            cps.out('FILES:')
            for f, s, d in zip(x.files, x.src_files, x.dst_files):
                print(('    {:<%d}\n        SRC: {:<%d}\n        DST: {:<%d}' % (c1, c2, c3)).format(f, s, d))
            print()
            cps.out('LINKS:')
            print('    ', end='')
            ColorPrinter().cfg('r', st='b').out('TODO')
            print()

            ColorPrinter().cfg('g', st='b').out(('{:=^%d}' % width).format(''))

    #############################ß
    #   S E C T I O N   D E B   #
    #############################

    @staticmethod
    def _write_deb_control(package_yaml, dst_full_filename):
        pass

    @staticmethod
    def section_deb_action_copy():
        ctx = ContextManager()
        cm = ctx.cm
        assert(isinstance(cm, ConfigurationManager))

        print_info(PIL.DEBUG, 'DEB_BUILD_DIR:', cm.configuration.DEB_BUILD_DIR,
                   ColorPrinter().cfg('r', st='b').fmt('(not found)') if os.path.exists(cm.configuration.DEB_BUILD_DIR) else '')
        os.makedirs(cm.configuration.DEB_BUILD_DIR, exist_ok=True)



        for package in cm.packages:
            assert(isinstance(package, PackageEntry))
            print_info(ColorPrinter().cfg(st='b').fmt(package.identifier))
            package_directory = FileName(filename=package.identifier, basepath=cm.configuration.DEB_BUILD_DIR).fullfilename

            print_info(PIL.VERBOSE, 'performing self check...', indent=1)
            if not package.check():
                printf_info(PIL.WARN, 'self check failed, package skipped', indent=1)
                continue


            if os.path.exists(package_directory) and os.path.isdir(package_directory):
                printf_info(PIL.VERBOSE,
                            'directory for package %s already exists, removing\n\t-> %s',
                            package.identifier, package_directory)
                #FIXME: ENABLE -> #shutil.rmtree(dst_package_directory)




    @staticmethod
    def section_deb_action_build():
        pass


    @staticmethod
    def section_deb_action_delete():
        pass


    ###############################
    #   S E C T I O N   R E P O   #
    ###############################

    @staticmethod
    def section_repo_action_init():
        pass

    @staticmethod
    def section_repo_action_includeall():
        pass

    @staticmethod
    def section_repo_action_delete():
        pass


    ###############################
    #   S E C T I O N   A U T O   #
    ###############################

    @staticmethod
    def section_auto_action_auto():
        ParserExecute.section_deb_action_delete()
        ParserExecute.section_repo_action_delete()
        ParserExecute.section_deb_action_copy()
        ParserExecute.section_deb_action_build()
        ParserExecute.section_repo_action_init()
        ParserExecute.section_repo_action_includeall()

    ###########################################
    #   S E C T I O N   A P T - C O N F I G   #
    ###########################################

    @staticmethod
    def section_aptgen_action_local():
        pass




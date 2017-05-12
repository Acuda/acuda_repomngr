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

import yaml

from core.GenericContextManager import ContextManager
from core.PrintInfo import *


def load_configuration(filename):
    with open(filename, 'r') as f:
        raw_yaml = yaml.safe_load(f)
    ContextManager().raw_yaml = raw_yaml


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
        ParserExecute._check_argparse_result(parser, argparse_result)

        cm = ContextManager()
        cm.verbose = argparse_result.verbose
        if cm.verbose:
            cm.PIL._print_info_log_level = PIL.VERBOSE

        cm.argparse_result = argparse_result
        load_configuration(argparse_result.cfile)

        ParserExecute._resolve_callback_by_attr(['section', 'action'])()


    #############################
    #   S E C T I O N   D E V   #
    #############################

    @staticmethod
    def section_dev_action_config():
        import pprint
        pprint.pprint(ContextManager().raw_yaml)

    @staticmethod
    def section_dev_action_args():
        import pprint
        pprint.pprint(ContextManager().argparse_result)


    #############################
    #   S E C T I O N   D E B   #
    #############################

    @staticmethod
    def _write_deb_control(package_yaml, dst_full_filename):
        os.makedirs(os.path.dirname(dst_full_filename), exist_ok=True)

    @staticmethod
    def section_deb_action_copy():
        raw_yaml = ContextManager().raw_yaml

        deb_build_dir = raw_yaml['CONFIGURATION']['DEB_BUILD_DIR']
        os.makedirs(deb_build_dir, exist_ok=True)

        if not 'PACKAGES' in raw_yaml:
            print_info(PIL.ERROR, 'no configuration for packages found')
            exit(1)


        for package in raw_yaml['PACKAGES']:
            rel_path = package.get('RELATIVE_TO', '')

            package_name = package['PACKAGE_NAME']
            package_version = package['PACKAGE_VERSION']
            package_dir = '%s_%s' % (package_name, package_version)

            dst_package_directory = os.path.sep.join([deb_build_dir, package_dir])
            if os.path.exists(dst_package_directory) and os.path.isdir(dst_package_directory):
                printf_info(PIL.VERBOSE,
                            'directory for package %s with version %s already exists, removing\n\t-> %s',
                            package_name, package_version, dst_package_directory)
                shutil.rmtree(dst_package_directory)


            dst_package_control_filename = os.path.sep.join([dst_package_directory, 'DEBIAN', 'control'])
            ParserExecute._write_deb_control(package, dst_package_control_filename)


            for filepath in package['FILES']:
                src_full_file_path = os.path.sep.join([rel_path, filepath])
                dst_full_file_path = os.path.sep.join([deb_build_dir, package_dir, filepath])



                if os.path.isfile(src_full_file_path):
                    printf_info(PIL.VERBOSE,
                                'copy file \n\tFrom -> %s\n\tTo   -> %s',
                                src_full_file_path, dst_full_file_path)

                    os.makedirs(os.path.dirname(dst_full_file_path), exist_ok=True)
                    shutil.copyfile(src_full_file_path, dst_full_file_path, follow_symlinks=False)

                elif os.path.isdir(src_full_file_path):
                    printf_info(PIL.VERBOSE,
                                'copy directory \n\tFrom -> %s\n\tTo   -> %s',
                                src_full_file_path, dst_full_file_path)

                    shutil.copytree(src_full_file_path, dst_full_file_path, symlinks=True)
                else:
                    print_info(PIL.ERROR, 'unknown file type for filename: %s' % src_full_file_path)
                    exit(1)











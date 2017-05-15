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

        raw_yaml = ContextManager().raw_yaml
        template = raw_yaml['CONFIGURATION']['DEB_CONTROL_TEMPLATE']
        replacement = dict()
        replacement.update(raw_yaml['CONFIGURATION']['DEB_CONTROL_DEFAULTS'])
        replacement.update(raw_yaml['MAINTAINER']['default'])
        replacement.update(package_yaml)

        for key, value in replacement.items():
            placeholder = '${%s}' % key
            if placeholder in template:
                template = template.replace(placeholder, value)

        with open(dst_full_filename, 'w') as f:
            f.write(template)

    @staticmethod
    def section_deb_action_copy():
        raw_yaml = ContextManager().raw_yaml

        deb_build_dir = raw_yaml['CONFIGURATION']['DEB_BUILD_DIR']
        deb_build_dir = deb_build_dir.replace('~', os.environ.get('HOME', '~'))

        os.makedirs(deb_build_dir, exist_ok=True)

        if not 'PACKAGES' in raw_yaml:
            print_info(PIL.ERROR, 'no configuration for packages found')
            exit(1)


        for package in raw_yaml['PACKAGES']:
            src_rel_path = package.get('SRC_RELATIVE_TO', '')
            dst_rel_path = package.get('DST_RELATIVE_TO', '')

            package_name = package['PACKAGE_NAME']
            package_version = package['PACKAGE_VERSION']
            package_dir = '%s_%s' % (package_name, package_version)

            printf_info(PIL.INFO, 'copy files for %s ...' % package_name)

            dst_package_directory = os.path.sep.join([deb_build_dir, package_dir])
            if os.path.exists(dst_package_directory) and os.path.isdir(dst_package_directory):
                printf_info(PIL.VERBOSE,
                            'directory for package %s with version %s already exists, removing\n\t-> %s',
                            package_name, package_version, dst_package_directory)
                shutil.rmtree(dst_package_directory)


            dst_package_control_filename = os.path.sep.join([dst_package_directory, 'DEBIAN', 'control'])
            ParserExecute._write_deb_control(package, dst_package_control_filename)


            for filepath in package.get('FILES', list()):
                src_full_file_path = os.path.sep.join([src_rel_path, filepath]) if len(src_rel_path) else filepath
                src_full_file_path = src_full_file_path.replace('~', os.environ.get('HOME', '~'))
                dst_full_file_path = os.path.sep.join([deb_build_dir, package_dir, dst_rel_path, filepath])
                dst_full_file_path = dst_full_file_path.replace('~', os.environ.get('HOME', '~'))


                if not os.path.exists(src_full_file_path):
                    printf_info(PIL.ERROR,
                                'file does not exist, skip package, remove target package directory\n\t(%s)',
                                src_full_file_path)
                    shutil.rmtree(dst_package_directory)
                    break
                elif os.path.isfile(src_full_file_path):
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

            for link in package.get('LINKS', list()):
                full_pkg_filepath = os.path.sep.join([deb_build_dir, package_dir])
                link_target = link['TARGET']
                link_name = link['NAME']

                full_target_linkfilename = os.sep.join([full_pkg_filepath, link_name])
                os.makedirs(os.path.dirname(full_target_linkfilename), exist_ok=True)
                cmd = ['ln', '-s', link_target, full_target_linkfilename]

                msg = subprocess.check_output(cmd, cwd=full_pkg_filepath)
                print_info(PIL.INFO, msg.decode('utf-8').rstrip('\n'))
                print(cmd)

    @staticmethod
    def section_deb_action_build():
        raw_yaml = ContextManager().raw_yaml
        deb_build_dir = raw_yaml['CONFIGURATION']['DEB_BUILD_DIR']
        deb_build_dir = deb_build_dir.replace('~', os.environ.get('HOME', '~'))
        for entry in os.listdir(deb_build_dir):
            full_filename = os.path.sep.join([deb_build_dir, entry])
            if not os.path.isdir(full_filename) \
                    or os.path.islink(full_filename) \
                    or not 'DEBIAN' in os.listdir(full_filename):
                continue

            cmd = ['fakeroot', 'dpkg-deb', '--build', entry]
            #cmd = ['dpkg-deb', '--build', entry]
            msg = subprocess.check_output(cmd, cwd=deb_build_dir)
            print_info(PIL.INFO, msg.decode('utf-8').rstrip('\n'))


    @staticmethod
    def section_deb_action_delete():
        raw_yaml = ContextManager().raw_yaml
        deb_build_dir = raw_yaml['CONFIGURATION']['DEB_BUILD_DIR']
        deb_build_dir = deb_build_dir.replace('~', os.environ.get('HOME', '~'))
        if not os.path.isdir(deb_build_dir) or not os.path.exists(deb_build_dir):
            print_info(PIL.ERROR, 'DEB_BUILD_DIR is no directory!')
            exit(1)
        shutil.rmtree(deb_build_dir)


    ###############################
    #   S E C T I O N   R E P O   #
    ###############################

    @staticmethod
    def section_repo_action_init():
        raw_yaml = ContextManager().raw_yaml
        repo_build_dir = raw_yaml['CONFIGURATION']['REPO_BUILD_DIR']
        repo_build_dir = repo_build_dir.replace('~', os.environ.get('HOME', '~'))


        os.makedirs(os.path.sep.join([repo_build_dir, 'conf']), exist_ok=True)
        os.makedirs(os.path.sep.join([repo_build_dir, 'incoming']), exist_ok=True)

        template = raw_yaml['CONFIGURATION']['REPO_DISTRIBUTIONS_TEMPLATE']

        dst_full_filename = os.path.sep.join([repo_build_dir, 'conf', 'distributions'])
        with open(dst_full_filename, 'w') as f:
            f.write(template)

    @staticmethod
    def section_repo_action_includeall():
        raw_yaml = ContextManager().raw_yaml
        deb_build_dir = raw_yaml['CONFIGURATION']['DEB_BUILD_DIR']
        deb_build_dir = deb_build_dir.replace('~', os.environ.get('HOME', '~'))
        repo_build_dir = raw_yaml['CONFIGURATION']['REPO_BUILD_DIR']
        repo_build_dir = repo_build_dir.replace('~', os.environ.get('HOME', '~'))
        repo_codename = raw_yaml['CONFIGURATION']['REPO_CODENAME']

        for entry in os.listdir(deb_build_dir):
            deb_full_filename = os.path.sep.join([deb_build_dir, entry])
            if not os.path.isfile(deb_full_filename) or not deb_full_filename.endswith('.deb'):
                continue

            cmd = ['reprepro', 'includedeb', repo_codename, deb_full_filename]
            try:
                msg = subprocess.check_output(cmd, cwd=repo_build_dir)
            except subprocess.CalledProcessError:
                pass
            print_info(PIL.INFO, msg.decode('utf-8').rstrip('\n'))

    @staticmethod
    def section_repo_action_delete():
        raw_yaml = ContextManager().raw_yaml
        repo_build_dir = raw_yaml['CONFIGURATION']['REPO_BUILD_DIR']
        repo_build_dir = repo_build_dir.replace('~', os.environ.get('HOME', '~'))
        if not os.path.isdir(repo_build_dir) or not os.path.exists(repo_build_dir):
            print_info(PIL.ERROR, 'REPO_BUILD_DIR is no directory!')
            exit(1)
        shutil.rmtree(repo_build_dir)


    ###############################
    #   S E C T I O N   A U T O   #
    ###############################

    @staticmethod
    def section_auto_action_auto():
        #ParserExecute.section_deb_action_delete()
        #ParserExecute.section_repo_action_delete()
        ParserExecute.section_deb_action_copy()
        ParserExecute.section_deb_action_build()
        ParserExecute.section_repo_action_init()
        ParserExecute.section_repo_action_includeall()

    ###########################################
    #   S E C T I O N   A P T - C O N F I G   #
    ###########################################

    @staticmethod
    def section_aptgen_action_local():
        raw_yaml = ContextManager().raw_yaml
        template = raw_yaml['CONFIGURATION']['APT_LOCAL_TEMPLATE']
        replacement = dict()
        replacement.update(raw_yaml['CONFIGURATION'])

        for key, value in replacement.items():
            placeholder = '${%s}' % key
            if placeholder in template:
                template = template.replace(placeholder, value)

        template = template.replace('~', os.environ.get('HOME', '~'))
        print(template)

        filename = '/etc/apt/sources.list.d/acurep-local.list'
        with open(filename, 'w') as f:
            f.write(template)




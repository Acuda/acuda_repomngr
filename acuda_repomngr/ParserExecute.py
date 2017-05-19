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

    @staticmethod
    def _print_step_info(funcname):
        actionstring = ' '.join(funcname.upper().replace('_', ' ').split(' ')[1::2])
        print_info(ColorPrinter().cfg('g', st='br').fmt(' {:-^50} '.format(' PERFORM %s ' % actionstring)))

    #############################
    #   S E C T I O N   D E V   #
    #############################

    @staticmethod
    def section_dev_action_config():
        printf_info(PIL.ERROR, 'not yet supported')

    @staticmethod
    def section_dev_action_args():
        printf_info(PIL.ERROR, 'not yet supported')

    @staticmethod
    def section_dev_action_cpconfig():
        printf_info(PIL.ERROR, 'not yet supported')

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
    def _parse_tampleate(template, placeholder_data):
        for key, value in placeholder_data.items():
            placeholder = '${%s}' % key
            if placeholder in template:
                template = template.replace(placeholder, os.path.expanduser(value))
        print_info(PIL.DEBUG, 'creating from template:\n%s' % template.rstrip('\n'))
        return template

    @staticmethod
    def section_deb_action_copy():
        ParserExecute._print_step_info(sys._getframe().f_code.co_name)
        cm = ContextManager().cm
        assert(isinstance(cm, ConfigurationManager))

        print_info(PIL.DEBUG, 'DEB_BUILD_DIR:', cm.configuration.DEB_BUILD_DIR,
                   ColorPrinter().cfg('r', st='b').fmt('(not found)') if os.path.exists(cm.configuration.DEB_BUILD_DIR) else '')
        os.makedirs(cm.configuration.DEB_BUILD_DIR, exist_ok=True)


        for package in cm.packages:
            assert(isinstance(package, PackageEntry))
            print_info(ColorPrinter().cfg(st='b').fmt(package.identifier))
            package_directory = FileName(filename=package.identifier, basepath=cm.configuration.DEB_BUILD_DIR).fullfilename

            print_info(PIL.VERBOSE, 'performing self check ...', indent=1)
            if not package.check():
                printf_info(PIL.WARN, 'self check failed, package skipped', indent=1)
                continue

            if os.path.exists(package_directory) and os.path.isdir(package_directory):
                printf_info(PIL.VERBOSE, 'directory for package %s already exists, removing:', package.identifier, indent=1)
                printf_info(PIL.VERBOSE, '-> %s', package_directory, indent=2)
                shutil.rmtree(package_directory)

            template_content = ParserExecute._parse_tampleate(cm.configuration.DEB_CONTROL_TEMPLATE, package.package_dict)
            package_control_filename = os.path.sep.join([package_directory, 'DEBIAN', 'control'])
            os.makedirs(os.path.dirname(package_control_filename), exist_ok=True)
            with open(package_control_filename, 'w') as f:
                f.write(template_content)

            full_dst_filename = [FileName(filename=dstf, basepath=package_directory).fullfilename for dstf in package.dst_files]
            full_src_dst_filename_list = zip(package.src_files, full_dst_filename)
            for src, dst in full_src_dst_filename_list:
                if os.path.isfile(src):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    print_info(PIL.VERBOSE, 'copy file / link:', indent=2)
                    printf_info(PIL.VERBOSE, 'from: %s', src, indent=3)
                    printf_info(PIL.VERBOSE, '  to: %s', dst, indent=3)
                    shutil.copy2(src, dst, follow_symlinks=False)
                elif os.path.isdir(src):
                    print_info(PIL.VERBOSE, 'copy directory:', indent=2)
                    printf_info(PIL.VERBOSE, 'from: %s', src, indent=3)
                    printf_info(PIL.VERBOSE, '  to: %s', dst, indent=3)
                    shutil.copytree(src, dst, symlinks=True)
                else:
                    printf_info(PIL.ERROR, 'unknown file type for filename: %s', src, indent=2)


    @staticmethod
    def section_deb_action_build():
        ParserExecute._print_step_info(sys._getframe().f_code.co_name)

        cm = ContextManager().cm
        assert(isinstance(cm, ConfigurationManager))

        deb_build_dir = cm.configuration.DEB_BUILD_DIR

        for entry in os.listdir(deb_build_dir):
            print_info(ColorPrinter().cfg(st='b').fmt(entry))
            entry_filename = FileName(filename=entry, basepath=deb_build_dir).fullfilename
            package_control_filename = FileName(filename=os.path.sep.join(['DEBIAN', 'control']),
                                                basepath=entry_filename).fullfilename

            if os.path.isfile(entry_filename):
                continue

            if not os.path.exists(package_control_filename) or not os.path.isfile(package_control_filename):
                printf_info(PIL.WARN, 'no package_control_filename, package skipped', indent=1)
                continue

            cmd = cm.configuration.DEB_BUILD_COMMAND
            cmd.append(entry)
            msg = subprocess.check_output(cmd, cwd=deb_build_dir)
            print_info(PIL.VERBOSE, msg.decode('utf-8').rstrip('\n'), indent=1)


    @staticmethod
    def section_deb_action_delete():
        ParserExecute._print_step_info(sys._getframe().f_code.co_name)

        cm = ContextManager().cm
        assert(isinstance(cm, ConfigurationManager))

        deb_build_dir = cm.configuration.DEB_BUILD_DIR

        printf_info(PIL.INFO, 'try deleting DEB_BUILD_DIR:')
        printf_info(PIL.INFO, deb_build_dir, indent=1)

        if not os.path.isdir(deb_build_dir) \
           or not os.path.exists(deb_build_dir):
            print_info(PIL.WARN, 'DEB_BUILD_DIR not available, no directory or not valid!')
            return

        shutil.rmtree(deb_build_dir)


    ###############################
    #   S E C T I O N   R E P O   #
    ###############################

    @staticmethod
    def section_repo_action_init():
        ParserExecute._print_step_info(sys._getframe().f_code.co_name)

        cm = ContextManager().cm
        assert(isinstance(cm, ConfigurationManager))

        repo_build_dir = cm.configuration.REPO_BUILD_DIR

        repo_conf_dir = FileName(filename='conf', basepath=repo_build_dir).fullfilename
        os.makedirs(repo_conf_dir, exist_ok=True)
        os.makedirs(FileName(filename='incoming', basepath=repo_build_dir).fullfilename, exist_ok=True)

        template_content = cm.configuration.REPO_DISTRIBUTIONS_TEMPLATE
        repo_distributions_filename = FileName(filename='distributions', basepath=repo_conf_dir).fullfilename
        with open(repo_distributions_filename, 'w') as f:
            f.write(template_content)

        print_info('done')


    @staticmethod
    def section_repo_action_includeall():
        ParserExecute._print_step_info(sys._getframe().f_code.co_name)

        cm = ContextManager().cm
        assert(isinstance(cm, ConfigurationManager))

        deb_build_dir = cm.configuration.DEB_BUILD_DIR
        repo_build_dir = cm.configuration.REPO_BUILD_DIR

        for entry in os.listdir(deb_build_dir):
            entry_filename = FileName(filename=entry, basepath=deb_build_dir).fullfilename

            if not os.path.isfile(entry_filename) or not entry.endswith('.deb'):
                continue

            print_info(ColorPrinter().cfg(st='b').fmt(entry))

            cmd = ['reprepro', 'includedeb']
            cmd.append(cm.configuration.REPO_CODENAME)
            cmd.append(entry_filename)

            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=repo_build_dir)
            output, error = p.communicate()

            if output:
                print_info(PIL.INFO, output.decode('utf-8').rstrip('\n').replace('\n', '\n%s' % (' '*13)))

            if error:
                error_list = error.decode('utf-8').rstrip('\n').split('\n')
                print_info(PIL.ERROR, error_list[0])
                print_info(PIL.VERBOSE, ('\n%s' % (' '*13)).join(error_list[1:]))


    @staticmethod
    def section_repo_action_delete():
        ParserExecute._print_step_info(sys._getframe().f_code.co_name)

        cm = ContextManager().cm
        assert(isinstance(cm, ConfigurationManager))

        repo_build_dir = cm.configuration.REPO_BUILD_DIR
        repo_distributions_filename = os.path.sep.join([repo_build_dir, 'conf', 'distributions'])

        printf_info(PIL.INFO, 'try deleting REPO_BUILD_DIR:')
        printf_info(PIL.INFO, repo_build_dir, indent=1)

        if not os.path.isdir(repo_build_dir) \
           or not os.path.exists(repo_build_dir) \
           or not os.path.isfile(repo_distributions_filename) \
           or not os.path.exists(repo_distributions_filename):
            print_info(PIL.WARN, 'REPO_BUILD_DIR not available, no directory or not valid!')
            return

        shutil.rmtree(repo_build_dir)



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
        ParserExecute._print_step_info(sys._getframe().f_code.co_name)

        cm = ContextManager().cm
        assert(isinstance(cm, ConfigurationManager))

        template_content = ParserExecute._parse_tampleate(cm.configuration.APT_LOCAL_TEMPLATE, cm.configuration._data)
        apt_local_filename = '/etc/apt/sources.list.d/acurep-local.list'

        if not os.access(os.path.dirname(apt_local_filename), os.W_OK):
            printf_info(PIL.ERROR, 'insufficient permissions, file "%s" not writable', apt_local_filename)
            return

        with open(apt_local_filename, 'w') as f:
            f.write(template_content)

        print_info('done')

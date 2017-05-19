#!/opt/acuda_repomngr/venv_acuda_repomngr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Björn Eistel
# Contact: <eistel@gmail.com>
#
# THIS SOURCE-CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED. IN NO  EVENT WILL THE AUTHOR BE HELD LIABLE FOR ANY DAMAGES ARISING FROM
# THE USE OF THIS SOURCE-CODE. USE AT YOUR OWN RISK.

import yaml
import os

from pprint import pprint
from acuda_repomngr.PrintInfo import *

class FileName(object):

    def __init__(self, filename, basepath=None):
        self._filename = filename
        self._basepath = basepath

    @property
    def filename(self):
        return FileName.fix(self._filename)

    @property
    def fullfilename(self):
        ffn = os.path.sep.join([self._basepath, self._filename]) if not self._basepath is None else self._filename
        return FileName.fix(ffn)

    @staticmethod
    def fix(filename):
        filename = FileName.replace_special_chars(filename)
        return filename

    @staticmethod
    def replace_special_chars(filename):
        filename = os.path.expanduser(filename)
        filename = os.path.expandvars(filename)
        filename = os.path.normpath(filename)
        return filename


class PdoBase(object):
    BASENAME = None

    def __init__(self):
        if not hasattr(self, '_raw_data'):
            self._raw_data = dict()

    def update(self, src_dict, tgt_dict=None):
        assert isinstance(src_dict, dict)
        if tgt_dict is None:
            tgt_dict = self._raw_data

        for key, value in src_dict.items():
            if isinstance(value, dict):
                if key not in tgt_dict:
                    tgt_dict[key] = dict()
                self.update(value, tgt_dict[key])
            elif isinstance(value, list):
                if key not in tgt_dict:
                    tgt_dict[key] = list()
                tgt_dict[key].extend(value)

            else:
                tgt_dict[key] = value

    @property
    def _data(self):
        return self._raw_data[self.BASENAME]

    @property
    def _data_available(self):
        return self.BASENAME in self._raw_data


class ConfigurationPdo(PdoBase):
    BASENAME = 'CONFIGURATION'

    def __init__(self, other=None):
        super(self.__class__, self).__init__()
        if issubclass(self.__class__, other.__class__) \
        or other.__class__.__base__ == self.__class__.__base__:
            self.__dict__ = other.__dict__.copy()

    @property
    def CONFIGURATION_D_DIR(self):
        return FileName.fix(self._data['CONFIGURATION_D_DIR'])

    @property
    def MAINTAINER_D_DIR(self):
        return FileName.fix(self._data['MAINTAINER_D_DIR'])

    @property
    def PACKAGE_D_DIR(self):
        return FileName.fix(self._data['PACKAGE_D_DIR'])

    @property
    def DEB_BUILD_DIR(self):
        return FileName.fix(self._data['DEB_BUILD_DIR'])

    @property
    def DEB_BUILD_COMMAND(self):
        return self._data['DEB_BUILD_COMMAND'].split(' ')

    @property
    def DEB_CONTROL_TEMPLATE(self):
        return self._data['DEB_CONTROL_TEMPLATE']

    @property
    def DEB_CONTROL_DEFAULTS(self):
        return self._data.get('DEB_CONTROL_DEFAULTS', dict())

    @property
    def REPO_BUILD_DIR(self):
        return FileName.fix(self._data['REPO_BUILD_DIR'])

    @property
    def REPO_DISTRIBUTIONS_TEMPLATE(self):
        return self._data['REPO_DISTRIBUTIONS_TEMPLATE']

    @property
    def REPO_CODENAME(self):
        return self._data['REPO_CODENAME']

    @property
    def APT_LOCAL_TEMPLATE(self):
        return self._data['APT_LOCAL_TEMPLATE']


class MaintainerPdo(PdoBase):
    BASENAME = 'MAINTAINER'

    def __init__(self, other=None):
        super(self.__class__, self).__init__()
        if issubclass(self.__class__, other.__class__) \
        or other.__class__.__base__ == self.__class__.__base__:
            self.__dict__ = other.__dict__.copy()

    @property
    def DEFAULT(self):
        return self._data.get('DEFAULT', dict())


class PackagesPdo(PdoBase):
    BASENAME = 'PACKAGES'

    def __init__(self, other=None):
        super(self.__class__, self).__init__()
        if issubclass(self.__class__, other.__class__) \
        or other.__class__.__base__ == self.__class__.__base__:
            self.__dict__ = other.__dict__.copy()

    def __getitem__(self, dslice):
        if isinstance(dslice, slice):
            return [PackageEntry(self._create_updated_package_entry_dict(x)) for x in self._data[dslice]]
        else:
            return PackageEntry(self._create_updated_package_entry_dict(self._data[dslice]))

    def _create_updated_package_entry_dict(self, package_data_dict):
        package_dict_updated = dict()

        if ConfigurationPdo(self)._data_available:
            package_dict_updated.update(ConfigurationPdo(self).DEB_CONTROL_DEFAULTS)

        if MaintainerPdo(self)._data_available:
            package_dict_updated.update(MaintainerPdo(self).DEFAULT)

        package_dict_updated.update(package_data_dict)

        return package_dict_updated

    def __len__(self):
        return len(self._data)

    def remove_multiple_entries(self):
        #if not self._data_available:
        #    return
        seen = set()
        numPackages = len(self) - 1
        seen_twice = [(x, numPackages - idx) for idx, x in enumerate(self[::-1]) if x.identifier in seen or seen.add(x.identifier)]

        if not seen_twice:
            return

        # TODO: warn if duplicate is removed...
        pkgentry, idxlist = zip(*seen_twice)
        for idx in idxlist:
            self._data.pop(idx)


class PackageEntry(object):
    def __init__(self, package_dict):
        self.package_dict = package_dict

    @property
    def identifier(self):
        return '{name}_{version}'.format(name=self.name, version=self.version)

    @property
    def name(self):
        return self.package_dict['PACKAGE_NAME']

    @property
    def version(self):
        return self.package_dict['PACKAGE_VERSION']

    @property
    def src_relative_to(self):
        return FileName.fix(self.package_dict.get('SRC_RELATIVE_TO', '/'))

    @property
    def dst_relative_to(self):
        return FileName.fix(self.package_dict.get('DST_RELATIVE_TO', '/'))

    @property
    def files(self):
        return self.package_dict.get('FILES', list())

    @property
    def src_files(self):
        src_files = [FileName(filename=f, basepath=self.src_relative_to).fullfilename for f in self.files]
        return src_files

    @property
    def dst_files(self):
        dst_files = [FileName(filename=f, basepath=self.dst_relative_to).fullfilename for f in self.files]
        return dst_files

    def __eq__(self, other):
        return self.identifier == other.identifier

    def check(self):
        if len(self.src_files) == 0:
            return True

        existing = read_access = False
        filetype = 'unknown'
        for filename in self.src_files:
            cps = ColorPrinter().cfg('g')
            cpf = ColorPrinter().cfg('r', st='b')

            existing = os.path.exists(filename)
            read_access = os.access(filename, os.R_OK)

            filetype = 'unknown'
            if os.path.isdir(filename):
                filetype = 'directory'
            if os.path.islink(filename):
                filetype = 'link'
            if os.path.isfile(filename):
                filetype = 'file'

            print_info(
                PIL.VERBOSE, filename,
                filetype,
                cps.fmt('(%s)' % filetype) if filetype != 'unknown' else cpf.fmt('(%s)' % filetype),
                cps.fmt('(found)') if existing else cpf.fmt('(not found)'),
                cps.fmt('(readable)') if read_access else cpf.fmt('(not readable)'),
                indent=2
            )
        return existing and read_access and filetype != 'unknown'

class ConfigurationManager(object):
    def __init__(self):
        super(ConfigurationManager, self).__init__()
        self.base = PdoBase()
        self.configuration = ConfigurationPdo(self.base)
        self.maintainer = MaintainerPdo(self.base)
        self.packages = PackagesPdo(self.base)

    def load_configuration_file(self, filename):
        if isinstance(filename, str):
            with open(filename, 'r') as f:
                self.load_configuration_file(f)
            return

        yaml_raw = yaml.safe_load(filename)
        self.base.update(yaml_raw)
        self.packages.remove_multiple_entries()

    def load_configuration_directory(self, filename):
        conffile = os.listdir(filename)
        conffile.sort()
        for cfile in conffile:
            ffn = os.sep.join([filename, cfile])
            self.load_configuration_file(ffn)

    def load_additional_configuration(self):

        self.load_configuration_directory(self.configuration.CONFIGURATION_D_DIR)
        self.load_configuration_directory(self.configuration.PACKAGE_D_DIR)

if __name__ == '__main__':
    cm = ConfigurationManager()
    cm.load_configuration_file('/home/beistel/PycharmProjects/acuda_repomngr/config.yaml')
    cm.load_configuration_file('/home/beistel/PycharmProjects/acuda_repomngr/etc/acurep/packages.yaml')
    cm.load_configuration_directory('/home/beistel/PycharmProjects/acuda_repomngr/etc/acurep/packages.d')
    cm.load_configuration_directory('/home/beistel/PycharmProjects/acuda_repomngr/etc/acurep/configuration.d')

    #print('###', cm.configuration._raw_data.keys())
    #print('###', PackagesPdo(cm.configuration)._raw_data.keys())

    fmt = '{:.<20}: {}'
    for x in cm.packages:
        print(x.identifier)
        print(fmt.format('src_relative_to', x.src_relative_to))
        print(fmt.format('dst_relative_to', x.dst_relative_to))
        print(x.files)
        print(x.src_files)
        print(x.dst_files)
        print('---')



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

class PdoBase(object):
    BASENAME = None

    def __init__(self):
        if not hasattr(self, 'raw_data'):
            self.raw_data = dict()

    def update(self, src_dict, tgt_dict=None):
        assert isinstance(src_dict, dict)
        if tgt_dict is None:
            tgt_dict = self.raw_data

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
        #print(self.BASENAME, self.raw_data)
        return self.raw_data[self.BASENAME]



class ConfigurationPdo(PdoBase):
    BASENAME = 'CONFIGURATION'

    def __init__(self, other=None):
        super(self.__class__, self).__init__()
        if issubclass(self.__class__, other.__class__) \
        or other.__class__.__base__ == self.__class__.__base__:
            self.__dict__ = other.__dict__.copy()

    @property
    def DEB_BUILD_DIR(self):
        return self._data['DEB_BUILD_DIR']

    @property
    def DEB_CONTROL_TEMPLATE(self):
        return self._data['DEB_CONTROL_TEMPLATE']

    @property
    def DEB_CONTROL_DEFAULTS(self):
        return self._data['DEB_CONTROL_DEFAULTS']

    @property
    def REPO_BUILD_DIR(self):
        return self._data['REPO_BUILD_DIR']

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
        return self._data['DEFAULT']


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
        package_dict_updated.update(ConfigurationPdo(self).DEB_CONTROL_DEFAULTS)
        package_dict_updated.update(MaintainerPdo(self).DEFAULT)
        package_dict_updated.update(package_data_dict)
        return package_dict_updated

    def __len__(self):
        return len(self._data)

    def remove_multiple_entries(self):
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

    def __eq__(self, other):
        return self.identifier == other.identifier

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
        for cfile in conffile:
            ffn = os.sep.join([filename, cfile])
            self.load_configuration_file(ffn)



if __name__ == '__main__':
    cm = ConfigurationManager()
    cm.load_configuration_file('/home/beistel/PycharmProjects/acuda_repomngr/config.yaml')
    cm.load_configuration_directory('/home/beistel/PycharmProjects/acuda_repomngr/etc/packages.d')

    #print('###', cm.configuration.raw_data.keys())
    #print('###', PackagesPdo(cm.configuration).raw_data.keys())

    pprint([x.identifier for x in cm.packages])



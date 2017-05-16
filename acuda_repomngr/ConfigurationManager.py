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



class PdoBase(object):
    def __init__(self):
        super(PdoBase, self).__init__()
        self.data = dict()

    def load_dict(self, data):
        self.data.update(data)

class ConfigurationPdo(PdoBase):
    BASENAME = 'CONFIGURATION'

    def __init__(self):
        super(ConfigurationPdo, self).__init__()

    def load_dict(self, data):
        assert isinstance(data, dict)
        data = data.get(self.BASENAME, dict())
        super(ConfigurationPdo, self).load_dict(data)

class MaintainerPdo(PdoBase):
    BASENAME = 'MAINTAINER'

    def __init__(self):
        super(MaintainerPdo, self).__init__()

    def load_dict(self, data):
        assert isinstance(data, dict)
        data = data.get(self.BASENAME, dict())
        super(MaintainerPdo, self).load_dict(data)

class PackagesPdo(PdoBase):
    BASENAME = 'PACKAGES'

    def __init__(self):
        super(PackagesPdo, self).__init__()

    def load_dict(self, data):
        assert isinstance(data, dict)
        data = data.get(self.BASENAME, dict())
        super(PackagesPdo, self).load_dict(data)

class ConfigurationManager(object):
    def __init__(self):
        super(ConfigurationManager, self).__init__()
        self.configuration = ConfigurationPdo()
        self.maintainer = MaintainerPdo()
        self.packages = PackagesPdo()


    def parse_configuration_file(self, filename):
        if isinstance(filename, str):
            with open(filename, 'r') as f:
                self.parse_configuration_file(f)
            return

        yaml_raw = yaml.safe_load(filename)
        self.configuration.load_dict(yaml_raw)
        self.maintainer.load_dict(yaml_raw)
        self.packages.load_dict(yaml_raw)





if __name__ == '__main__':
    cm = ConfigurationManager()
    cm.parse_configuration_file('/home/beistel/PycharmProjects/acuda_repomngr/config.yaml')

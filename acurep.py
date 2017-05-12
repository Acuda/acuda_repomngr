#!virtenv_acuda_repomngr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Björn Eistel
# Contact: <eistel@gmail.com>
#
# THIS SOURCE-CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED. IN NO  EVENT WILL THE AUTHOR BE HELD LIABLE FOR ANY DAMAGES ARISING FROM
# THE USE OF THIS SOURCE-CODE. USE AT YOUR OWN RISK.

import argparse
import yaml
import sys

def main():
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('--cfile', type=open)

    sub_parser = parser.add_subparsers(help='commands')
    deb_sub_parser = sub_parser.add_parser('deb', help='List contents')




    results = parser.parse_args(['--cfile', 'config.yaml', 'deb'])


    '''
    class REPR(object):
        def __repr__(self):
            return "%s(%s)" % (
                self.__class__.__name__,
                ' '.join(['%s=%r' % (x, getattr(self, x)) for x in dir(self) if not x.startswith('_') and not 'yaml' in x])
            )

    class MAINTAINER(yaml.YAMLObject, REPR):
        yaml_loader = yaml.SafeLoader
        yaml_tag = u'!MAINTAINER'
    '''

    if not results.cfile is None:
        from pprint import pprint
        m =yaml.safe_load(results.cfile)
        pprint(m)

if __name__ == '__main__':
    main()

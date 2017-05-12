#!/opt/acuda_repomngr/venv_acuda_repomngr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Björn Eistel
# Contact: <eistel@gmail.com>
#
# THIS SOURCE-CODE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED. IN NO  EVENT WILL THE AUTHOR BE HELD LIABLE FOR ANY DAMAGES ARISING FROM
# THE USE OF THIS SOURCE-CODE. USE AT YOUR OWN RISK.


class ContextManager(object):
    """Prepare Application-Context and give the ability to access the Context trough
    normal initialisation for a given Pseudo-Namespace. The ContextManager provides
    the Plugins-, Configuration- and DataLink-Controller as well as the
    ProcessManager. """

    class Section(object):
        def __init__(self, parent):
            self._parent = parent

    _instance = dict()

    def __new__(cls, *args, **kwargs):
        """
        Act as singleton for simpler data sharing. Internal use only!
        """

        ctxName = kwargs.get('ctxName', None)
        if ctxName not in cls._instance.keys():
            cls._instance[ctxName] = super(ContextManager, cls).__new__(cls)

        if 'section' in kwargs:
            cls._instance[ctxName].add_section(kwargs['section'])
            return getattr(cls._instance[ctxName], kwargs['section'])

        return cls._instance[ctxName]


    def __init__(cls, *args, **kwargs):
        pass

    def add_section(self, name):
        if not hasattr(self, name):
            setattr(self, name, ContextManager.Section(self))

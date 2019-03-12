# -*- coding: utf-8 -*-

import os
from configparser import ConfigParser


ENVIRON_VAR = "OVIRT4_SCRIPTS_INI"
DEFAULT_CFGFILE = "/etc/ovirt4scripts.ini"

LOCAL_CFGFILE = {
        'HOME': '.ovirt4scripts.ini',                 # Pour linux
        'USERPROFILE': 'ovirt4scripts.ini',           # Pour Windows
    }


class Config:
    configs = {}

    def __init__(self, cfg_file=None):
        cfg_file = self.find_inifile(cfg_file)
        cfg = ConfigParser()
        cfg.read(cfg_file)
        self.config = cfg._sections

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value

    def find_inifile(self, inifile):
        if inifile is not None:
            if os.path.exists(inifile):
                return inifile
            else:
                raise Exception("Fichier de configuration %s introuvable", inifile)

        if ENVIRON_VAR in os.environ:
            return os.environ[ENVIRON_VAR]

        for envvarname, filename in LOCAL_CFGFILE.items():
            if envvarname in os.environ:
                if os.path.exists(os.environ[envvarname]+'/'+filename):
                    return os.environ[envvarname]+'/'+filename

        if os.path.exists(DEFAULT_CFGFILE):
            return DEFAULT_CFGFILE

        raise Exception("Aucun fichier de configuration")

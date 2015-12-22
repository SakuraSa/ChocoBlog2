#!/usr/bin/env python
# coding=utf-8

import os
import json

"""
core.configs
"""

__author__ = 'Rnd495'
__all__ = ['Configs', 'ConfigsError']

# check "config/now.conf"
# if not exists, create by copying "config/default.conf" to "config/now.conf"
ENVIRON_ROOT_NAME = "PROJECT_ROOT"
if ENVIRON_ROOT_NAME in os.environ:
    ROOT_PATH = os.environ[ENVIRON_ROOT_NAME]
else:
    ROOT_PATH = os.path.split(os.path.split(__file__)[0])[0]
os.chdir(ROOT_PATH)
CONFIG_PATH_NOW = os.path.join(ROOT_PATH, "config/now.conf")
CONFIG_PATH_DEFAULT = os.path.join(ROOT_PATH, "config/default.conf")
CONFIG_NOTNULL = [
    'database_url',
    'init_admin_username',
    'init_admin_password'
]
if not os.path.exists(CONFIG_PATH_NOW):
    # try to copy from default
    import shutil

    shutil.copy(CONFIG_PATH_DEFAULT, CONFIG_PATH_NOW)
    del shutil


class ConfigsError(Exception):
    """
    ConfigsError
    """

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
        self.error_line = kwargs.get('line', None)


class Configs(object):
    """
    Configs
    """
    INSTANCE_NAME = "_instance"

    def __init__(self, config_file_name):
        with open(config_file_name, 'rb') as file_handle:
            for line in file_handle:
                line = line.strip()
                # lines startswith '#' is comment
                if not line or line.startswith(b'#'):
                    continue
                separator_index = line.find(b'=')
                if separator_index < 0:
                    raise ConfigsError('ConfigsError: config line syntax error', line=line)
                name = line[:separator_index].strip()
                value = line[separator_index + 1:].strip()
                # accept upper case
                if value.lower() in ('true', 'false'):
                    value = value.lower()
                # param type parse
                try:
                    data = json.loads(value)
                    self.__dict__[name] = data
                except ValueError:
                    raise ConfigsError('ConfigsError: unknown data format "%s"' % value, line=line)
        for name in CONFIG_NOTNULL:
            if self.__dict__.get(name, None) is None:
                raise ConfigsError('ConfigsError: property "%s" is not set' % name)

    @classmethod
    def instance(cls, config_file_name=None):
        if not hasattr(cls, cls.INSTANCE_NAME):
            cls.reload_instance(config_file_name)
        return getattr(cls, cls.INSTANCE_NAME)

    @classmethod
    def reload_instance(cls, config_file_name=None):
        setattr(cls, cls.INSTANCE_NAME, cls(config_file_name or CONFIG_PATH_NOW))

    @classmethod
    def clear_instance(cls):
        if hasattr(cls, cls.INSTANCE_NAME):
            delattr(cls, cls.INSTANCE_NAME)


if __name__ == '__main__':
    print("NOW_CONFIGS: ")
    print("path:", CONFIG_PATH_NOW)
    for k, v in Configs.instance().__dict__.iteritems():
        print(k, "=", v)

#!/usr/bin/env python
# coding=utf-8

from flask import Flask
from core.configs import Configs


"""
application
"""

__author__ = 'Rnd495'


configs = Configs.instance()
app = Flask("ChocoBlog2")
app.config['SECRET_KEY'] = configs.cookie_secret
__import__("pages")

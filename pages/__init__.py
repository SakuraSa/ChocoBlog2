#!/usr/bin/env python
# coding=utf-8

import os

"""
__init__.py
"""

__author__ = 'Rnd495'


# import *Page.py
for root, dirs, files in os.walk(os.path.split(__file__)[0]):
    for py in (name for name in files if name.endswith("Page.py")):
        __import__('pages.' + py[:-3])

#!/usr/bin/env python
# coding=utf-8

from flask import render_template
from core.application import app

"""
homePage
"""

__author__ = 'Rnd495'


@app.route('/')
def hello_world():
    return render_template('home.html')

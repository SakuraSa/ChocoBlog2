#!/usr/bin/env python
# coding=utf-8

from flask import render_template
from core.application import app
from core.models import get_new_session, User, Role, Post

"""
homePage
"""

__author__ = 'Rnd495'


@app.route('/')
def hello_world():
    session = get_new_session()
    posts = session.query(Post).order_by(Post.post_time).all()
    html_content = render_template('home.html', posts=posts)
    session.close()
    return html_content

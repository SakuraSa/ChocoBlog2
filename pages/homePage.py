#!/usr/bin/env python
# coding=utf-8

from flask import render_template, request
from core.application import app
from core.models import get_new_session, Tag, Post

"""
homePage
"""

__author__ = 'Rnd495'


@app.route('/', methods=['GET'])
def home():
    session = get_new_session()
    sqlite = session.query(Post).order_by(Post.post_time)
    html_content = render_template('post_list.html', sqlite=sqlite, index=0, size=10)
    session.close()
    return html_content


@app.route('/tag/<tag>', methods=['GET'])
def post_list(tag):
    session = get_new_session()
    sqlite = session.query(Post)\
        .join(Tag)\
        .filter(Tag.post_id == Post.id and Tag.name == tag)\
        .order_by(Post.post_time)
    html_content = render_template('post_list.html', sqlite=sqlite, index=0, size=10)
    session.close()
    return html_content



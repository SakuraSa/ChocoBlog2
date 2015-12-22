#!/usr/bin/env python
# coding=utf-8

from flask import render_template, request
from core.application import app
from core.models import DatabaseContext, Tag, Post

"""
homePage
"""

__author__ = 'Rnd495'


@app.route('/', methods=['GET'])
def home():
    with DatabaseContext() as db:
        sqlite = db.query(Post).order_by(Post.post_time)
        return render_template('post_list.html', sqlite=sqlite, index=0, size=10)


@app.route('/tag/<tag>', methods=['GET'])
def post_list(tag):
    with DatabaseContext() as db:
        sqlite = db.query(Post)\
            .join(Tag)\
            .filter(Tag.post_id == Post.id and Tag.name == tag)\
            .order_by(Post.post_time)
        return render_template('post_list.html', sqlite=sqlite, index=0, size=10)

#!/usr/bin/env python
# coding=utf-8

from flask import render_template
from core.application import app
from core.models import DatabaseContext, Tag, Post
from core.pagination import Pagination as Page

"""
homePage
"""

__author__ = 'Rnd495'


@app.route('/', methods=['GET'])
@app.route('/post/list', methods=['GET'])
@app.route('/post/list/<int:index>', methods=['GET'])
@app.route('/post/list/<int:index>/<int:size>', methods=['GET'])
def post_list(index=0, size=10):
    with DatabaseContext() as db:
        sqlite = db.query(Post).order_by(Post.post_time)
        page = Page(sqlite=sqlite, handler_name='post_list',
                    static_params={}, index=index, size=size)
        return render_template('post_list.html', post_page=page)


@app.route('/post/tag/<tag>', methods=['GET'])
@app.route('/post/tag/<tag>/<int:index>', methods=['GET'])
@app.route('/post/tag/<tag>/<int:index>/<int:size>', methods=['GET'])
def post_list_by_tag(tag, index=0, size=10):
    with DatabaseContext() as db:
        sqlite = db.query(Post)\
            .join(Tag)\
            .filter(Tag.post_id == Post.id and Tag.name == tag)\
            .order_by(Post.post_time)
        page = Page(sqlite=sqlite, handler_name='post_list_by_tag',
                    static_params={'tag': tag}, index=index, size=size)
        return render_template('post_list.html', post_page=page)

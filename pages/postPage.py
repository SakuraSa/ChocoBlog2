#!/usr/bin/env python
# coding=utf-8

from flask import render_template, abort, request, redirect, url_for
from core.application import app
from core.models import DatabaseContext, Post, Tag
from core.configs import Configs
from core.pagination import Pagination as Page
from pages.sessionPage import get_current_user, need_authorized

"""
postPage
"""

__author__ = 'Rnd495'


@app.route('/', methods=['GET'])
@app.route('/post/list', methods=['GET'])
@app.route('/post/list/<int:index>', methods=['GET'])
@app.route('/post/list/<int:index>/<int:size>', methods=['GET'])
def post_list(index=0, size=10):
    with DatabaseContext() as db:
        sqlite = db.query(Post).order_by(Post.post_time)
        if not get_current_user():
            sqlite = sqlite.filter(~Post.hidden)
        page = Page(sqlite=sqlite, handler_name='post_list',
                    static_params={}, index=index, size=size)
        return render_template('post_list.html', post_page=page, user=get_current_user())


@app.route('/post/tag/<tag>', methods=['GET'])
@app.route('/post/tag/<tag>/<int:index>', methods=['GET'])
@app.route('/post/tag/<tag>/<int:index>/<int:size>', methods=['GET'])
def post_list_by_tag(tag, index=0, size=10):
    with DatabaseContext() as db:
        sqlite = db.query(Post) \
            .join(Tag) \
            .filter(Tag.post_id == Post.id and Tag.name == tag) \
            .order_by(Post.post_time)
        if not get_current_user():
            sqlite = sqlite.filter(~Post.hidden)
        page = Page(sqlite=sqlite, handler_name='post_list_by_tag',
                    static_params={'tag': tag}, index=index, size=size)
        return render_template('post_list.html', post_page=page, user=get_current_user())


@app.route('/post/<int:post_id>', methods=['GET'])
def post_show(post_id):
    with DatabaseContext() as db:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            abort(404)
        if not get_current_user() and post.hidden:
            abort(404)
        return render_template('post.html',
                               post=post,
                               disqus_name=Configs.instance().disqus_name,
                               user=get_current_user())


@app.route('/post/new', methods=['GET', 'POST'])
@need_authorized
def new_post():
    if request.method == 'GET':
        return edit_post(post_id=None)
    elif request.method == 'POST':
        return 'read from request.form and save new post'


@app.route('/post/edit/<int:post_id>', methods=['GET'])
@need_authorized
def edit_post(post_id):
    if post_id is None:
        return 'show empty form'
    else:
        return 'show post'


@app.route('/post/delete/<int:post_id>')
@need_authorized
def delete_post(post_id):
    with DatabaseContext() as db:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            abort(404)
        db.delete(post)
        db.commit()
        return redirect(url_for('post_list'))


@app.route('/post/<action>/<int:post_id>')
@need_authorized
def toggle_post_display(action, post_id):
    action = action.lower().strip()
    takes = {'show': False, 'hide': True}
    if action not in takes:
        abort(400)
    with DatabaseContext() as db:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            abort(404)
        post.hidden = takes[action]
        db.commit()
        return redirect(url_for('post_show', post_id=post_id))

#!/usr/bin/env python
# coding=utf-8

from flask import render_template, abort
from core.application import app
from core.models import get_new_session, Post

"""
postPage
"""

__author__ = 'Rnd495'


@app.route('/post/<int:post_id>', methods=['GET'])
def post_show(post_id):
    session = get_new_session()
    post = session.query(Post).filter(Post.id == post_id).first()
    html_content = render_template('post.html', post=post) if post else None
    session.close()
    return html_content if html_content else abort(404)

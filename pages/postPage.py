#!/usr/bin/env python
# coding=utf-8

from flask import render_template, abort
from core.application import app
from core.models import DatabaseContext, Post
from core.configs import Configs as configs

"""
postPage
"""

__author__ = 'Rnd495'


@app.route('/post/<int:post_id>', methods=['GET'])
def post_show(post_id):
    with DatabaseContext() as db:
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            abort(404)
        return render_template('post.html', post=post, disqus_name=configs.instance().disqus_name)

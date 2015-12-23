#!/usr/bin/env python
# coding=utf-8

import random
import hashlib
import datetime

from flask import render_template, request, session, abort, redirect, url_for
from core.application import app
from core.models import DatabaseContext, User


"""
sessionPage
"""

__author__ = 'Rnd495'


def create_random_secret(seed=None):
    """
    create a random secret
    :param seed: random seed
    :return: hex string
    """
    gen = random.Random(seed)
    layer_one = ''.join(chr(gen.randint(0, 255)) for _ in range(64))
    return hashlib.sha256(layer_one).hexdigest()


def check_expire():
    if session:
        expire_date = session.get('expires', None)
        if not expire_date:
            return False
        return expire_date < datetime.datetime.now()
    return False


def get_current_user():
    if session:
        if check_expire():
            if 'user' in session:
                del session['user']
        else:
            user_id = session.get('user', None)
            with DatabaseContext() as db:
                if user_id is not None:
                    user = db.query(User).filter(User.id == user_id).one()
                else:
                    user = None
                return user
    return None


@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'GET':
        secret = create_random_secret()
        session['secret'] = secret
        return render_template('sign-in.html', secret=secret)
    elif request.method == 'POST':
        secret = session.get('secret', '')
        if secret != request.form['secret']:
            abort(403)

        username = request.form['username']
        password = request.form['password']

        with DatabaseContext() as db:
            user = db.query(User).filter(User.name == username).first()

        if not user or password != hashlib.sha256(secret + user.pwd).hexdigest():
            abort(403)
        expire_date = datetime.datetime.now() + datetime.timedelta(days=30)
        session['user'] = user.id
        session['expires'] = expire_date
        return redirect(url_for('post_list'))
    else:
        abort(405)


@app.route('/sign-out', methods=['GET'])
def sign_out():
    if 'user' in session:
        del session['user']
    if 'expires' in session:
        del session['expires']
    return redirect(url_for('post_list'))

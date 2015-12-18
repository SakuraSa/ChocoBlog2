#!/usr/bin/env python
# coding=utf-8

import random
import hashlib
import datetime

from flask import render_template, make_response, request, session, abort, redirect, url_for
from core.application import app
from core.models import get_new_session, User


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
        if not check_expire():
            if 'user' in session:
                del session['user']
        else:
            return session.get('user', None)
    return None


@app.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'GET':
        secret = create_random_secret()
        session['secret'] = secret
        return render_template('sign-in.html', secret=secret)
    else:
        secret = session.get('secret', '')
        if secret != request.form['secret']:
            abort(401)

        username = request.form['username']
        password = request.form['password']

        db = get_new_session()
        user = db.query(User).filter(User.name == username).first()
        db.close()

        if not user or password != hashlib.sha256(secret + user.pwd).hexdigest():
            abort(401)
        expire_date = datetime.datetime.now() + datetime.timedelta(days=30)
        session['user'] = user
        session['expires'] = expire_date
        return redirect(url_for('home'))


@app.route('/sign-out', methods=['GET'])
def sign_out():
    if 'user' in session:
        del session['user']
    if 'expires' in session:
        del session['expires']
    return redirect(url_for('home'))

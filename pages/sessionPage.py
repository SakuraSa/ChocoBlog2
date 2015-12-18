#!/usr/bin/env python
# coding=utf-8

import random
import hashlib
import datetime

from flask import render_template, make_response, request, session, abort
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
        response = make_response('Hello ' + user.name)
        expire_date = datetime.datetime.now()
        expire_date = expire_date + datetime.timedelta(days=30)
        response.set_cookie('id', str(user.id), expires=expire_date)
        return response

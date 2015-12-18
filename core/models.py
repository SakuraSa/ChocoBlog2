#!/usr/bin/env python
# coding=utf-8

import datetime
import hashlib

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, Index, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

"""
core.models
"""

__author__ = 'Rnd495'


class _Base(object):
    """
    Base
    """

    def __repr__(self):
        return "<%s>" % type(self).__name__

    @staticmethod
    def init_data(config):
        pass

Base = declarative_base(cls=_Base)


_models = []


def model(_class):
    global _models
    _models.append(_class)
    return _class


@model
class User(Base):
    __tablename__ = 'T_User'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=64), nullable=False, unique=True, index=Index('User_index_name'))
    pwd = Column(String(length=128), nullable=False)
    role_id = Column(Integer, ForeignKey('T_Role.id'))
    register_time = Column(DateTime, nullable=False)

    role = relationship("Role", uselist=False, backref="T_User")

    def __init__(self, name, pwd,
                 role_id=3,
                 header_url=None):
        self.name = name
        self.pwd = pwd
        self.register_time = datetime.datetime.now()
        self.role_id = role_id
        self.header_url = header_url

    def __repr__(self):
        return "<User[%s]: %s>" % (self.id, self.name)

    @staticmethod
    def init_data(config):
        session = get_new_session()
        session.add(User(
            name=config.init_admin_username,
            pwd=hashlib.sha256(config.init_admin_password).hexdigest(),
            role_id=1
        ))
        session.commit()
        session.close()


@model
class Role(Base):
    __tablename__ = 'T_Role'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=64), nullable=False)

    def __init__(self, name, id=None):
        self.name = name
        if id is not None:
            self.id = id

    def __repr__(self):
        return "<Role[%s]: %s>" % (self.id, self.name)

    @staticmethod
    def init_data(_):
        session = get_new_session()
        session.add(Role(name=u"站长", id=1))
        session.add(Role(name=u"管理员", id=2))
        session.add(Role(name=u"会员", id=3))
        session.commit()
        session.close()


@model
class Post(Base):
    __tablename__ = 'T_Post'

    id = Column(Integer, primary_key=True, autoincrement=True)
    author_id = Column(Integer, ForeignKey('T_User.id'), nullable=False)
    title = Column(String(length=128), nullable=False)
    content = Column(Text, nullable=False)
    post_time = Column(DateTime, nullable=False)

    author = relationship("User", uselist=False, backref="T_Post")

    def __init__(self, title, content, author_id):
        self.title = title
        self.content = content
        self.post_time = datetime.datetime.now()
        self.author_id = author_id

    def __repr__(self):
        return "<Post[%s]: %s>" % (self.id, self.title)

    @staticmethod
    def init_data(_):
        import os.path
        from core.configs import ROOT_PATH

        md_file_name = os.path.join(ROOT_PATH, 'markdown-help.md')
        if os.path.exists(md_file_name):
            title = u'Markdown Help'
            with open(md_file_name, 'rb') as file_handle:
                content = file_handle.read().decode('utf-8')

            session = get_new_session()
            session.add(Post(title=title, content=content, author_id=1))
            session.commit()
            session.close()

_engine = None
_session_maker = None
_session = None
_table_created = False


def get_engine(configs=None, echo=False, auto_create=False):
    global _engine
    if configs is None:
        from core.configs import Configs
        configs = Configs.instance()
    else:
        _engine = None
    if not _engine:
        _engine = create_engine(configs.database_url, echo=echo)
    if auto_create and not _table_created:
        create_all(_engine)
    return _engine


def get_session_maker():
    global _session_maker
    if not _session_maker:
        _session_maker = sessionmaker(bind=get_engine())
    return _session_maker


def get_global_session():
    global _session
    if not _session:
        _session = get_session_maker()()
    return _session


def get_new_session():
    return get_session_maker()()


def create_all(engine):
    global _table_created
    _table_created = True
    from core.configs import Configs
    Base.metadata.create_all(engine)
    config = Configs.instance()
    for _class in _models:
        _class.init_data(config)


def drop_all(engine):
    Base.metadata.drop_all(engine)

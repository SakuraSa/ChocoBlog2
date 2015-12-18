#!/usr/bin/env python
# coding=utf-8

import unittest

import core.configs
import core.models

"""
test
"""

__author__ = 'Rnd495'


class ModelsTestCase(unittest.TestCase):

    def setUp(self):
        config = core.configs.Configs.instance("config/test.conf")
        engine = core.models.get_engine(config, echo=False, auto_create=False)
        core.models.drop_all(engine)
        core.models.create_all(engine)

    def test_model_init(self):
        from core.models import get_new_session, User, Role
        session = get_new_session()
        user_admin = session.query(core.models.User).filter(
            User.name == core.configs.Configs.instance().init_admin_username).first()
        assert user_admin, "admin user failed to be created."
        role_list = session.query(Role).all()
        assert role_list, "role failed to be created."
        admin_role = user_admin.role
        assert admin_role.id == 1, "admin user get wrong role"
        session.close()

    def tearDown(self):
        core.models.drop_all(core.models.get_engine())

if __name__ == '__main__':
    unittest.main()

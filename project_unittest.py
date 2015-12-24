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
        # setup db
        self.config = core.configs.Configs.instance("config/test.conf")
        self.engine = core.models.get_engine(self.config, echo=False, auto_create=False)
        # clear db
        core.models.drop_all(self.engine)
        # rebuild db
        core.models.create_all(self.engine)

        # setup app
        from core.application import app
        self.app = app.test_client()

    def test_model_init(self):
        from core.models import DatabaseContext, User, Role, Post
        with DatabaseContext() as db:
            user_admin = db.query(core.models.User).filter(
                User.name == core.configs.Configs.instance().init_admin_username).first()
            assert user_admin, "admin user failed to be created."
            role_list = db.query(Role).all()
            assert role_list, "role failed to be created."
            admin_role = user_admin.role
            assert admin_role.id == 1, "admin user get wrong role"
            welcome_post = db.query(Post).first()
            assert welcome_post, "welcome post failed to be created"
            assert welcome_post.tags, "welcome post tags failed to be created"

    def test_model_operations(self):
        from core.models import DatabaseContext, User, Post
        with DatabaseContext() as db:
            admin = db.query(User).filter(User.role_id == 1).first()
            assert admin, "no admin user is found."
            test_post_title = "Test post"
            post = Post(test_post_title, "# This is a test post\n# This should not be seen for users.", admin.id, False)
            db.add(post)
            db.commit()
            post.add_tags("test")

            # tag operation test
            post = db.query(Post).filter(Post.title == test_post_title).first()
            assert post, "test post failed to be created"
            post.clear_tags()
            assert not post.tags, "post tags failed to be cleared"
            test_tag_texts = "this is a test".split()
            post.add_tags(*test_tag_texts)
            assert all(tag.name in test_tag_texts for tag in post.tags), "post tags failed to be added"

            # remove test post
            db.query(Post).filter(Post.title == test_post_title).delete()
            db.commit()

    def tearDown(self):
        core.models.drop_all(core.models.get_engine())


class AuthorizationTestCase(unittest.TestCase):

    def setUp(self):
        # setup db
        self.config = core.configs.Configs.instance("config/test.conf")
        self.engine = core.models.get_engine(self.config, echo=False, auto_create=False)
        # clear db
        core.models.drop_all(self.engine)
        # rebuild db
        core.models.create_all(self.engine)

        # setup app
        from core.application import app
        self.app = app.test_client()

        # setup test post
        from core.models import DatabaseContext, User, Post
        with DatabaseContext() as db:
            # get a admin user
            admin = db.query(User).filter(User.role_id == 1).first()
            # build test posts
            public_post = Post('Public', 'content', admin.id, False)
            private_post = Post('Private', 'content', admin.id, True)
            db.add(public_post)
            db.add(private_post)
            db.commit()
            public_post.add_tags("test", "public")
            private_post.add_tags("test", "private")
            self.post_public_id = public_post.id
            self.post_private_id = private_post.id

    def test_anonymous_authorization_home(self):
        test_cases = [
            ('/', 'ChocoBlog2', True),
            ('/', 'Public', True),
            ('/', 'Private', False),
        ]
        self.multi_access_testing(test_cases)

    def test_anonymous_authorization_post_list(self):
        test_cases = [
            ('/post/list', 'ChocoBlog2', True),
            ('/post/list', 'Public', True),
            ('/post/list', 'Private', False),
            ('/post/list/0', 'ChocoBlog2', True),
            ('/post/list/0', 'Public', True),
            ('/post/list/0', 'Private', False),
            ('/post/list/0/10', 'ChocoBlog2', True),
            ('/post/list/0/10', 'Public', True),
            ('/post/list/0/10', 'Private', False),
        ]
        self.multi_access_testing(test_cases)

    def test_anonymous_authorization_post_list_filtered_by_tag(self):
        test_cases = [
            ('/post/tag/test', 'ChocoBlog2', True),
            ('/post/tag/test', 'Public', True),
            ('/post/tag/test', 'Private', False),
            ('/post/tag/public', 'ChocoBlog2', True),
            ('/post/tag/public', 'Public', True),
            ('/post/tag/public', 'Private', False),
            ('/post/tag/private', 'ChocoBlog2', True),
            ('/post/tag/private', 'Public', False),
            ('/post/tag/private', 'Private', False),
            ('/post/tag/test/0', 'ChocoBlog2', True),
            ('/post/tag/test/0', 'Public', True),
            ('/post/tag/test/0', 'Private', False),
            ('/post/tag/public/0', 'ChocoBlog2', True),
            ('/post/tag/public/0', 'Public', True),
            ('/post/tag/public/0', 'Private', False),
            ('/post/tag/private/0', 'ChocoBlog2', True),
            ('/post/tag/private/0', 'Public', False),
            ('/post/tag/private/0', 'Private', False),
            ('/post/tag/test/0/10', 'ChocoBlog2', True),
            ('/post/tag/test/0/10', 'Public', True),
            ('/post/tag/test/0/10', 'Private', False),
            ('/post/tag/public/0/10', 'ChocoBlog2', True),
            ('/post/tag/public/0/10', 'Public', True),
            ('/post/tag/public/0/10', 'Private', False),
            ('/post/tag/private/0/10', 'ChocoBlog2', True),
            ('/post/tag/private/0/10', 'Public', False),
            ('/post/tag/private/0/10', 'Private', False),
        ]
        self.multi_access_testing(test_cases)

    def test_anonymous_authorization_post_view(self):
        test_cases = [
            ('/post/%d' % self.post_public_id, 'Public', True),
            ('/post/%d' % self.post_public_id, 'content', True),
            ('/post/%d' % self.post_private_id, 'Private', False),
            ('/post/%d' % self.post_private_id, 'content', False),
        ]
        self.multi_access_testing(test_cases)

    def test_anonymous_authorization_post_operation_deny_by_get(self):
        test_cases = [
            ('/post/new', None, False),
            ('/post/edit/%d' % self.post_public_id, None, False),
            ('/post/edit/%d' % self.post_private_id, None, False),
            ('/post/delete/%d' % self.post_public_id, None, False),
            ('/post/delete/%d' % self.post_private_id, None, False),
            ('/post/show/%d' % self.post_public_id, None, False),
            ('/post/show/%d' % self.post_private_id, None, False),
            ('/post/hide/%d' % self.post_public_id, None, False),
            ('/post/hide/%d' % self.post_private_id, None, False),
        ]
        self.multi_access_testing(test_cases)

    def test_anonymous_authorization_post_operation_deny_by_post(self):
        data = {
            'post_id': '',
            'post_title': 'anonymous posted post',
            'post_content': 'this content should be denied.',
            'post_hidden': 'true',
            'post_tags': 'this, should, not, added, to, tags'
        }
        response = self.app.post('/post/new', data=data, follow_redirects=True)
        accessed = 200 <= response.status_code < 300
        denied = not accessed
        assert denied, 'server accepted anonymous new post'

    def test_login_and_logout(self):
        self.login()
        self.logout()

    def test_admin_authorization_home(self):
        self.login()
        test_cases = [
            ('/', 'ChocoBlog2', True),
            ('/', 'Public', True),
            ('/', 'Private', True),
        ]
        self.multi_access_testing(test_cases)
        self.logout()

    def test_admin_authorization_post_list(self):
        self.login()
        test_cases = [
            ('/post/list', 'ChocoBlog2', True),
            ('/post/list', 'Public', True),
            ('/post/list', 'Private', True),
            ('/post/list/0', 'ChocoBlog2', True),
            ('/post/list/0', 'Public', True),
            ('/post/list/0', 'Private', True),
            ('/post/list/0/10', 'ChocoBlog2', True),
            ('/post/list/0/10', 'Public', True),
            ('/post/list/0/10', 'Private', True),
        ]
        self.multi_access_testing(test_cases)
        self.logout()

    def test_admin_authorization_post_list_filtered_by_tag(self):
        self.login()
        test_cases = [
            ('/post/tag/test', 'ChocoBlog2', True),
            ('/post/tag/test', 'Public', True),
            ('/post/tag/test', 'Private', True),
            ('/post/tag/public', 'ChocoBlog2', True),
            ('/post/tag/public', 'Public', True),
            ('/post/tag/public', 'Private', False),
            ('/post/tag/private', 'ChocoBlog2', True),
            ('/post/tag/private', 'Public', False),
            ('/post/tag/private', 'Private', True),
            ('/post/tag/test/0', 'ChocoBlog2', True),
            ('/post/tag/test/0', 'Public', True),
            ('/post/tag/test/0', 'Private', True),
            ('/post/tag/public/0', 'ChocoBlog2', True),
            ('/post/tag/public/0', 'Public', True),
            ('/post/tag/public/0', 'Private', False),
            ('/post/tag/private/0', 'ChocoBlog2', True),
            ('/post/tag/private/0', 'Public', False),
            ('/post/tag/private/0', 'Private', True),
            ('/post/tag/test/0/10', 'ChocoBlog2', True),
            ('/post/tag/test/0/10', 'Public', True),
            ('/post/tag/test/0/10', 'Private', True),
            ('/post/tag/public/0/10', 'ChocoBlog2', True),
            ('/post/tag/public/0/10', 'Public', True),
            ('/post/tag/public/0/10', 'Private', False),
            ('/post/tag/private/0/10', 'ChocoBlog2', True),
            ('/post/tag/private/0/10', 'Public', False),
            ('/post/tag/private/0/10', 'Private', True),
        ]
        self.multi_access_testing(test_cases)
        self.logout()

    def test_admin_authorization_post_view(self):
        self.login()
        test_cases = [
            ('/post/%d' % self.post_public_id, 'Public', True),
            ('/post/%d' % self.post_public_id, 'content', True),
            ('/post/%d' % self.post_private_id, 'Private', True),
            ('/post/%d' % self.post_private_id, 'content', True),
        ]
        self.multi_access_testing(test_cases)
        self.logout()

    def test_admin_authorization_post_operations(self):
        self.login()

        # new post
        post_data = {
            'post_id': '',
            'post_title': 'new post for test',
            'post_content': 'content 00',
            'post_tags': 'tag0, tag1, tag2, tag3'
        }
        response = self.app.post('/post/new', data=post_data, follow_redirects=True)
        successful = 200 <= response.status_code < 300 and post_data['post_title'] in response.data
        assert successful, 'admin create new post failed'

        # edit post
        from core.models import DatabaseContext, Post
        with DatabaseContext() as db:
            post_data['post_id'] = db.query(Post).filter(Post.title == post_data['post_title']).one().id
        post_data['post_title'] = 'new post for test(MOD)'
        post_data['post_content'] = 'content 01'
        post_data['post_tags'] = 't0, t1, t2, t3'
        response = self.app.post('/post/new', data=post_data, follow_redirects=True)
        successful = 200 <= response.status_code < 300 and post_data['post_title'] in response.data
        response_content = response.data
        assert successful, 'admin edit post failed'
        if any(tag.strip() not in response_content for tag in post_data['post_tags'].split(',')):
            successful = False
        assert successful, 'admin edit post failed, tag is missing'

        # hide post
        self.app.get('/post/hide/%s' % post_data['post_id'])
        self.logout()
        response = self.app.get('/')
        response_content = response.data
        assert post_data['post_title'] not in response_content, 'admin hide post failed'
        self.login()

        # show post
        self.app.get('/post/show/%s' % post_data['post_id'])
        self.logout()
        response = self.app.get('/')
        response_content = response.data
        assert post_data['post_title'] in response_content, 'admin show post failed'
        self.login()

        # delete post
        response = self.app.get('/post/delete/%s' % post_data['post_id'], follow_redirects=True)
        successful = 200 <= response.status_code < 300 and post_data['post_title'] not in response.data
        assert successful, 'admin delete post failed'

        self.logout()

    def login(self):
        import re
        import hashlib
        username = self.config.init_admin_username
        password = self.config.init_admin_password

        secret_regex = re.compile(r'name="secret"\s*value="([^"]+)"')
        login_page_response = self.app.get('/sign-in')
        html_content = login_page_response.data
        match = secret_regex.search(html_content)
        assert match, "secret not found in sign-in page."
        secret = match.group(1)
        salt_added_password = secret + hashlib.sha256(password).hexdigest()
        salt_hashed_password = hashlib.sha256(salt_added_password).hexdigest()

        login_post_data = {
            'username': username,
            'password': salt_hashed_password,
            'secret': secret
        }
        login_response = self.app.post('/sign-in', data=login_post_data, follow_redirects=True)
        successful = 200 <= login_response.status_code < 300
        assert successful, 'login failed.'

    def logout(self):
        self.app.get('/sign-out')

    def multi_access_testing(self, test_cases):
        for test_case in test_cases:
            self.access_testing(*test_case)

    def access_testing(self, url, content, accessible):
        response = self.app.get(url)
        accessed = 200 <= response.status_code < 300
        if content:
            accessed = accessed and content in response.data
        if accessible:
            assert accessed == accessible, '"%s" denied. Test case: %s' % (url, content)
        else:
            assert accessed == accessible, '"%s" accessible. Test case: %s' % (url, content)

    def tearDown(self):
        core.models.drop_all(core.models.get_engine())

if __name__ == '__main__':
    unittest.main()

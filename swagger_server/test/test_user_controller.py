# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.test import BaseTestCase


class TestUserController(BaseTestCase):
    """UserController integration test stubs"""

    def test_create_user(self):
        """Test case for create_user

        Create user Leobox
        """
        query_string = [('email', 'email_example'),
                        ('username', 'username_example'),
                        ('lastfistname', 'lastfistname_example'),
                        ('password', 'password_example')]
        response = self.client.open(
            '/v1/user/create',
            method='POST',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_user(self):
        """Test case for delete_user

        Delete user
        """
        response = self.client.open(
            '/v1/user/{username}'.format(username='username_example'),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_user_by_name(self):
        """Test case for get_user_by_name

        List of username
        """
        response = self.client.open(
            '/v1/user/{username}'.format(username='username_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_login_user(self):
        """Test case for login_user

        Logs user into Leobox
        """
        query_string = [('username', 'username_example'),
                        ('password', 'password_example')]
        response = self.client.open(
            '/v1/user/login',
            method='GET',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_logout_user(self):
        """Test case for logout_user

        Logs out current logged in user session
        """
        response = self.client.open(
            '/v1/user/{username}/logout'.format(username='username_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_user(self):
        """Test case for update_user

        Updated user
        """
        query_string = [('new_username', 'new_username_example'),
                        ('email', 'email_example'),
                        ('password', 'password_example')]
        response = self.client.open(
            '/v1/user/{username}'.format(username='username_example'),
            method='PUT',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()

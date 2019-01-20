# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.test import BaseTestCase


class TestShareController(BaseTestCase):
    """ShareController integration test stubs"""

    def test_delete_shared_file(self):
        """Test case for delete_shared_file

        Delete File of User
        """
        response = self.client.open(
            '/v1/share/{username}/{id_shared}'.format(username='username_example', id_shared=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_shared_file(self):
        """Test case for get_shared_file

        Download Shared File of User
        """
        response = self.client.open(
            '/v1/share/{username}/{id_shared}'.format(username='username_example', id_shared=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_shared_list_file(self):
        """Test case for get_shared_list_file

        List of All Shared File of User
        """
        response = self.client.open(
            '/v1/share/{username}'.format(username='username_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_share_file(self):
        """Test case for share_file

        Share file in Leobox
        """
        query_string = [('item_type', 'item_type_example'),
                        ('id_owner', 56),
                        ('id_shared', 56),
                        ('id_file', 56),
                        ('expiration', 'expiration_example'),
                        ('comment', 'comment_example')]
        response = self.client.open(
            '/v1/share/create',
            method='POST',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_updateshare_file(self):
        """Test case for updateshare_file

        Update shared file in Leobox
        """
        query_string = [('item_type', 'item_type_example'),
                        ('expiration', 'expiration_example'),
                        ('comment', 'comment_example')]
        response = self.client.open(
            '/v1/share/{username}/{id_shared}'.format(username='username_example', id_shared=56),
            method='PUT',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()

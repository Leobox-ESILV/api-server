# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.test import BaseTestCase


class TestFileController(BaseTestCase):
    """FileController integration test stubs"""

    def test_create_file(self):
        """Test case for create_file

        Create file in Leobox
        """
        query_string = [('path_file', 'path_file_example'),
                        ('file_name', 'file_name_example'),
                        ('size', 0),
                        ('is_crypted', true),
                        ('propertyname', 'propertyname_example'),
                        ('propertyvalue', 'propertyvalue_example')]
        response = self.client.open(
            '/v1/file/create',
            method='POST',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_delete_file(self):
        """Test case for delete_file

        Delete File of User
        """
        response = self.client.open(
            '/v1/file/{username}/{id_file}'.format(username='username_example', id_file=56),
            method='DELETE')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_file(self):
        """Test case for get_file

        Download File of User
        """
        response = self.client.open(
            '/v1/file/{username}/{id_file}'.format(username='username_example', id_file=56),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_get_list_file(self):
        """Test case for get_list_file

        List of All File of User
        """
        response = self.client.open(
            '/v1/file/{username}'.format(username='username_example'),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_update_file(self):
        """Test case for update_file

        Update File of User
        """
        query_string = [('path_file', 'path_file_example'),
                        ('file_name', 'file_name_example'),
                        ('size', 0),
                        ('is_crypted', true),
                        ('propertyname', 'propertyname_example'),
                        ('propertyvalue', 'propertyvalue_example')]
        response = self.client.open(
            '/v1/file/{username}/{id_file}'.format(username='username_example', id_file=56),
            method='PUT',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))

    def test_upload_file(self):
        """Test case for upload_file

        Upload file in Leobox
        """
        query_string = [('id_file', 56)]
        data = dict(file=(BytesIO(b'some file data'), 'file.txt'))
        response = self.client.open(
            '/v1/file/upload',
            method='POST',
            data=data,
            content_type='multipart/form-data',
            query_string=query_string)
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()

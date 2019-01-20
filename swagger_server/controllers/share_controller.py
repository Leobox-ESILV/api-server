import connexion
import six

from swagger_server import util


def delete_shared_file(username, id_shared):  # noqa: E501
    """Delete File of User

    This can access only by logger user and shared user # noqa: E501

    :param username: username of user
    :type username: str
    :param id_shared: ID of who did you share file
    :type id_shared: int

    :rtype: None
    """
    return 'do some magic!'


def get_shared_file(username, id_shared):  # noqa: E501
    """Download Shared File of User

    This can access only by logger user and shared user # noqa: E501

    :param username: username of user
    :type username: str
    :param id_shared: ID of who did you share file
    :type id_shared: int

    :rtype: None
    """
    return 'do some magic!'


def get_shared_list_file(username):  # noqa: E501
    """List of All Shared File of User

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str

    :rtype: None
    """
    return 'do some magic!'


def share_file(username, item_type, name_shared, id_file, expiration, comment):  # noqa: E501
    """Share file in Leobox

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str
    :param item_type: Type of share (file or folder)
    :type item_type: str
    :param name_shared: name of who did you share file
    :type name_shared: int
    :param id_file: ID of file shared
    :type id_file: int
    :param expiration: Date of expiration share
    :type expiration: str
    :param comment: Comment for shared file
    :type comment: str

    :rtype: None
    """
    return 'do some magic!'


def updateshare_file(username, id_shared, item_type=None, expiration=None, comment=None):  # noqa: E501
    """Update shared file in Leobox

    This can access only by logger user and shared user # noqa: E501

    :param username: Username of user
    :type username: str
    :param id_shared: ID of who did you share file
    :type id_shared: int
    :param item_type: Type of share (file or folder)
    :type item_type: str
    :param expiration: Date of expiration share
    :type expiration: str
    :param comment: Comment for shared file
    :type comment: str

    :rtype: None
    """
    return 'do some magic!'

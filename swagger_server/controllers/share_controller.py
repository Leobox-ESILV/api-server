import connexion
import six

from swagger_server import util
import swagger_server.models.share_model as share_model

def delete_shared_file(username, id_shared):  # noqa: E501
    """Delete File of User

    This can access only by logger user and shared user # noqa: E501

    :param username: username of user
    :type username: str
    :param id_shared: ID of who did you share file
    :type id_shared: int

    :rtype: None
    """
    return None


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


def get_shared_list_file(username, uid_owner = None, uid_file = None):  # noqa: E501
    """List of All Shared File of User

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str

    :rtype: None
    """
    if uid_owner:
        return share_model.getsharedlistfile2(username,uid_owner)
    else:
        return share_model.getsharedlistfile(username)


def share_file_add(username, username_shared, id_file, expiration=None):  # noqa: E501
    """Add user access to file

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str
    :param username_shared: name of who did you share file
    :type username_shared: int
    :param id_file: ID of file shared
    :type id_file: int
    :param expiration: Date of expiration share
    :type expiration: str

    :rtype: None
    """
    return share_model.adduser(username, username_shared, id_file, expiration)


def share_file_delete(username, username_shared, id_file):  # noqa: E501
    """Remove access to user to a file shared

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str
    :param username_shared: name of who did you share file
    :type username_shared: int
    :param id_file: ID of file shared
    :type id_file: int
    :param expiration: Date of expiration share
    :type expiration: str

    :rtype: None
    """
    return share_model.removeuser(username, username_shared, id_file)


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

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
    return share_model.delete_file_model(username, id_shared)


def get_shared_file(username, id_shared):  # noqa: E501
    """Download Shared File of User

    This can access only by logger user and shared user # noqa: E501

    :param username: username of user
    :type username: str
    :param id_shared: ID of who did you share file
    :type id_shared: int

    :rtype: None
    """
    return share_model.get_file_model(username, id_shared)


def get_shared_list_file(username, uid_owner = None, uid_file = None):  # noqa: E501
    """List of All Shared File of User

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str

    :rtype: None
    """
    if uid_owner:
        return share_model.getsharedlistfile2(username,uid_owner)
    elif uid_file:
        return share_model.getsharedlistfile3(username,uid_file)
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


def update_file_share(action, username, id_shared, path_file=None,file=None, propertyname=None, propertyvalue=None):  # noqa: E501
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
    if action==1:
        return share_model.rename_file_model(username, id_shared, path_file, propertyname, propertyvalue)
    elif action == 2:
        return json_output(400,"bad request, NOT YET")
    elif action == 3:
        return share_model.update_file_model(username, id_shared, file, propertyname, propertyvalue)
    else:
        return json_output(400,"bad request, ACTION INVALID")


def upload_file_share(username, parent_id, file, propertyname=None, propertyvalue=None):  # noqa: E501
    """Upload file in Leobox

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str
    :param parent_id: Path of file
    :type parent_id: str
    :param file: The file to upload.
    :type file: werkzeug.datastructures.FileStorage
    :param propertyname: Additional property name
    :type propertyname: List[str]
    :param propertyvalue: Additional property value
    :type propertyvalue: List[str]

    :rtype: None
    """
    return share_model.upload_file_model(username, parent_id, file, propertyname, propertyvalue)

def create_directory_share(username, path_dir, parent_id, propertyname=None, propertyvalue=None):  # noqa: E501
    """Create directory in Leobox

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str
    :param path_dir: Path of file
    :type path_dir: str
    :param parent_id: Path of file
    :type parent_id: str
    :param propertyname: Additional property name
    :type propertyname: List[str]
    :param propertyvalue: Additional property value
    :type propertyvalue: List[str]

    :rtype: None
    """
    return share_model.create_directory_model(username, path_dir,parent_id, propertyname, propertyvalue)

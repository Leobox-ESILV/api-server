import connexion
import six

from swagger_server import util
import swagger_server.models.file_model as file_model


def create_directory(username, path_dir, propertyname=None, propertyvalue=None):  # noqa: E501
    """Create directory in Leobox

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str
    :param path_dir: Path of file
    :type path_dir: str
    :param propertyname: Additional property name
    :type propertyname: List[str]
    :param propertyvalue: Additional property value
    :type propertyvalue: List[str]

    :rtype: None
    """
    return file_model.create_directory_model(username, path_dir, propertyname, propertyvalue)


def delete_file(username, id_file):  # noqa: E501
    """Delete File of User

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str
    :param id_file: id of file needed to be Deleted
    :type id_file: int

    :rtype: None
    """
    return file_model.delete_file_model(username, id_file)


def get_file(username, id_file):  # noqa: E501
    """Download File of User

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str
    :param id_file: id of file needed to be Deleted
    :type id_file: int

    :rtype: None
    """
    return file_model.get_file_model(username, id_file)


def get_list_file(username):  # noqa: E501
    """List of All File of User

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str

    :rtype: None
    """
    return file_model.get_list_file_model(username)


def update_file(action, username, id_file, path_file=None, file=None, propertyname=None, propertyvalue=None):  # noqa: E501
    """Update File of User

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str
    :param id_file: id of file needed updated
    :type id_file: int
    :param path_file: Path of File
    :type path_file: str
    :param propertyname: Additional property name
    :type propertyname: List[str]
    :param propertyvalue: Additional property value
    :type propertyvalue: List[str]

    :rtype: None
    """
    if action==1:
        return file_model.rename_file_model(username, id_file, path_file, file, propertyname, propertyvalue)
    elif action == 2:
        return file_model.move_file_model(username, id_file, path_file, file, propertyname, propertyvalue)
    elif action == 3:
        return file_model.update_file_model(username, id_file, path_file, file, propertyname, propertyvalue)
    else:
        return json_output(400,"bad request, ACTION INVALID")


def upload_file(username, path_file, file, propertyname=None, propertyvalue=None):  # noqa: E501
    """Upload file in Leobox

    This can access only by logger user # noqa: E501

    :param username: name of user
    :type username: str
    :param path_file: Path of file
    :type path_file: str
    :param file: The file to upload.
    :type file: werkzeug.datastructures.FileStorage
    :param propertyname: Additional property name
    :type propertyname: List[str]
    :param propertyvalue: Additional property value
    :type propertyvalue: List[str]

    :rtype: None
    """
    return file_model.upload_file_model(username, path_file, file, propertyname, propertyvalue)

import connexion
import six

from swagger_server import util
import swagger_server.models.user_model as user_model 

def create_user(email, username, password):  # noqa: E501
    """Create user Leobox

    This can access by everyone # noqa: E501

    :param email: Email adresse
    :type email: str
    :param username: Pseudo of output in Leobox
    :type username: str
    :param password: Password of User
    :type password: str

    :rtype: None
    """
    return user_model.create_user_model(email, username, password)


def delete_user(username):  # noqa: E501
    """Delete user

    This can only be done by the logged in user. # noqa: E501

    :param username: The name that needs to be deleted
    :type username: str

    :rtype: None
    """
    return 'do some magic!'


def get_user_by_name(username):  # noqa: E501
    """List of username

    This can only be done by the logged in user. # noqa: E501

    :param username: The user name for get list of user
    :type username: str

    :rtype: None
    """
    return user_model.get_user_by_name_model(username)


def login_user(username, password):  # noqa: E501
    """Logs user into Leobox

    This can done by everyone # noqa: E501

    :param username: The user name for login
    :type username: str
    :param password: The password for login in clear text
    :type password: str

    :rtype: None
    """
    return user_model.login_user_model(username, password)


def logout_user(username):  # noqa: E501
    """Logs out current logged in user session

    This can only be done by the logged in user. # noqa: E501

    :param username: name that need to be updated
    :type username: str

    :rtype: None
    """
    return user_model.logout_user_model(username)


def update_user(username, new_username=None, email=None, password=None):  # noqa: E501
    """Updated user

    This can only be done by the logged in user. # noqa: E501

    :param username: name that need to be updated
    :type username: str
    :param new_username: new name
    :type new_username: str
    :param email: new email
    :type email: str
    :param password: new password
    :type password: str

    :rtype: None
    """
    return 'do some magic!'

import os
import logging

from six.moves import configparser

import bandwidth_sdk
from .utils import get_creds_from_file, file_exists
from .rest import RESTClientObject


logger = logging.getLogger(__package__)

__all__ = ('Client', 'get_client', 'set_client')

_global_client = None

_HELP_MISSING_ENV_VARS = '' \
    'If BANDWIDTH_USER_ID is defined in the environment, ' \
    'BANDWIDTH_API_TOKEN and BANDWIDTH_API_SECRET must also be defined'

_HELP_MISSING_PARAMS = '' \
    'Creating Client with arguments requires: Client(user_id, token, secret) ' \
    'where user_id, token, secret are from your Catapult account.'

_HELP_CONFIG_FORMAT = '' \
    'The config file: <%s> is either not formatted correctly or is missing ' \
    'values. If that\'s the wrong config file, make sure ' \
    'BANDWIDTH_CONFIG_FILE is set correctly or not set if you\'re trying to ' \
    'use .bndsdkrc.'

_HELP_CONFIG_FILE_MISSING = '' \
    'The config file specified: <%s> could not be found. If that\'s the' \
    ' wrong config file, make sure BANDWIDTH_CONFIG_FILE is set correctly or' \
    ' not set if you\'re trying to use .bndsdkrc.'


def Client(user_id=None, token=None, secret=None):
    """
    Initialize the bandwidth sdk client.  This function will attempt to
    gather credentials from one of several different locations in the
    following order:

    1) Included as arguments when creating the client::

        bandwidth = bandwidth_sdk.Client(
            user_id='u-your-user-id',
            token='t-your-token',
            secret='your-secret')

    2) environment variables::

        $ export BANDWIDTH_USER_ID=u-your-user-id
        $ export BANDWIDTH_API_TOKEN=t-your-token
        $ export BANDWIDTH_API_SECRET=your-secret

    3) Lastly the sdk will attempt to load credentials from a configuration
       file specified with env var BANDWIDTH_CONFIG_FILE else .bndsdkrc is
       searched for in the current directory. The config file has the following
       format::

        $ export BANDWIDTH_CONFIG_FILE=/home/user/.bndsdkrc
        $ cat /home/user/.bndsdkrc
        [catapult]
        user_id = u-your-user-id
        token = t-your-token
        secret = your-secret

    :type user_id: str
    :param user_id: catapult user id
    :type token: str
    :param token: catapult token
    :type secret: str
    :param secret: catapult secret
    :rtype: RESTClientObject
    :returns: bandwidth rest client
    """
    global _global_client

    if any((user_id, token, secret)):
        # at least one keyword argument was specified, require that all are
        # given or raise an error.
        if not all((user_id, token, secret)):
            raise ValueError('{}{}'.format(
                _HELP_MISSING_PARAMS, Client.__doc__
            ))

    elif 'BANDWIDTH_USER_ID' in os.environ:
        # attempt to load config from environment variables.  If environment
        # variables are only partially set then raise an error
        user_id = os.environ.get('BANDWIDTH_USER_ID')
        token = os.environ.get('BANDWIDTH_API_TOKEN')
        secret = os.environ.get('BANDWIDTH_API_SECRET')

        if not all((user_id, token, secret)):
            raise EnvironmentError('{}{}'.format(
                _HELP_MISSING_ENV_VARS, Client.__doc__
            ))

    elif 'BANDWIDTH_CONFIG_FILE' in os.environ:
        # attempt to get the credentials from a user defined config file
        config_path = os.environ.get('BANDWIDTH_CONFIG_FILE')
        if file_exists(config_path):
            user_id, token, secret = _load_config(config_path)
        else:
            raise ValueError('{}{}'.format(
                _HELP_CONFIG_FILE_MISSING % config_path, Client.__doc__
            ))

    elif file_exists('.bndsdkrc'):
        # attempt to get credentials from a config file in cwd
        config_path = '.bndsdkrc'
        user_id, token, secret = _load_config(config_path)

    elif bandwidth_sdk.user_id is not None:
        user_id = bandwidth_sdk.user_id
        token = bandwidth_sdk.api_token
        secret = bandwidth_sdk.api_secret

    else:
        # could not locate configuration variables, raise an error
        raise ValueError('No configuration provided. {}'.format(Client.__doc__))

    _global_client = RESTClientObject(user_id, (token, secret))
    return _global_client


_HELP_MISSING_IRIS_ENV_VARS = '' \
    'If BANDWIDTH_ACCOUNT_ID is defined in the environment, ' \
    'BANDWIDTH_USERNAME and BANDWIDTH_PASSWORD must also be defined'

_HELP_MISSING_IRIS_PARAMS = '' \
    'Creating iris_client with arguments requires: iris_client(account_id, username, password) ' \
    'where user_id, token, secret are from your Catapult account.'


def _iris_client(account_id='', username='', password=''):
    """
    Initialize the bandwidth sdk client for bandwidth dashboard (aka iris) api calls.  This function will attempt to
    gather credentials from one of several different locations in the
    following order:

    1) Included as arguments when creating the client::

        bandwidth = bandwidth_sdk.iris_client(
            account_id='your-bandwidth-dashboard-account_id',
            username='your-bandwidth-dashboard-username',
            password='your-bandwidth-dashboard-password')

    2) environment variables::

        $ export BANDWIDTH_ACCOUNT_ID=your-account-id
        $ export BANDWIDTH_USERNAME=t-your-username
        $ export BANDWIDTH_PASSWORD=your-password

    3) The sdk will attempt to load credentials from a configuration
       file specified with env var BANDWIDTH_CONFIG_FILE else .bndsdkrc is
       searched for in the current directory. The config file has the following
       format::

        $ export BANDWIDTH_CONFIG_FILE=/home/user/.bndsdkrc
        $ cat /home/user/.bndsdkrc
        [catapult]
        account_id = dashboard account id
        username = dashboard username
        password = dashboard password

    4) Finally the sdk will look for credentials in a module variable. You can set these as follows:

        bandwidth_sdk.account_id='dashboard account id'
        bandwidth_sdk.username='dashboard username'
        bandwidth_sdk.password='dashboard password'

    :type account_id: str
    :param account_id: dashboard account id
    :type username: str
    :param username: dashboard username
    :type password: str
    :param password: dashboard password
    :rtype: RESTClientObject
    :returns: bandwidth rest client
    """

    IRIS_ENDPOINT = 'https://dashboard.bandwidth.com:443/v1.0/'

    if any((account_id, username, password)):
        # at least one keyword argument was specified, require that all are
        # given or raise an error.
        if not all((account_id, username, password)):
            raise ValueError('{}{}'.format(
                _HELP_MISSING_PARAMS, _iris_client.__doc__
            ))

        bandwidth_sdk.account_id = account_id
        bandwidth_sdk.username = username
        bandwidth_sdk.password = password

    elif 'BANDWIDTH_ACCOUNT_ID' in os.environ:
        # attempt to load config from environment variables.  If environment
        # variables are only partially set then raise an error
        user_id = os.environ.get('BANDWIDTH_ACCOUNT_ID')
        token = os.environ.get('BANDWIDTH_USERNAME')
        secret = os.environ.get('BANDWIDTH_PASSWORD')

        if not all((user_id, token, secret)):
            raise EnvironmentError('{}{}'.format(
                _HELP_MISSING_IRIS_ENV_VARS, _iris_client.__doc__
            ))

        bandwidth_sdk.account_id = account_id
        bandwidth_sdk.username = username
        bandwidth_sdk.password = password

    elif 'BANDWIDTH_CONFIG_FILE' in os.environ:
        # attempt to get the credentials from a user defined config file
        config_path = os.environ.get('BANDWIDTH_CONFIG_FILE')
        if file_exists(config_path):
            account_id, username, password = _load_config(config_path)

            bandwidth_sdk.account_id = account_id
            bandwidth_sdk.username = username
            bandwidth_sdk.password = password
        else:
            raise ValueError('{}{}'.format(
                _HELP_CONFIG_FILE_MISSING % config_path, _iris_client.__doc__
            ))

    elif file_exists('.bndsdkrc'):
        # attempt to get credentials from a config file in cwd
        config_path = '.bndsdkrc'
        account_id, username, password = _load_config(config_path)

        bandwidth_sdk.account_id = account_id
        bandwidth_sdk.username = username
        bandwidth_sdk.password = password

    elif bandwidth_sdk.account_id is not None:

        account_id = bandwidth_sdk.account_id
        username = bandwidth_sdk.username
        password = bandwidth_sdk.password

        if not all((account_id, username, password)):
            raise EnvironmentError('{}{}'.format(
                _HELP_MISSING_ENV_VARS, _iris_client.__doc__
            ))

    else:
        # could not locate configuration variables, raise an error
        raise ValueError('No configuration provided. {}'.format(_iris_client.__doc__))

    if bandwidth_sdk.iris_endpoint is not None:
        _endpoint = bandwidth_sdk.iris_endpoint
    else:
        _endpoint = IRIS_ENDPOINT

    return RESTClientObject(account_id, (username, password), endpoint=_endpoint, xml=True)


def _load_config(config_path):
    try:
        return get_creds_from_file(config_path)
    except configparser.Error:
        raise ValueError('{}{}'.format(
            _HELP_CONFIG_FORMAT % config_path, Client.__doc__
        ))


def get_client():
    global _global_client
    if not _global_client:
        return Client()
    return _global_client


def get_iris_client():
    return _iris_client()


def set_client(client):
    """
    Set the global HTTP client for sdk.
    Returns previous client.
    """
    global _global_client
    previous = _global_client
    _global_client = client
    return previous

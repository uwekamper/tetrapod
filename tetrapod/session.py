import os
import logging

from . import podio_auth


log = logging.getLogger(__file__)


def try_environment_token():
    """
    Try to get the token from the environment variables TETRAPOD_CLIENT_ID and TETRAPOD_ACCESS_TOKEN.
    :return:
    """
    try:
        client_id = os.environ['TETRAPOD_CLIENT_ID']
        access_token = os.environ['TETRAPOD_ACCESS_TOKEN']
    except KeyError as e:
        log.info('Environment variables TETRAPOD_CLIENT_ID and TETRAPOD_ACCESS_TOKEN not set.')
        return None
    log.info('Loading OAuth2 token from environment.')
    return {
      "access_token": str(access_token),
      "client_id": str(client_id),
      "token_type": "bearer"
    }


def create_podio_session(credentials_file=None, credentials=None, check=True):
    token = try_environment_token()
    if token is None:
        log.info('Loading OAuth2 token from credentials file.')
        token = podio_auth.load_token()
    podio = podio_auth.make_client(token['client_id'], token)
    return podio


def create_app_auth_session(client_id:str, client_secret:str, app_id:int, app_token:str):
    return podio_auth.make_app_auth_client(client_id, client_secret, app_id, app_token)
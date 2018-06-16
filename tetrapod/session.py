from . import podio_auth


def create_podio_session(credentials_file=None, credentials=None, check=True):
    token = podio_auth.load_token()
    podio = podio_auth.make_client(token['client_id'], token)
    return podio
import sqlite3
from tetrapod.podio_auth import PodioOAuth2Session


class CachedItemFactory(object):
    """
    One object to connect a PodioOauth2Session and a SQLite3 database together.

    Example:
    >>> import sqlite3
    >>> from tetrapod.session import create_podio_session
    >>> podio = create_podio_session()
    >>> conn = sqlite3.connect('database.sqlite3')
    >>> factory = CachedItemFactory(conn, podio)
    >>> factory.get_item(12929939)
    """

    def __init__(self, conn:sqlite3.Connection, podio:PodioOAuth2Session):
        self.conn = conn
        self.podio = podio



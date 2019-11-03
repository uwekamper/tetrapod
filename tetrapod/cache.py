import json
import sqlite3

from tetrapod.helpers import iterate_resource
from tetrapod.items import Item
from tetrapod.podio_auth import PodioOAuth2Session


class CachedItem(Item):

    def __init__(self, item_storage, item_data):
        self._item_storage = item_storage
        super().__init__(item_data)

    def get_podio_session(self):
        return self._item_storage.podio

    def save(self):
        podio = self.get_podio_session()
        podio_dict = self.as_podio_dict(fields=self._tainted)
        resp = podio.put(
            f'https://api.podio.com/item/{self.item_id}/value',
            json=podio_dict
        )
        self._item_storage.update_item(item=self)



class CachedItemStorage(object):
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

    def get_item(self, app_id: int, item_id: int):
        table_name = f'podio_app_{app_id}'

        with self.conn.cursor() as cursor:
            sql = """SELECT item_data FROM ? WHERE item_id = ?"""
            vars = (table_name, item_id)
            cursor.execute(sql, vars)
            item_data = json.loads(cursor.fetchone()[0])
            item = CachedItem(item_storage=self, item_data=item_data)
            return item

    def update_item(self, item):
        table_name = f'podio_app_{item.app_id}'

        with self.conn.cursor() as cursor:
            sql = """UPDATE ? SET item_data = ? WHERE item_id = ?"""
            vars = (table_name, json.dumps(item.get_item_data()), item.item_id)
            cursor.execute(sql, vars)
        self.conn.commit()

    def cache_app(self, podio_app_id: int, join_fields, natural_key):
        """
        Create a local copy of all the items in one app.
        """
        table_name = 'podio_app_%d' % podio_app_id
        cols = [
            'item_id INT PRIMARY KEY NOT NULL',
            'item_data TEXT NULL',
        ]
        if natural_key:
            cols.append('__natural_key TEXT NULL')

        for field_name in join_fields:
            cols.append('%s TEXT NULL' % field_name)
        cols_sql = ",\n".join(cols)
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS %s ('
            '%s'
            ');' % (table_name, cols_sql)
        )
        self.conn.commit()
        url = "https://api.podio.com/item/app/%d/filter/" % podio_app_id
        all_items = iterate_resource(self.podio, url, limit=300)
        for item_data in all_items:
            item = Item(item_data)

            # determine the value of the natural key

            # item-ID and json-dump of the whole item go first.
            values = [item_data['item_id'], json.dumps(item_data)]

            if natural_key:
                nat_key_val = item[natural_key]
                values.append(nat_key_val)

            for field_name in join_fields:
                values.append('%s' % item[field_name])

            # create enough questionsmarks for the SQL
            placeholders = ', '.join('?' * len(values))
            self.conn.execute('INSERT INTO %s VALUES (%s)' % (table_name, placeholders),
                         values)
            self.conn.commit()
        self.conn.commit()
        if natural_key:
            print('CREATE UNIQUE INDEX idx_natural_key ON %s(__natural_key)' % table_name)
            self.conn.execute('CREATE UNIQUE INDEX idx_natural_key ON %s(__natural_key)' % table_name)
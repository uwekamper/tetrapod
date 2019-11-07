import os
import json
from unittest import TestCase
import datetime

from tetrapod.items import (
    fetch_field,
    Item,
)


class TestFetchField(TestCase):
    def setUp(self):
        json_path = os.path.join(os.path.dirname(__file__), 'test_item.json')
        with open(json_path, mode='r') as fh:
            self.test_item = json.load(fh)

    def test_get_field_not_found(self):
        self.assertEquals(
            None,
            fetch_field('does_not_exist', self.test_item)
        )

    def test_get_field_with_underscore(self):
        self.assertEquals(
            'Go',
            fetch_field('do_it', self.test_item)
        )

    def test_get_text_field(self):
        self.assertEquals(
            "Bow of boat",
            fetch_field('name', self.test_item)
        )

    def test_get_text_field_multiline(self):
        self.assertEquals(
            "<p>There's something about knowing the bow from the stern that "
            "makes sense in regard to this project.</p>",
            fetch_field('description', self.test_item)
        )

    def test_fetch_category_field(self):
        self.assertEqual(
            [(1, "Entered"), (2, "Accepted"), (3, "Rejected")],
            fetch_field('status2__choices', self.test_item)
        )
        self.assertEqual(
            "Accepted",
            fetch_field('status2', self.test_item)
        )
        self.assertEqual(
            "Accepted",
            fetch_field('status2__active', self.test_item)['text']
        )
        self.assertEqual(
            2,
            fetch_field('status2__active', self.test_item)['id']
        )
        self.assertEqual(
            "DCEBD8",
            fetch_field('status2__active', self.test_item)['color']
        )

    def test_fetch_app_field(self):
        self.assertEqual(
            [503454054],
            fetch_field('projects', self.test_item)
        )
        # self.assertEqual(
        #     503454054,
        #    fetch_field('projects__first', self.test_item)
        #)
        #self.assertEqual(
        #    503454054,
        #    fetch_field('projects__last', self.test_item)
        #)

    def test_fetch_calculation_field(self):
        self.assertEqual(
            "Hello,  John Doe",
            fetch_field('calc', self.test_item)
        )

    def test_fetch_date_field(self):
        self.assertEqual(
            '2018-07-27 01:00:00',
            fetch_field('date', self.test_item)
        )
        self.assertEqual(
            datetime.datetime(2018, 7, 27, 1, 0),
            fetch_field('date__datetime', self.test_item)
        )

    def test_fetch_embed_field(self):
        self.assertEqual(
            "http://www.newsletter-webversion.de/?c=0-v0yw-0-11xa&utm_source=newsletter&utm_medium=email&utm_campaign=02%2F2017+DT&newsletter=02%2F2017+DT",
            fetch_field('embed', self.test_item)
        )


class TestItem(TestCase):

    def setUp(self):
        json_path = os.path.join(os.path.dirname(__file__), 'test_item.json')
        with open(json_path, mode='r') as fh:
            self.test_item = json.load(fh)
        self.item = Item(item_data=self.test_item)

    def test__getitem__(self):
        self.assertEquals(
            "Bow of boat",
            self.item['name']
        )

    def test__setitem__(self):
        self.assertEqual(0, len(self.item._tainted))
        self.item['name'] = 'Bow of ship'
        # after setting the value, the number of tainted fields should go up.
        self.assertEqual(1, len(self.item._tainted))
        res = self.item.as_podio_dict(fields=self.item._tainted)
        self.assertEqual("Bow of ship", res['name'][0]['value'])

    def test_as_podio_dict(self):
        res = self.item.as_podio_dict(fields=['name'])
        self.assertEqual("Bow of boat", res['name'][0]['value'])


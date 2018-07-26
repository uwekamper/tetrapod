import json
import os
from unittest import TestCase
import datetime

from tetrapod.helpers import (
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
            503454054,
            fetch_field('projects', self.test_item)['item_id']
        )
        self.assertEqual(
            503454054,
            fetch_field('projects__all', self.test_item)[0]['item_id']
        )

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
            datetime.datetime(2018, 7, 27),
            fetch_field('date__datetime', self.test_item)
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
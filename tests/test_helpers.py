import json
import os
from unittest import TestCase

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
        self.assertEquals(
            "Accepted",
            fetch_field('status2', self.test_item)['text']
        )
        self.assertEquals(
            2,
            fetch_field('status2', self.test_item)['id']
        )
        self.assertEquals(
            "DCEBD8",
            fetch_field('status2', self.test_item)['color']
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
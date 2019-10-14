import json
import os
from unittest import TestCase

from tetrapod.podio_auth import make_client
from tetrapod.session import create_podio_session


class TestPodioOAuthSession(TestCase):
    def setUp(self):
        self.podio = create_podio_session(robust=True)

    def test_make_request(self):
        resp = self.podio.get('https://api.podio.com/user/status')
        print(resp.json())

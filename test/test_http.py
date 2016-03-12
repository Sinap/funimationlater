# -*- coding: utf-8 -*-
import unittest
import json
import funimationlater.http as http


class TestHTTPClient(unittest.TestCase):
    def test_get_request_headers(self):
        client = http.HTTPClient('https://httpbin.org', lambda x: json.loads(x))
        resp = client.get('/headers')
        self.assertDictContainsSubset(client.headers, resp['headers'])

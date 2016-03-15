# -*- coding: utf-8 -*-
import unittest
import mock
import urllib2
import urllib
import funimationlater.http as http


class TestHTTPClient(unittest.TestCase):
    def test_get_request(self):
        with mock.patch('http.urllib2.urlopen') as urlopen:
            client = http.HTTPClient('https://foo.bar', lambda x: x)
            header = {'Foo': 'bar'}
            client.add_headers(header)
            client.get('/')
            self.assertTrue(urlopen.called)
            request = urlopen.call_args[0][0]
            self.assertIsInstance(urlopen.call_args[0][0], urllib2.Request)
            self.assertDictContainsSubset(header, request.headers)

    def test_post_request(self):
        with mock.patch('http.urllib2.urlopen') as urlopen:
            client = http.HTTPClient('https://foo.bar', lambda x: x)
            expected_payload = {'foo': 'bar'}
            header = {'Foo': 'bar'}
            client.add_headers(header)
            client.post('/', expected_payload)
            self.assertTrue(urlopen.called)
            request = urlopen.call_args[0][0]
            actual_payload = urlopen.call_args[0][1]
            self.assertEqual(urllib.urlencode(expected_payload), actual_payload)
            self.assertIsInstance(urlopen.call_args[0][0], urllib2.Request)
            self.assertDictContainsSubset(header, request.headers)

    def test_add_headers(self):
        client = http.HTTPClient('https://foo.bar')
        header = {'Foo': 'Bar'}
        client.add_headers(header)
        self.assertDictContainsSubset(header, client.headers)

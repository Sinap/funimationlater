# -*- coding: utf-8 -*-
import unittest
try:
    from urllib.parse import urlencode
    from urllib.request import Request
except ImportError:
    from urllib import urlencode
    from urllib2 import Request
from io import StringIO

import mock

import funimationlater.httpclient as http
from funimationlater.response_handler import NullHandler


def extract_dict1_from_dict2(dict1, dict2):
    return {k: dict2[k] for k in dict1.keys() if k in dict2.keys()}


class TestHTTPClient(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.host = 'https://foo.bar'

    def test_get_request(self):
        with mock.patch('funimationlater.httpclient.urlopen') as opener:
            client = http.HTTPClient(self.host, NullHandler)
            header = {'Foo': 'bar'}
            client.add_headers(header)
            client.get('/')
            self.assertTrue(opener.called)
            request = opener.call_args[0][0]
            self.assertIsInstance(request, Request)
            self.assertEqual(
                header, extract_dict1_from_dict2(header, request.headers))

    def test_get_request_with_query_string(self):
        with mock.patch('funimationlater.httpclient.urlopen') as opener:
            uri = '/foobar'
            qry = {'foo': 'bar'}
            client = http.HTTPClient(self.host, NullHandler)
            client.get(uri, qry)
            self.assertTrue(opener.called)
            request = opener.call_args[0][0]
            self.assertIsInstance(request, Request)
            self.assertEqual(request.get_full_url(),
                             '{}{}?{}'.format(self.host, uri, urlencode(qry)))

    def test_post_request(self):
        with mock.patch('funimationlater.httpclient.urlopen') as opener:
            client = http.HTTPClient(self.host, NullHandler)
            expected_payload = {'foo': 'bar'}
            header = {'Foo': 'bar'}
            client.add_headers(header)
            client.post('/', expected_payload)
            self.assertTrue(opener.called)
            request = opener.call_args[0][0]
            actual_payload = opener.call_args[0][1]
            self.assertEqual(urlencode(expected_payload), actual_payload)
            self.assertIsInstance(request, Request)

    def test_add_headers(self):
        client = http.HTTPClient(self.host)
        header = {'Foo': 'Bar'}
        client.add_headers(header)
        self.assertEqual(
            header, extract_dict1_from_dict2(header, client.headers))

    def test_add_bad_headers(self):
        client = http.HTTPClient(self.host)
        header = 'foo=bar'
        self.assertRaises(TypeError, client.add_headers, header)

    def test_build_url_correctly(self):
        with mock.patch('funimationlater.httpclient.urlopen') as opener:
            uri = 'foobar'
            client = http.HTTPClient(self.host, NullHandler)
            client.get(uri)
            self.assertTrue(opener.called)
            request = opener.call_args[0][0]
            self.assertIsInstance(request, Request)
            self.assertEqual(request.get_full_url(),
                             '{}/{}'.format(self.host, uri))

    def test_xml_response_handling(self):
        with mock.patch('funimationlater.httpclient.urlopen') as opener:
            uri = '/foobar'
            expected = {'foo': {'bar': {'#text': 'fiz', '@bang': 'foo'}}}
            opener.return_value = StringIO(
                u'<foo><bar bang="foo">fiz</bar></foo>')
            client = http.HTTPClient(self.host)
            actual = dict(client.get(uri))
            self.assertTrue(opener.called)
            request = opener.call_args[0][0]
            self.assertIsInstance(request, Request)
            self.assertIsInstance(actual, dict)
            self.assertEqual(actual, expected)

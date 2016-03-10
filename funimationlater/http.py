# -*- coding: utf-8 -*-
import urllib2
from urllib import urlencode

from utils import etree_to_dict


class XMLToDictResponseMixin(object):
    @staticmethod
    def handle_response(data):
        """
        Args:
            data (str):

        Returns:
            dict:
        """
        return etree_to_dict(data)


class HTTPClient(XMLToDictResponseMixin):
    def __init__(self, host):
        """
        Args:
            host (str):
        """
        super(HTTPClient, self).__init__()
        self.host = host
        self.headers = {'Accept-Encoding': 'gzip, deflate'}

    def get(self, uri, query_str=None):
        """
        Args:
            query_str (dict):
            uri (str):

        Returns:
            dict:
        """
        if query_str:
            req = self.create_request(uri + urlencode(query_str))
        else:
            req = self.create_request(uri)
        resp = urllib2.urlopen(req)
        return self.handle_response(resp.read())

    def post(self, uri, data):
        """Send a post request to the `uri`

        Args:
            uri (str):
            data (dict): data is urlencoded before send the request

        Returns:
            dict:
        """
        resp = urllib2.urlopen(self.create_request(uri), urlencode(data))
        return self.handle_response(resp.read())

    def add_headers(self, headers):
        """Add headers to all requests.

        Args:
            headers (dict):
        """
        if not isinstance(headers, dict):
            raise TypeError('argument must be of type `dict`')
        self.headers.update(headers)

    def create_request(self, uri):
        """Builds :class:`urllib2.Request` instance with `self.headers`
        Args:
            uri (str):

        Returns:
            urllib2.Request:
        """
        return urllib2.Request(self._build_url(uri), headers=self.headers)

    def _build_url(self, uri):
        if uri[0] == '/':
            return self.host + uri
        else:
            return self.host + '/' + uri

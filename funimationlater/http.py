# -*- coding: utf-8 -*-
import cookielib
import urllib2
from urllib import urlencode
import requests
from utils import etree_to_dict


class XMLToDictMixin(object):
    @staticmethod
    def handle_response(data):
        """
        Args:
            data (str):

        Returns:
            dict:
        """
        return etree_to_dict(str(data))


class HTTPClient(XMLToDictMixin):
    def __init__(self, host):
        """
        Args:
            host (str):
        """
        super(HTTPClient, self).__init__()
        self.host = host
        self.cj = cookielib.CookieJar()
        self.headers = list()
        self._add_header(('Accept-Encoding', 'gzip, deflate'))

    def get(self, uri):
        """
        Args:
            uri (str):

        Returns:
            dict:
        """
        resp = requests.get(self._build_url(uri))
        return self.handle_response(resp.text)

    def post(self, uri, payload=None):
        """
        Args:
            uri (str):
            payload (dict):

        Returns:
            dict:
        """
        if payload is None:
            payload = ''
        resp = requests.post(url=self._build_url(uri), data=payload)
        return self.handle_response(resp.text)

    def add_headers(self, header):
        """
        Args:
            header ([dict,list,tuple]):
        """
        if isinstance(header, dict):
            for k, v in header.iteritems():
                self._add_header((k, v))
        elif isinstance(header, list):
            for h in header:
                self._add_header(h)
        elif isinstance(header, tuple):
            self._add_header(header)

    def _build_url(self, uri):
        if uri[0] == '/':
            return self.host + uri
        else:
            return self.host + '/' + uri

    def _add_header(self, header):
        """
        Args:
            header (tuple):
        """
        if header not in self.headers:
            self.headers.append(header)

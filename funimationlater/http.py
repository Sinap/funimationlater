# -*- coding: utf-8 -*-
import cookielib
import urllib2
from urllib import urlencode

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
        return etree_to_dict(data)


class HTTPClient(XMLToDictMixin):
    def __init__(self, host):
        """
        Args:
            host (str):
        """
        super(HTTPClient, self).__init__()
        self.host = host
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        self._add_header(('Accept-Encoding', 'gzip, deflate'))

    def get(self, uri):
        """
        Args:
            uri (str):

        Returns:
            dict:
        """
        resp = self.opener.open(self._build_url(uri))
        return self.handle_response(resp.read())

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
        resp = self.opener.open(self._build_url(uri), urlencode(payload))
        return self.handle_response(resp.read())

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
        if header not in self.opener.addheaders:
            self.opener.addheaders.append(header)

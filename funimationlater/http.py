# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
import urllib2
from urllib import urlencode

from funimationlater.utils import etree_to_dict, CaseInsensitiveDict
__all__ = ['HTTPClientBase', 'HTTPClient', 'ResponseHandler', 'XMLResponse',
           'NullHandler']


class ResponseHandler(object):
    def __init__(self, resp, req):
        """
        Args:
            resp (str):
            req (urllib2.Request):
        """
        super(ResponseHandler, self).__init__()
        self._resp = resp
        self._req = req

    def handle(self):
        raise NotImplementedError


class NullHandler(ResponseHandler):
    def handle(self):
        return self._resp


class XMLResponse(ResponseHandler):
    def handle(self):
        data = etree_to_dict(self._resp)
        return CaseInsensitiveDict(data)


class HTTPClientBase(object):
    def __init__(self, host):
        super(HTTPClientBase, self).__init__()
        self.host = host

    def get(self, uri):
        raise NotImplementedError

    def post(self, uri, data):
        raise NotImplementedError

    def add_headers(self, headers):
        raise NotImplementedError


class HTTPClient(HTTPClientBase):
    """Used to handle POST and GET requests.

    This class really just handles building the request and transforming the
    response.

    Attributes:
        host (str): This will be used when building the URL.
        headers (dict): The headers that are sent in the requests.
        handle_response: This function is called for all requests and is passed
            the results of the request as a string.
    """

    def __init__(self, host, response_handler=None):
        """Init the HTTPClient

        Args:
            host (str): This is usually a domain.
            response_handler: This function must take 1 argument and return
                something.
        """
        super(HTTPClient, self).__init__(host)
        self.headers = {
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Python:FunimationLater:v0.0.1'
        }
        if response_handler is None:
            self.handle_response = XMLResponse
        else:
            self.handle_response = response_handler
        self._log = logging.getLogger(__name__)

    def get(self, uri, qry=None):
        """Send a GET request to `host` + `uri`

        Args:
            uri (str): This will be concatenated to `host`.
            qry ([dict]): Optional query string to add to the URL.

        Returns: Whatever is returned by `handle_response`.
        """
        if qry:
            query = urlencode(qry) if isinstance(qry, dict) else qry
            uri = '{}?{}'.format(uri, query)
        return self._request(uri)

    def post(self, uri, data):
        """Send a POST request to `host` + `uri` with `data` as the body.

        Args:
            uri (str): This will be concatenated to `host`.
            data (dict): Data is urlencoded before the request is sent.

        Returns: Whatever is returned by `handle_response`.
        """
        return self._request(uri, urlencode(data))

    def add_headers(self, headers):
        """Add headers to all requests.

        Args:
            headers (dict): Will overwrite existing keys
        """
        if not isinstance(headers, dict):
            raise TypeError('argument must be of type `dict`')
        self.headers.update(headers)

    def _request(self, uri, data=None):
        req = self._create_request(uri)
        resp = urllib2.urlopen(req, data)
        handler = self.handle_response(resp.read(), req)
        return handler.handle()

    def _create_request(self, uri):
        """Builds :class:`urllib2.Request` object using `uri` and sets the
        headers to `headers`.

        Args:
            uri (str): This will be concatenated to `host`

        Returns:
            urllib2.Request: A request object that will be used by
                :class:`urllib2.urlopen`
        """
        req = urllib2.Request(self._build_url(uri), headers=self.headers)
        self._log.debug(
            'Calling %s on %s', req.get_method(), req.get_full_url())
        return req

    def _build_url(self, uri):
        if uri[0] == '/':
            return self.host + uri
        else:
            return self.host + '/' + uri

# -*- coding: utf-8 -*-
import urllib2
import logging
from urllib import urlencode

from utils import etree_to_dict, CaseInsensitiveDict

log = logging.getLogger(__name__)


def xml_response(data):
    resp = etree_to_dict(data)
    return CaseInsensitiveDict(resp)


class HTTPClient(object):
    """Used to handle POST and GET requests.

    This class really just handles building the request and transforming the
    response.

    Attributes:
        host (str): This will be used when building the URL.
        headers (dict): The headers that are sent in the requests.
        handle_response: This function is called for all requests and is passed
            the results of the request as a string.
    """

    def __init__(self, host, response_handler=xml_response):
        """Init the HTTPClient

        Args:
            host (str): This is usually a domain.
            response_handler: This function must take 1 argument and return
                something.
        """
        super(HTTPClient, self).__init__()
        self.host = host
        self.headers = {
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Python:FunimationLater:v0.0.1'
        }
        self.handle_response = response_handler

    def get(self, uri, query_str=None):
        """Send a GET request to `host` + `uri`

        Args:
            uri (str): This will be concatenated to `host`.
            query_str ([dict]): Optional query string to add to the URL.

        Returns: Whatever is returned by `handle_response`.
        """
        if query_str:
            query = urlencode(query_str) if isinstance(query_str,
                                                       dict) else query_str
            req = self.create_request('{}?{}'.format(uri, query))
        else:
            req = self.create_request(uri)
        log.debug(
            'Calling {} on {}'.format(req.get_method(), req.get_full_url()))
        resp = urllib2.urlopen(req)
        return self.handle_response(resp.read())

    def post(self, uri, data):
        """Send a POST request to `host` + `uri` with `data` as the body.

        Args:
            uri (str): This will be concatenated to `host`.
            data (dict): Data is urlencoded before the request is sent.

        Returns: Whatever is returned by `handle_response`.
        """
        resp = urllib2.urlopen(self.create_request(uri), urlencode(data))
        return self.handle_response(resp.read())

    def add_headers(self, headers):
        """Add headers to all requests.

        Args:
            headers (dict): Will overwrite existing keys
        """
        if not isinstance(headers, dict):
            raise TypeError('argument must be of type `dict`')
        self.headers.update(headers)

    def create_request(self, uri):
        """Builds :class:`urllib2.Request` object using `uri` and sets the
        headers to `headers`.

        Args:
            uri (str): This will be concatenated to `host`

        Returns:
            urllib2.Request: A request object that will be used by
                :class:`urllib2.urlopen`
        """
        return urllib2.Request(self._build_url(uri), headers=self.headers)

    def _build_url(self, uri):
        if uri[0] == '/':
            return self.host + uri
        else:
            return self.host + '/' + uri

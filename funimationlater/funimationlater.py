# -*- coding: utf-8 -*-
from functools import wraps

from .error import (UnknowResponse, LoginRequired,
                    AuthenticationFailed)
from .http import HTTPClient, HTTPClientBase
from .models import Show
from .constants import ShowTypes, SortBy

__all__ = ['FunimationLater']


def require_login(func):
    """Decorator that throws an error when user isn't logged in.

    Args:
        func: The function to wrap
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # args[0] will always be self
        if not args[0].logged_in:
            raise LoginRequired('must be logged in')
        return func(*args, **kwargs)

    return wrapper


class FunimationLater(object):
    host = 'api-funimation.dadcdigital.com'
    base_path = '/xml'
    protocol = 'https'
    default_limit = 20

    def __init__(self, username=None, password=None, http_client=None):
        """
        Args:
            username (str):
            password (str):
            http_client: Must be an instance of HTTPClient
        """
        full_url = '{}://{}{}'.format(self.protocol, self.host, self.base_path)
        if http_client is None:
            self.client = HTTPClient(full_url)
        else:
            # NOTE(Sinap): using assert instead of raise here because we should
            # never use a client that is not a subclass of HTTPClientBase.
            assert issubclass(http_client, HTTPClientBase), \
                'http_client must be a subclass of HTTPClientBase'
            self.client = http_client(full_url)
        self.logged_in = False
        if username and password:
            self.login(username, password)

    def login(self, username, password):
        """Login and set the authentication headers
        Args:
            username (str):
            password (str):
        """
        resp = self.client.post('/auth/login/?',
                                {'username': username, 'password': password})
        if 'error' in resp['authentication']:
            raise AuthenticationFailed('username or password is incorrect')
        # the API returns what headers should be set
        self.client.add_headers(resp['authentication']['parameters']['header'])
        self.logged_in = True

    @require_login
    def get_my_queue(self):
        """Get the list of shows in the current users queue
        Returns:
            list[Show]:
        """
        resp = self.client.get('/myqueue/get-items/?')
        if resp['watchlist']['items'] is not None:
            return [Show(x['item'], self.client) for x in
                    resp['watchlist']['items']['item']]
        else:
            return []

    @require_login
    def add_to_queue(self, show_id):
        self.client.get('/myqueue/add/', {'id': show_id})

    @require_login
    def remove_from_queue(self, show_id):
        self.client.get('/myqueue/remove/', {'id': show_id})

    @require_login
    def get_history(self):
        resp = self.client.get('/history/get-items/?')
        if 'watchlist' in resp:
            return [Show(x['item'], self.client) for x in
                    resp['watchlist']['items']['historyitem']]
        raise UnknowResponse(resp)

    def get_shows(self, show_type, sort_by=SortBy.TITLE, sort_order='desc',
                  limit=default_limit, offset=0, **kwargs):
        """
        Args:
            show_type (str): simulcasts, broadcast-dubs, genre
            sort_by:
            sort_order:
            offset (int):
            limit (int):

        Returns:
            list([Show]):
        """
        resp = self._get_content(
            id=show_type,
            sort=sort_by,
            sort_direction=sort_order,
            itemThemes='dateAddedShow',
            territory='US',
            role='g',
            offset=offset,
            limit=limit,
            **kwargs
        )
        return resp

    def search(self, query):
        """Perform a search

        Args:
            query (str): The query string

        Returns:
            list: a list of results
        """
        resp = self.get_shows(ShowTypes.SEARCH, q=query)
        return resp

    def get_all_shows(self):
        shows = self.get_shows(ShowTypes.SHOWS, limit=99999)
        if shows is None:
            return []
        else:
            return shows

    def get_simulcasts(self, limit=default_limit, offset=0):
        shows = self.get_shows(ShowTypes.SIMULCAST, limit, offset)
        if shows is None:
            return []
        else:
            return shows

    def _get_content(self, **kwargs):
        resp = self.client.get('/longlist/content/page/', kwargs)['items']
        if isinstance(resp, (tuple, str)):
            return None
        resp = resp['item']
        if isinstance(resp, list):
            return [Show(x, self.client) for x in resp]
        else:
            return [Show(resp, self.client)]

    def __iter__(self):
        offset = 0
        limit = self.default_limit
        while True:
            shows = self.get_shows(ShowTypes.SHOWS, limit=limit, offset=offset)
            for show in shows:
                yield show
            if len(shows) < limit:
                break
            offset += limit

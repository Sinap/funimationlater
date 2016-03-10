# -*- coding: utf-8 -*-
from http import HTTPClient
from functools import wraps

__all__ = ['FunimationLater', 'AuthenticationFailed', 'Show', 'Video']


# NOTE(Sinap): the errors should probably be moved into there own file
class AuthenticationFailed(Exception):
    pass


class LoginRequired(Exception):
    pass


class UnknowResponse(Exception):
    pass


# NOTE(Sinap): these should probably be moved into a different file
class Media(object):
    def __init__(self, data, client):
        """
        Args:
            data (dict): Data about the media.
            client (HTTPClient): An HTTP client.
            Used to make requests from within the media object. e.g
            >>> show = FunimationLater().get_shows('simulcast')[0]
            >>> show[1]  # season 1
            >>> show[1][4]  # season 1 episode 4
        """
        self.title = data['title']
        self.thumbnail = data['thumbnail']['#text']
        self.client = client

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__, self.title)


class Show(Media):
    def __init__(self, data, client):
        super(Show, self).__init__(data, client)
        self.ratings = [(r['#text'], r['@region'])
                        for r in data['ratings']['tv']]
        self.themes = data['themes']
        self.id = data['id']


class Video(Media):
    def __init__(self, data, client):
        super(Video, self).__init__(data, client)
        self.desctription = data['content']['description']
        self.release_year = data['content']['metadata']['releaseYear']
        self.format = data['content']['metadata']['format']


def _require_login(func):
    """Decorator to require the user be logged in to call specific methods"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # args[0] will always be self
        if not args[0].logged_in:
            raise LoginRequired('must be logged in')
        return func(*args, **kwargs)

    return wrapper


class FunimationLater(object):
    def __init__(self):
        """Funimation API"""
        self.client = HTTPClient('https://api-funimation.dadcdigital.com/xml')
        self.logged_in = False

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
        self.client.add_headers(resp['authentication']['parameters']['header'])
        self.logged_in = True

    @_require_login
    def get_my_queue(self):
        """Get the list of shows in the current users queue
        Returns:
            list[Show]:
        """
        resp = self.client.get('/myqueue/get-items/?')
        if 'watchlist' in resp:
            return [Show(x['item'], self.client) for x in
                    resp['watchlist']['items']['item']]
        raise UnknowResponse(resp)

    @_require_login
    def get_history(self):
        resp = self.client.get('/history/get-items/?')
        if 'watchlist' in resp:
            return [Show(x['item'], self.client) for x in
                    resp['watchlist']['items']['historyitem']]
        raise UnknowResponse(resp)

    @_require_login
    def video_details(self, pk):
        """
        Args:
            pk (str):

        Returns:
            Video:
        """
        resp = self.client.get('/detail/?pk={}'.format(pk))
        return Video(resp['list2d']['hero']['item'], self.client)

    def get_shows(self, show_type, offset=0, limit=20):
        """
        Args:
            show_type (str): simulcasts, broadcast-dubs, genre
            offset (int):
            limit (int):

        Returns:

        """
        resp = self._get_content(
            id=show_type,
            sort='start_timestamp',
            sort_direction='desc',
            role='g',  # no idea what this means
            itemThemes='dateAddedShow',
            territory='US',
            offset=offset,
            limit=limit
        )
        return [Show(x, self.client) for x in resp['items']['item']]

    def _get_content(self, **kwargs):
        resp = self.client.get('/longlist/content/page/?', kwargs)
        return resp

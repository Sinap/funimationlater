# -*- coding: utf-8 -*-
import logging
from functools import wraps

from error import *
from http import HTTPClient

__all__ = ['FunimationLater', 'Show', 'Episode', 'Video', 'ShowTypes']

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ShowTypes(object):
    SIMULCAST = 'simulcasts'
    BROADCAST_DUBS = 'broadcast-dubs'
    SEARCH = 'search'
    SHOWS = 'shows'


# NOTE(Sinap): these should probably be moved into a different file
class Media(object):
    def __init__(self, data, client):
        """
        Args:
            data (dict): Data about the media.
            client (HTTPClient): An HTTP client.
        """
        if 'pointer' in data:
            pointer = data['pointer']
            if isinstance(pointer, list):
                self.target = pointer[0]['target']
                self.path = pointer[0]['path']
                self.params = pointer[0]['params']
            else:
                self.target = pointer['target']
                self.path = pointer['path']
                self.params = pointer['params']
        self.title = data['title']
        self.client = client

    def parse_results(self, data):
        """Can't think of a better name
        Args:
            data (dict):
        """
        raise NotImplemented

    def _invoke(self):
        resp = self.client.get(self.path, self.params)
        return self.parse_results(resp[self.target])

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__,
                                 self.title.encode('utf-8'))


class Show(Media):
    def __init__(self, data, client):
        super(Show, self).__init__(data, client)

    def parse_results(self, data):
        return ShowDetails(data, self.client)

    def get_details(self):
        """
        Returns:
            ShowDetails:
        """
        return self._invoke()


class ShowDetails(Media):
    def __init__(self, data, client):
        super(ShowDetails, self).__init__(data, client)
        hero = data['hero']['item']
        content = hero['content']
        self.title = hero['title']
        self.description = content['description']
        self.format = content['metadata']['format']
        self.release_year = content['metadata']['releaseYear']
        self.thumbnail = hero['thumbnail']['#text']
        for thumb in hero['thumbnail']['alternate']:
            if 'ios' in thumb['@platforms']:
                self.thumbnail = thumb['#text']
        # NOTE(Sinap): WHY?!?!
        filter = data['pointer'][0]['longList']['palette']['filter']
        button = filter[0]['choices']['button']
        self.seasons = [(b['title'], b['value']) for b in button]
        self.season = 1

    def get_episodes(self, season=1):
        self.season = season
        self.params = '{}&season={}'.format(self.params, self.season)
        return self._invoke()

    def parse_results(self, data):
        return [Episode(x, self.client) for x in data['items']['item']]


class Episode(Media):
    def __init__(self, data, client):
        super(Episode, self).__init__(data, client)
        content = data['content']
        metadata = content['metadata']
        self.description = content['description']
        self.duration = int(metadata['duration'])
        self.format = metadata['format']
        self.episode_number = int(metadata['episodeNumber'])
        self.languages = metadata['languages'].split(',')

    def parse_results(self, data):
        return Video(data, self.client)


class Video(Media):
    def __init__(self, data, client):
        # this class can probably be combined with Episode because i think
        # all we need from this is the video url
        video = data['item']['video']
        super(Video, self).__init__(video, client)
        self.video_url = data['item']['hls']['url']
        self.id = video['id']
        self.thumbnail = video['thumbnail']
        self.duration = video['content']['metadata']['duration']


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
    ENDPOINT = 'https://api-funimation.dadcdigital.com/xml'

    def __init__(self, username=None, password=None):
        self.client = HTTPClient(self.ENDPOINT)
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
        if 'watchlist' in resp:
            return [Show(x['item'], self.client) for x in
                    resp['watchlist']['items']['item']]
        raise UnknowResponse(resp)

    @require_login
    def get_history(self):
        resp = self.client.get('/history/get-items/?')
        if 'watchlist' in resp:
            return [Show(x['item'], self.client) for x in
                    resp['watchlist']['items']['historyitem']]
        raise UnknowResponse(resp)

    @require_login
    def get_shows(self, show_type=ShowTypes.SHOWS, limit=20, offset=0):
        """
        Args:
            show_type (str): simulcasts, broadcast-dubs, genre
            offset (int):
            limit (int):

        Returns:
            list([Show]):
        """
        resp = self._get_content(
            id=show_type,
            sort='start_timestamp',
            sort_direction='desc',
            itemThemes='dateAddedShow',
            territory='US',
            offset=offset,
            limit=limit
        )
        return [Show(x, self.client) for x in resp['items']['item']]

    def get_all_shows(self, limit=20, offset=0):
        return self.get_shows(ShowTypes.SHOWS, limit, offset)

    def get_simulcasts(self, limit=20, offset=0):
        return self.get_shows(ShowTypes.SIMULCAST, limit, offset)

    def _get_content(self, **kwargs):
        resp = self.client.get('/longlist/content/page/', kwargs)
        return resp

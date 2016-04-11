# -*- coding: utf-8 -*-
from functools import wraps

from .error import (UnknowResponse, LoginRequired, AuthenticationFailed,
                    HTTPError, UnknownShow, UnknownEpisode)
from .http import HTTPClient, HTTPClientBase
from .models import Show, ShowDetails, EpisodeDetails
from .constants import ShowTypes, SortBy, SortOrder

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
            username (str): The users email address
            password (str): The password
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
            username (str): The users email address
            password (str): The password
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
            list[funimationlater.models.Show]:
        """
        resp = self.client.get('/myqueue/get-items/?')
        if resp['watchlist']['items'] is not None:
            return [Show(x['item'], self.client) for x in
                    resp['watchlist']['items']['item']]
        else:
            return []

    @require_login
    def add_to_queue(self, show_stub):
        """Add a show to the current users queue.

        Args:
            show_stub (str): This is a 3 letter code for the show to add.
        """
        self.client.get('myqueue/add/', {'id': show_stub})

    @require_login
    def remove_from_queue(self, show_stub):
        """Remove a show from the current users queue.

        Args:
            show_stub (str): This is a 3 letter code for the show to remove.
        """
        self.client.get('myqueue/remove/', {'id': show_stub})

    @require_login
    def get_history(self):
        """Get the history for the current user.

        Returns:
            list[funimationlater.models.Show]

        Raises:
            funimationlater.error.UnknowResponse:
        """
        resp = self.client.get('/history/get-items/?')
        if 'watchlist' in resp:
            return [Show(x['item'], self.client) for x in
                    resp['watchlist']['items']['historyitem']]
        raise UnknowResponse(resp)

    def get_shows(self, show_type, sort_by=SortBy.TITLE,
                  sort_order=SortOrder.DESC, limit=default_limit, offset=0,
                  **kwargs):
        """

        Args:
            show_type (str): simulcasts, broadcast-dubs, genre
            sort_by (str):
            sort_order (str):
            offset (int):
            limit (int):

        Returns:
            list[funimationlater.models.Show]:
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

    def get_show(self, show_id):
        """Get the :class:`funimationlater.models.ShowDetails` for `show_id`.

        Args:
            show_id (int): The shows numeric ID.

        Returns:
            funimationlater.models.ShowDetails: Returns None if no show exists.
        """
        try:
            resp = self.client.get('detail/', {'pk': show_id})
            if resp:
                return ShowDetails(resp['list2d'], self.client)
        except HTTPError:
            # So we don't need the same code twice, just pass on HTTPError
            # then raise UnknownShow. If it's a different error it should
            # raise that error instead.
            pass
        raise UnknownShow('Show with ID {} not found'.format(show_id))

    def get_episode(self, show_id, episode_id, audio_type=None):
        """Get a specific episodes details.

        Args:
            show_id (int):
            episode_id (int):
            audio_type (Optional[str]):

        Returns:
            funimationlater.models.EpisodeDetails:
        """
        params = {'id': episode_id, 'show': show_id}
        if audio_type is not None:
            params['audio'] = audio_type
        try:
            resp = self.client.get('player/', params)
            if resp:
                return EpisodeDetails(resp['player'], self.client)
        except HTTPError:
            # See get_episodes note.
            pass
        raise UnknownEpisode("Episode ID {} for show {} doesn't exist".format(
            episode_id, show_id))

    def search(self, query):
        """Perform a search using the API.

        Args:
            query (str): The query string

        Returns:
            list[funimationlater.models.Show]: a list of results
        """
        resp = self.get_shows(ShowTypes.SEARCH, q=query)
        return resp

    def get_all_shows(self):
        """Get a list of all shows.

        Returns:
            List[funimationlater.models.Show]:
        """
        # limit=-1 appears to return all shows
        shows = self.get_shows(ShowTypes.SHOWS, limit=-1)
        if shows is None:
            return []
        else:
            return shows

    def get_simulcasts(self):
        """Get a list of all shows being simulcasted.

        NOTE(Sinap): This doesn't appear to be working. You always get the same
                     20 shows even if you set the limit or offset higher, the
                     shows are also old.

        Args:

        Returns:
            list[funimationlater.models.Show]
        """
        shows = self.get_shows(ShowTypes.SIMULCAST)
        return shows

    def _get_content(self, **kwargs):
        resp = self.client.get('/longlist/content/page/', kwargs)['items']
        if not resp or isinstance(resp, (tuple, str)):
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

    def __getitem__(self, item):
        if isinstance(item, int):
            try:
                return self.get_show(item)
            except HTTPError:
                return None
        # NOTE(Sinap): This would allow you to do api['Cowboy Bebop'] but I'm
        #              not sure if I should do that because it could be
        #              confusing if you  can use both the integer index and
        #              a string
        # elif isinstance(item, str):
        #     return self.search(item)

# -*- coding: utf-8 -*-
from __future__ import absolute_import

from .constants import AudioType
from .response_handler import NullHandler
from .error import UnknownSeason, UnknownEpisode

__all__ = ['Media', 'EpisodeContainer', 'Show', 'ShowDetails', 'Season',
           'Episode', 'EpisodeDetails']


class EpisodeContainer(list):
    """The purpose of this class is to return the correct episode number
        when using an index.
    """

    def __getitem__(self, item):
        """Get an episode using index notation.

        Args:
            item (int): The episode number

        Returns:
            Episode: Returns the details of the requested episode

        Raises:
            InvalidEpisode: If the episode doesn't exist
        """
        for episode in self:
            if episode.episode_number == item:
                return episode.get_details()
        raise UnknownEpisode()


class SeasonContainer(list):
    def __getitem__(self, item):
        for season in self:
            if season.title == item:
                return season


class Pointer(object):
    __slots__ = ['target', 'path', 'params', 'themes', 'platforms',
                 'alternates']

    def __init__(self, target, path, params, themes=None, alternates=None,
                 **kwargs):
        self.target = target
        self.path = path
        self.params = params
        self.themes = themes
        self.platforms = kwargs.get('@platforms')
        if isinstance(alternates, list):
            self.alternates = [Pointer(**alt) for alt in alternates]
        elif alternates:
            self.alternates = [Pointer(**alternates)]
        else:
            self.alternates = []


class Thumbnail(object):
    __slots__ = ['url', 'platforms', 'alternates']

    def __init__(self, **kwargs):
        self.url = kwargs.get('#text')
        self.platforms = kwargs.get('@platforms')
        alternates = kwargs.get('alternate')
        if isinstance(alternates, list):
            self.alternates = [Thumbnail(**alt) for alt in alternates]
        elif alternates:
            self.alternates = [Thumbnail(**alternates)]
        else:
            self.alternates = []

    def __getitem__(self, item):
        """Get the URL for a specific platform

        Args:
            item (str): The platform you want

        Returns:
            str: The URL of the specific playform or the default
        """
        for alt in self.alternates:
            if item in alt.platforms:
                return alt.url
        return self.url


class Media(object):
    def __init__(self, data, client):
        """Base media object

        Args:
            data (dict): Data about the media.
            client (HTTPClient): An HTTP client.
        """
        if 'pointer' in data:
            pointer = data['pointer']
            # NOTE(Sinap): Getting the details of a show returns two pointers,
            # one to get episode details and one for similar shows. Index 0
            # is always the episode pointer which is what we want.
            if isinstance(pointer, list):
                self.pointer = Pointer(**pointer[0])
            else:
                self.pointer = Pointer(**pointer)
        self.title = data['title'].encode('utf-8')
        self.client = client
        self._data = data

    def invoke(self):
        resp = self.client.get(self.pointer.path, self.pointer.params)
        return resp[self.pointer.target]

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__,
                                 self.title)


class Show(Media):
    def __init__(self, data, client):
        super(Show, self).__init__(data, client)
        self.thumbnail = Thumbnail(**data['thumbnail'])
        # NOTE(Sinap): Some shows don't have an ID or a content key
        self.id = int(data.get('id', self.pointer.params.split('=')[1]))
        button = data['legend']['button']
        if isinstance(button, list):
            pointer = button[0]['pointer']
        else:
            pointer = button['pointer']
        self.show_id = pointer['toggle']['data']['params'].split('=')[1]
        if 'content' in data:
            self.recent_item = data['content']['metadata']['recentContentItem']
        else:
            self.recent_item = None

    def get_details(self):
        """Get details about the show

        Returns:
            ShowDetails:
        """
        return self.invoke()

    def invoke(self):
        return ShowDetails(super(Show, self).invoke(), self.client)

    def __getitem__(self, item):
        return self.get_details().get_season(item)

    def __iter__(self):
        details = self.invoke()
        for season in details.seasons:
            result = details.get_season(season)
            if result:
                yield result


class ShowDetails(Media):
    def __init__(self, data, client):
        super(ShowDetails, self).__init__(data, client)
        hero = data['hero']['item']
        content = hero['content']
        self.title = hero['title']
        self.description = content['description']
        self.format = content['metadata']['format']
        self.release_year = content['metadata']['releaseYear']
        self.thumbnail = Thumbnail(**hero['thumbnail'])
        pointer = data['pointer']
        if isinstance(pointer, list):
            fltr = pointer[0]['longList']['palette']['filter']
        else:
            fltr = data['pointer']['longList']['palette']['filter']
        button = fltr[0]['choices']['button']
        # NOTE(Sinap): etree_to_dict squashes nodes with only one child.
        # Might want to change this, not sure yet.
        if isinstance(button, list):
            self.seasons = {int(b['value']): b['title'] for b in button}
        else:
            self.seasons = {int(button['value']): button['title']}
        self.season = self.seasons.keys()[0]

    @property
    def has_movie(self):
        return 'Movie' in self.seasons.values()

    @property
    def has_ova(self):
        return 'OVS' in self.seasons.values()

    def get_season(self, season=1):
        self.season = season
        self.pointer.params = '{}&season={}'.format(self.pointer.params,
                                                    self.season)
        return self.invoke()

    def invoke(self):
        data = super(ShowDetails, self).invoke()
        if data['items']:
            return Season(
                data['items'], self.client, self.seasons[self.season])
        else:
            return []

    def __getitem__(self, item):
        """Get a specific season using index notation

        Args:
            item (int):

        Returns:

        """
        for season in self.seasons:
            if item == season:
                return self.get_season(item)
        raise UnknownSeason('valid seasons are: {}'.format(
            ', '.join(self.seasons.values())))

    def __iter__(self):
        for season in self.seasons:
            yield season


class Season(Media):
    def __init__(self, data, client, season):
        data['title'] = season
        super(Season, self).__init__(data, client)
        self.season = season
        if isinstance(data['item'], list):
            self._episodes = EpisodeContainer(
                [Episode(x, self.client) for x in data['item']])
        else:
            self._episodes = EpisodeContainer(
                [Episode(data['item'], self.client)])

    def __iter__(self):
        for episode in self._episodes:
            yield episode


class Episode(Media):
    # noinspection PyTypeChecker
    def __init__(self, data, client):
        super(Episode, self).__init__(data, client)
        content = data['content']
        metadata = content['metadata']
        self._audio = None
        self.description = content.get('description', '')
        self.duration = int(metadata['duration'])
        self.format = metadata['format']
        self.episode_number = float(metadata['episodeNumber'])
        if metadata['languages']:
            self.languages = metadata['languages'].split(',')
        else:
            self.languages = None

    def get_dub(self):
        self._audio = AudioType.DUB
        return self.invoke()

    def get_sub(self):
        self._audio = AudioType.SUB
        return self.invoke()

    def get_details(self):
        """
        Returns:
            EpisodeDetails:
        """
        return self.invoke()

    def invoke(self):
        if self._audio:
            self.pointer.params = self.pointer.params.replace(
                'explicit:', '').format(autoPlay=1, audio=self._audio)
        return EpisodeDetails(super(Episode, self).invoke(), self.client)


class EpisodeDetails(Media):
    def __init__(self, data, client):
        super(EpisodeDetails, self).__init__(data['item']['video'], client)
        video = data['item']['video']
        metadata = video['content']['metadata']
        hls = data['item']['hls']
        related = data['item']['related']['alternate']
        self.video_url = hls['url']
        self.closed_caption_url = hls['closedCaptionUrl']
        self.video_id = int(video['id'])
        self.thumbnail = video['thumbnail']
        self.duration = int(metadata['duration'])
        self.episode = int(metadata['episode'].split(' ')[1])
        self.season = int(metadata['season'].split(' ')[1])
        self.show_name = metadata['showName']
        self.params = related['params']
        self.path = related['path']
        self.target = related['target']
        self.ratings = [(r['@region'], r['#text']) for r in
                        data['item']['ratings']['tv']]

    def get_stream(self, quality=None):
        """Get the m3u URL for a specific stream quality.

        If the quality doesn't exist the default m3u file that contains all
        streams is returned.

        Args:
            quality (int): an int between 0 and 9.
                Some shows might not have a quality of 9

        Returns:
            str: A url to an m3u file.
        """
        if quality is None:
            return self.video_url
        # replace the response handler with one that does nothing to the
        # response then put the original back.
        handler = self.client.handle_response
        try:
            self.client.handle_response = NullHandler
            resp = self.client.get(self.video_url)
            quality = 'Layer{}'.format(quality)
            for line in resp.split('\n'):
                if quality in line:
                    # pull out file from url and replace with file from
                    # m3u8 file.
                    url = self.video_url.split('/')[:-1].append(line)
                    return '/'.join(url)
        finally:
            self.client.handle_response = handler
        # specific quality wasn't found. just return original video url.
        return self.video_url

    def get_related(self):
        return self.invoke()

    def invoke(self):
        data = super(EpisodeDetails, self).invoke()
        data['title'] = data['hero']['item']['title']
        return ShowDetails(data, self.client)

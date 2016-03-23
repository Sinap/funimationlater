# -*- coding: utf-8 -*-
from __future__ import absolute_import

from funimationlater.error import InvalidSeason, UnknownEpisode


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


class Media(object):
    def __init__(self, data, client):
        """Base media object

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
        self.title = data['title'].encode('utf-8')
        self.client = client
        self._data = data

    def _parse_results(self, data):
        """Can't think of a better name
        Args:
            data (dict):
        """
        raise NotImplementedError

    def _invoke(self):
        resp = self.client.get(self.path, self.params)
        return self._parse_results(resp[self.target])

    def __repr__(self):
        return '<{}: {}>'.format(self.__class__.__name__,
                                 self.title.encode('utf-8'))


class Show(Media):
    def __init__(self, data, client):
        super(Show, self).__init__(data, client)

    def get_details(self):
        """Get details about the show

        Returns:
            ShowDetails:
        """
        return self._invoke()

    def _parse_results(self, data):
        return ShowDetails(data, self.client)

    def __getitem__(self, item):
        return self.get_details().get_season(item)

    def __iter__(self):
        details = self.get_details()
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
        self.thumbnail = hero['thumbnail']['#text']
        for thumb in hero['thumbnail']['alternate']:
            if 'ios' in thumb['@platforms']:
                self.thumbnail = thumb['#text']
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
        self.params = '{}&season={}'.format(self.params, self.season)
        return self._invoke()

    def _parse_results(self, data):
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
        raise InvalidSeason('valid seasons are: {}'.format(
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

    def _parse_results(self, data):
        return data

    def __iter__(self):
        for episode in self._episodes:
            yield episode


class Episode(Media):
    # noinspection PyTypeChecker
    def __init__(self, data, client):
        super(Episode, self).__init__(data, client)
        content = data['content']
        metadata = content['metadata']
        self.description = content.get('description', '')
        self.duration = int(metadata['duration'])
        self.format = metadata['format']
        self.episode_number = float(metadata['episodeNumber'])
        if metadata['languages']:
            self.languages = metadata['languages'].split(',')
        else:
            self.languages = None

    def get_details(self):
        """
        Returns:
            EpisodeDetails:
        """
        return self._invoke()

    def _parse_results(self, data):
        return EpisodeDetails(data, self.client)


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

    def get_related(self):
        return self._invoke()

    def _parse_results(self, data):
        data['title'] = data['hero']['item']['title']
        return ShowDetails(data, self.client)

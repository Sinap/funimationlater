# -*- coding: utf-8 -*-


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

    def get_video(self):
        """
        Returns:
            Video:
        """
        return self._invoke()

    def parse_results(self, data):
        return Video(data, self.client)


class Video(Media):
    def __init__(self, data, client):
        super(Video, self).__init__(data['item']['video'], client)
        video = data['item']['video']
        metadata = video['content']['metadata']
        hls = data['item']['hls']
        related = data['item']['related']['alternate']
        self.video_url = hls['url']
        self.closed_caption_url = hls['closedCaptionUrl']
        self.id = int(video['id'])
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

    def parse_results(self, data):
        data['title'] = data['hero']['item']['title']
        return ShowDetails(data, self.client)

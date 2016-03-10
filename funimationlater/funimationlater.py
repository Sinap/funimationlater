# -*- coding: utf-8 -*-
from http import HTTPClient

__all__ = ['FunimationLater', 'AuthenticationFailed', 'Show', 'Video']


class AuthenticationFailed(Exception):
    pass


class Show(object):
    def __init__(self, data):
        super(Show, self).__init__()
        self.title = data['title']
        self.thumbnail = data['thumbnail']['#text']
        self.pk = data['pointer']['params'].split('=')[1]


class Video(object):
    def __init__(self, data):
        super(Video, self).__init__()
        self.title = data['item']['title']
        self.thumbnail = data['item']['thumbnail']['#text']
        self.desctription = data['item']['content']['description']
        self.release_year = data['item']['content']['metadata']['releaseYear']
        self.format = data['item']['content']['metadata']['format']

    def __str__(self):
        return ''


class FunimationLater(object):
    def __init__(self):
        """Funimation API"""
        self.http = HTTPClient('https://api-funimation.dadcdigital.com/xml')
        self.logged_in = False

    def login(self, username, password):
        """
        Args:
            username (str):
            password (str):
        """
        resp = self.http.post('/auth/login/?',
                              {'username': username, 'password': password})
        if 'error' in resp['authentication']:
            raise AuthenticationFailed('username or password is incorrect')
        self.http.add_headers(resp['authentication']['parameters']['header'])
        self.logged_in = True

    def get_my_queue(self):
        """
        Returns:
            list[Show]:
        """
        resp = self.http.get('/myqueue/get-items/?')
        if 'watchlist' in resp:
            return [Show(x['item']) for x in resp['watchlist']['items']['item']]
        return resp

    def video_details(self, pk):
        """
        Args:
            pk (str):

        Returns:
            Video:
        """
        resp = self.http.get('/detail/?pk={0}'.format(pk))
        return Video(resp['list2d']['hero'])

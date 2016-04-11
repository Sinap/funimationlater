# -*- coding: utf-8 -*-
import urllib2

__all__ = ['AuthenticationFailed', 'LoginRequired', 'UnknowResponse',
           'UnknownSeason', 'UnknownEpisode', 'UnknownShow', 'HTTPError']


class AuthenticationFailed(Exception):
    pass


class LoginRequired(Exception):
    pass


class UnknowResponse(Exception):
    pass


class UnknownSeason(Exception):
    pass


class UnknownEpisode(Exception):
    pass


class UnknownShow(Exception):
    pass


class HTTPError(urllib2.HTTPError):
    """Override the str method to provide the URL with the error"""
    def __str__(self):
        return 'HTTP Error {}: URL: {} MSG: {}'.format(
            self.code, self.filename, self.msg)

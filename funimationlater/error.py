# -*- coding: utf-8 -*-
try:
    from urllib.error import HTTPError
except ImportError:
    from urllib2 import HTTPError

__all__ = ['AuthenticationFailed', 'LoginRequired', 'UnknowResponse',
           'UnknownSeason', 'UnknownEpisode', 'UnknownShow',
           'DetailedHTTPError']


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


# noinspection PyClassHasNoInit
class DetailedHTTPError(HTTPError):
    """Override the str method to provide the URL with the error"""
    def __str__(self):
        return 'HTTP Error {}: URL: {} MSG: {}'.format(
            self.code, self.filename, self.msg)

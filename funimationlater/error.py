# -*- coding: utf-8 -*-
import urllib2


class AuthenticationFailed(Exception):
    pass


class LoginRequired(Exception):
    pass


class UnknowResponse(Exception):
    pass


class InvalidSeason(Exception):
    pass


class UnknownEpisode(Exception):
    pass


class HTTPError(urllib2.HTTPError):
    def __str__(self):
        return 'HTTP Error {}: {} => {}'.format(
            self.code, self.filename, self.msg)

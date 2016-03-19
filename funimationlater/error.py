# -*- coding: utf-8 -*-
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

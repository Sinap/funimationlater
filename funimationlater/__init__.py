# -*- coding: utf-8 -*-
from __future__ import absolute_import
# noinspection PyUnresolvedReferences
import logging
from funimationlater.funimationlater import FunimationLater
# noinspection PyUnresolvedReferences
from funimationlater.error import (AuthenticationFailed, LoginRequired,
                                   InvalidSeason, UnknownEpisode,
                                   UnknowResponse)
# noinspection PyUnresolvedReferences
from funimationlater.models import (Show, ShowDetails, Season, Episode,
                                    EpisodeDetails, EpisodeContainer)

logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = 'Aaron Frase'
__email__ = 'afrase91@gmail.com'
__version__ = '0.0.1'

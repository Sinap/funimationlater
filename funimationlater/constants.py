class ShowTypes(object):
    SIMULCAST = 'simulcasts'
    BROADCAST_DUBS = 'broadcast-dubs'
    SEARCH = 'search'
    SHOWS = 'shows'


class SortBy(object):
    TITLE = 'slug_exact'
    DATE = 'start_timestamp'


class SortOrder(object):
    ASC = 'asc'
    DESC = 'desc'


class AudioType(object):
    SUB = 'ja'
    DUB = 'en'

# -*- coding: utf-8 -*-
from __future__ import print_function
import time
import collections
import xml.etree.cElementTree as Et
from functools import wraps
from contextlib import contextmanager

__all__ = ['CaseInsensitiveDict', 'etree_to_dict', 'timethis', 'timeblock']


class CaseInsensitiveDict(collections.MutableMapping):
    def __init__(self, data=None, **kwargs):
        self._store = {}
        if data is None:
            data = {}
        self.update(data, **kwargs)

    def __setitem__(self, key, value):
        self._store[key.lower()] = (key, value)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __len__(self):
        return len(self._store)

    def __iter__(self):
        return (k for k, _ in self._store.values())

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __eq__(self, other):
        if isinstance(other, collections.Mapping):
            other = CaseInsensitiveDict(other)
        else:
            raise NotImplementedError
        return dict(self.lower_items()) == dict(other.lower_items())

    def __repr__(self):
        return '%s(%r)' % (self.__class__.__name__, dict(self.items()))

    def lower_items(self):
        return ((k, v) for k, v in self._store.items())

    def copy(self):
        return CaseInsensitiveDict(self._store.values())


def etree_to_dict(xml):
    """Converts an XML string to a `dict`.

    Args:
        xml (str, Element): The string to convert.
         keys begining with '@' are attributes and '#text' key is the elements
         text.

    Returns:
        dict: The `dict` representation of the XML.
    """
    t = Et.fromstring(xml) if isinstance(xml, str) else xml
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = collections.defaultdict(list)
        for dc in [etree_to_dict(child) for child in children]:
            for key, val in dc.iteritems():
                dd[key].append(val)
        d = {t.tag: {k: v[0] if len(v) == 1 else v for k, v in dd.iteritems()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.iteritems())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def timethis(func):
    """A decorator used to time functions or methods

    Args:
        func: The function or method to time

    Returns: The result of the function or method call
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        r = func(*args, **kwargs)
        end = time.time()
        print('{}.{}: {}'.format(func.__module__, func.__name__, end - start))
        return r

    return wrapper


@contextmanager
def timeblock(label):
    """A generator to time a block of statements

    Args:
        label (str): The label used in output.
    """
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print('{}: {}'.format(label, end - start))

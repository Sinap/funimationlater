# -*- coding: utf-8 -*-
import time
import xml.etree.cElementTree as Et
from collections import defaultdict
from functools import wraps
from contextlib import contextmanager


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
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.iteritems():
                dd[k].append(v)
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
    """Time a block of statements

    Args:
        label (str): The label used in output.
    """
    start = time.time()
    try:
        yield
    finally:
        end = time.time()
        print('{} : {}'.format(label, end - start))

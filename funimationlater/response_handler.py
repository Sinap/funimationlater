# -*- coding: utf-8 -*-
import xml.etree.cElementTree as Et
from utils import etree_to_dict, CaseInsensitiveDict

__all__ = ['ResponseHandler', 'XMLResponse', 'NullHandler']


class ResponseHandler(object):
    def __init__(self, resp, req):
        """
        Args:
            resp (str):
            req (urllib2.Request):
        """
        super(ResponseHandler, self).__init__()
        self._resp = resp
        self._req = req

    def handle(self):
        raise NotImplementedError


class NullHandler(ResponseHandler):
    def handle(self):
        return self._resp


class XMLResponse(ResponseHandler):
    def handle(self):
        if self._resp:
            data = etree_to_dict(Et.fromstring(self._resp))
            return CaseInsensitiveDict(data)

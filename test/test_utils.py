# -*- coding: utf-8 -*-
import unittest

from funimationlater.utils import etree_to_dict, CaseInsensitiveDict


class TestUtils(unittest.TestCase):
    def test_etree_to_dict(self):
        xml = """
        <note>
            <to foo="bar">Foo</to>
            <from>Bar</from>
            <heading>Foo Bar</heading>
            <body>Fooooo baarrrrr</body>
        </note>
        """
        expected = {'note': {'body': 'Fooooo baarrrrr',
                             'from': 'Bar',
                             'heading': 'Foo Bar',
                             'to': {'#text': 'Foo', '@foo': 'bar'}}}
        # convert it back to a dict from a CaseInsensitiveDict
        actual = dict(etree_to_dict(xml))
        self.assertDictEqual(actual, expected)

    def test_case_insensitive_dict(self):
        ci_dict = CaseInsensitiveDict({'MixEdCase': 42})
        self.assertIn('mixEdCase', ci_dict)

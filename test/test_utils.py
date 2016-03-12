# -*- coding: utf-8 -*-
import unittest

from utils import etree_to_dict


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
        actual = etree_to_dict(xml)
        self.assertDictEqual(actual, expected)

# -*- coding: utf-8 -*-
import unittest

from funimationlater.utils import etree_to_dict, CaseInsensitiveDict


class TestUtils(unittest.TestCase):
    def test_etree_to_dict(self):
        xml = """<note><to foo="bar">Foo</to><from>Bar</from>
        <heading>Foo Bar</heading><body>Fooooo baarrrrr</body></note>"""
        expected = {'note': {'body': 'Fooooo baarrrrr',
                             'from': 'Bar',
                             'heading': 'Foo Bar',
                             'to': {'#text': 'Foo', '@foo': 'bar'}}}
        actual = etree_to_dict(xml)
        self.assertDictEqual(actual, expected)

    def test_case_insensitive_dict_setitem(self):
        ci_dict = CaseInsensitiveDict()
        ci_dict['MixEdCase'] = 42
        self.assertIn('mixedcase', ci_dict)
        self.assertEqual(ci_dict['mixedcase'], 42)

    def test_case_insensitive_dict_init_with_data(self):
        ci_dict = CaseInsensitiveDict({'MiXeDcAsE': 42})
        self.assertIn('mixedcase', ci_dict)
        self.assertEqual(ci_dict['mixedcase'], 42)

    def test_case_insensitive_dict_equal_to_dict(self):
        expected = {'MiXeDcAsE': 42}
        ci_dict = CaseInsensitiveDict(expected)
        self.assertEqual(ci_dict, expected)

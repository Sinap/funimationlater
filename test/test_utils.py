# -*- coding: utf-8 -*-
import unittest
import mock
import xml.etree.cElementTree as Et
from io import StringIO
from funimationlater.utils import (etree_to_dict, CaseInsensitiveDict,
                                   timethis, timeblock)


class TestUtils(unittest.TestCase):
    def test_etree_to_dict(self):
        xml = """<note><to foo="bar">Foo</to><from>Bar</from>
        <heading>Foo Bar</heading><body>Fooooo baarrrrr</body></note>"""
        expected = {'note': {'body': 'Fooooo baarrrrr',
                             'from': 'Bar',
                             'heading': 'Foo Bar',
                             'to': {'#text': 'Foo', '@foo': 'bar'}}}
        actual = etree_to_dict(Et.fromstring(xml))
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
        with self.assertRaises(NotImplementedError):
            ci_dict == 1

    def test_case_insensitive_dict_del_key(self):
        ci_dict = CaseInsensitiveDict({'MiXeDcAsE': 42, 'keyToDelete': 1})
        self.assertEqual(len(ci_dict), 2)
        del ci_dict['keytodelete']
        self.assertEqual(len(ci_dict), 1)
        with self.assertRaises(KeyError):
            # noinspection PyStatementEffect
            ci_dict['keytodelete']

    def test_case_insensitive_dict_copy(self):
        expected = {'MiXeDcAsE': 42}
        ci_dict = CaseInsensitiveDict(expected)
        copy = ci_dict.copy()
        repr(ci_dict)
        self.assertEqual(ci_dict, copy)
        self.assertEqual(expected, copy)

    def test_timethis(self):
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            seconds = 0.7

            @timethis
            def func():
                import time
                time.sleep(seconds)
            func()

            self.assertIn('{}: {}'.format(func.__name__, seconds),
                          fake_out.getvalue())

    def test_timeblock(self):
        with mock.patch('sys.stdout', new=StringIO()) as fake_out:
            seconds = 0.5
            label = 'test'

            with timeblock(label):
                import time
                time.sleep(seconds)

            self.assertIn('{}: {}'.format(label, seconds),
                          fake_out.getvalue())

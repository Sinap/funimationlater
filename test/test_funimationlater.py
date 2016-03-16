# -*- coding: utf-8 -*-
"""
Tests for `funimationlater` module.
"""
import os
import unittest
import mock
import funimationlater


class TestFunimationLater(unittest.TestCase):
    def test_login_successful(self):
        with mock.patch('funimationlater.funimationlater.HTTPClient'):
            payload = {'username': 'foo', 'password': 'bar'}
            api = funimationlater.FunimationLater()
            api.login(**payload)
            self.assertTrue(api.client.post.called)
            self.assertTrue(api.logged_in)
            call_args = api.client.post.call_args[0]
            self.assertEqual(call_args[0], '/auth/login/?')
            self.assertDictEqual(call_args[1], payload)

    def test_login_failed(self):
        # mock failed login to return a value
        with mock.patch('funimationlater.funimationlater.HTTPClient.post',
                        return_value={'authentication': {'error': 'error'}}):
            payload = {'username': 'foo', 'password': 'bar'}
            api = funimationlater.FunimationLater()
            self.assertRaises(funimationlater.AuthenticationFailed,
                              api.login, **payload)
            self.assertTrue(api.client.post.called)
            call_args = api.client.post.call_args[0]
            self.assertEqual(call_args[0], '/auth/login/?')
            self.assertDictEqual(call_args[1], payload)

    def test_get_my_queue(self):
        with mock.patch('funimationlater.http.urllib2.urlopen',
                        return_value=open(
                            os.path.normpath('./test/resources/myqueue.xml'))):
            api = funimationlater.FunimationLater()
            api.logged_in = True
            queue = api.get_my_queue()
            self.assertIsNotNone(queue)
            self.assertIsInstance(queue, list)
            self.assertIsInstance(queue[0], funimationlater.Show)

    def test_get_all_shows(self):
        with mock.patch('funimationlater.http.urllib2.urlopen',
                        return_value=open(
                            os.path.normpath(
                                './test/resources/all_shows.xml'))):
            api = funimationlater.FunimationLater()
            api.logged_in = True
            shows = api.get_all_shows()
            self.assertIsNotNone(shows)
            self.assertIsInstance(shows, list)
            self.assertIsInstance(shows[0], funimationlater.Show)

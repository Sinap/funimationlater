# -*- coding: utf-8 -*-
"""
Tests for `funimationlater` module.
"""
import unittest
import mock
import funimationlater


class TestFunimationLater(unittest.TestCase):

    def test_login_successful(self):
        with mock.patch('funimationlater.funimationlater.HTTPClient'):
            payload = {'username': 'foo', 'password': 'bar'}
            api = funimationlater.FunimationLater()
            api.login(**payload)
            self.assertTrue(api.http.post.called)
            self.assertTrue(api.logged_in)
            call_args = api.http.post.call_args[0]
            self.assertEqual(call_args[0], '/auth/login/?')
            self.assertDictEqual(call_args[1], payload)

    def test_login_failed(self):
        # mock failed login return value
        with mock.patch('funimationlater.funimationlater.HTTPClient.post',
                        return_value={'authentication': {'error': 'error'}}):
            payload = {'username': 'foo', 'password': 'bar'}
            api = funimationlater.FunimationLater()
            self.assertRaises(funimationlater.AuthenticationFailed,
                              api.login, **payload)
            self.assertTrue(api.http.post.called)
            call_args = api.http.post.call_args[0]
            self.assertEqual(call_args[0], '/auth/login/?')
            self.assertDictEqual(call_args[1], payload)

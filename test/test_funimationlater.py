# -*- coding: utf-8 -*-
"""
Tests for `funimationlater` module.
"""
import unittest
import logging
import mock
import funimationlater

logging.basicConfig(level=logging.INFO)


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

    # def test_something(self):
    #     api = funimationlater.FunimationLater()
    #     api.client.add_headers({
    #         'userName': '',
    #         'userType': '',
    #         'Authorization': '123',
    #         'userRole': '',
    #     })
    #     api.logged_in = True
    #     episode = api.get_shows()[14].get_details().get_episodes()[0]
    #     episode._invoke()
    #     api.get_simulcasts(3)[1].get_details().get_episodes()
    #     api.get_all_shows(3)[1].get_details().get_episodes()

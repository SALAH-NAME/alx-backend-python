#!/usr/bin/env python3
""" test_utils.py """

from parameterized import parameterized
import unittest
from unittest.mock import patch
from utils import (access_nested_map, get_json, memoize)
import requests


class TestAccessNestedMap(unittest.TestCase):
    """TestAccessNestedMap Class
    """

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {'b': 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        """access_nested_map function
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b')
    ])
    def test_access_nested_map_exception(self, nested_map, path, expected):
        """access_nested_map funciton
        """
        with self.assertRaises(KeyError) as exp:
            access_nested_map(nested_map, path)
        self.assertEqual(f"KeyError('{expected}')", repr(exp.exception))


class TestGetJson(unittest.TestCase):
    """TestGetJson Class
    """

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    def test_get_json(self, test_url, test_payload):
        """test_get_json function
        """
        config = {'return_value.json.return_value': test_payload}
        patcher = patch('requests.get', **config)
        mock = patcher.start()
        self.assertEqual(get_json(test_url), test_payload)
        mock.assert_called_once()
        patcher.stop()


class TestMemoize(unittest.TestCase):
    """TestMemoize Class
    """

    def test_memoize(self):
        """test_memoize function
        """

        class TestClass:
            """ Test Class for wrapping with memoize """

            def a_method(self):
                """a_method function"""
                return 42

            @memoize
            def a_property(self):
                """a_property function"""
                return self.a_method()

        with patch.object(TestClass, 'a_method') as mock:
            test_class = TestClass()
            test_class.a_property()
            test_class.a_property()
            mock.assert_called_once()

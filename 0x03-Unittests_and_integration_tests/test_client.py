#!/usr/bin/env python3
""" test_client.py """
import unittest
from fixtures import TEST_PAYLOAD
from client import GithubOrgClient
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class


class TestGithubOrgClient(unittest.TestCase):
    """TestGithubOrgClient Class
    """

    @parameterized.expand([
        ('google'),
        ('abc')
    ])
    @patch('client.get_json')
    def test_org(self, org_name, mock_get_json):
        """test_org function
        """
        client_instance = GithubOrgClient(org_name)
        client_instance.org()
        mock_get_json.assert_called_once_with(
            f'https://api.github.com/orgs/{org_name}'
        )

    def test_public_repos_url(self):
        """test_public_repos_url function
        """
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {"repos_url": "World"}
            client_instance = GithubOrgClient('test')
            result = client_instance._public_repos_url
            self.assertEqual(result, "World")

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """test_public_repos function
        """
        json_payload = [{"name": "Google"}, {"name": "Twitter"}]
        mock_get_json.return_value = json_payload

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_url:
            mock_public_url.return_value = "world"
            client_instance = GithubOrgClient('test')
            result = client_instance.public_repos()

            expected_repos = [repo["name"] for repo in json_payload]
            self.assertEqual(result, expected_repos)
            mock_public_url.assert_called_once()
            mock_get_json.assert_called_once()

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False)
    ])
    def test_has_license(self, repo, license_key, expected):
        """test_has_license function
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """TestIntegrationGithubOrgClient Class
    """

    @classmethod
    def setUpClass(cls):
        """setUpClass function
        """
        config = {
            'return_value.json.side_effect': [
                cls.org_payload, cls.repos_payload,
                cls.org_payload, cls.repos_payload
            ]
        }
        cls.get_patcher = patch('requests.get', **config)
        cls.mock_get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """tearDownClass function
        """
        cls.get_patcher.stop()

    def test_public_repos(self):
        """test_public_repos function
        """
        client_instance = GithubOrgClient("google")
        self.assertEqual(client_instance.org, self.org_payload)
        self.assertEqual(client_instance.repos_payload, self.repos_payload)
        self.assertEqual(client_instance.public_repos(), self.expected_repos)
        self.assertEqual(client_instance.public_repos("XLICENSE"), [])
        self.mock_get.assert_called()

    def test_public_repos_with_license(self):
        """test_public_repos_with_license function
        """
        client_instance = GithubOrgClient("google")
        self.assertEqual(client_instance.public_repos(), self.expected_repos)
        self.assertEqual(client_instance.public_repos("XLICENSE"), [])
        self.assertEqual(client_instance.public_repos("apache-2.0"),
                         self.apache2_repos)
        self.mock_get.assert_called()

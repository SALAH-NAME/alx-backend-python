#!/usr/bin/env python3
""" test_client.py """
import unittest
from unittest.mock import patch, MagicMock, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from client import GithubOrgClient
from fixtures import org_payload, repos_payload, expected_repos, apache2_repos


class TestGithubOrgClient(unittest.TestCase):
    """TestsGithubOrgClient Class
    """

    @parameterized.expand([
        ('google'),
        ('abc')
    ])
    @patch('client.get_json')
    def test_org(self, data, mock):
        """test_org function
        """
        endpoint = 'https://api.github.com/orgs/{}'.format(data)
        spec = GithubOrgClient(data)
        spec.org()
        mock.assert_called_once_with(endpoint)

    def test_public_repos_url(self):
        """test_public_repos_url function
        """
        with patch('client.GithubOrgClient.org',
                   new_callable=PropertyMock) as mock_org:
            mock_org.return_value = {
                "repos_url": "https://api.github.com/orgs/google/repos"
            }
            client = GithubOrgClient("google")
            self.assertEqual(client._public_repos_url,
                             "https://api.github.com/orgs/google/repos")

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json):
        """test_public_repos function
        """
        test_payload = [{'name': 'Google'}, {'name': 'T_E'}]
        mock_get_json.return_value = test_payload

        with patch('client.GithubOrgClient._public_repos_url',
                   new_callable=PropertyMock) as mock_public_repos_url:
            mock_public_repos_url.return_value = 'worold'
            client = GithubOrgClient('test')
            result = client.public_repos()
            names = [i["name"] for i in test_payload]
            self.assertEqual(result, names)
            mock_public_repos_url.assert_called_once()
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


@parameterized_class([
    {"org_payload": org_payload, "repos_payload": repos_payload,
     "expected_repos": expected_repos, "apache2_repos": apache2_repos}
])
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """TestIntegrationGithubOrgClient Class
    """

    @classmethod
    def setUpClass(cls):
        """setUpClass function
        """
        cls.get_patcher = patch('requests.get', side_effect=cls.get_payload)
        cls.mock_get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """tearDownClass function
        """
        cls.get_patcher.stop()

    @classmethod
    def get_payload(cls, url):
        """get_payload function
        """
        if url == "https://api.github.com/orgs/google":
            return Mock(json=lambda: cls.org_payload)
        elif url == "https://api.github.com/orgs/google/repos":
            return Mock(json=lambda: cls.repos_payload)
        return Mock(json=lambda: {})

    def test_public_repos(self):
        """test_public_repos function
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self):
        """test_public_repos_with_license function
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos("apache-2.0"), self.apache2_repos)

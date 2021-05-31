# Based on https://github.com/ansible-collections/community.grafana/blob/main/tests/unit/modules/grafana/grafana_user/test_grafana_user.py
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest import TestCase
from unittest.mock import call, patch, MagicMock
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.knightsg.dkron.plugins.modules import dkron_cluster_info
from ansible_collections.knightsg.dkron.plugins.module_utils.classes import DkronClusterInterface
from ansible_collections.knightsg.dkron.tests.unit.module_utils.dkron_cluster_responses import (
    cluster_query_status_response_success,
    cluster_query_leader_response_success,
    cluster_query_members_response_success,
    cluster_query_job_list_response_success,
    cluster_query_active_job_list_response_success,
    cluster_query_response_http_not_found,
    cluster_query_empty_dict_response,
    cluster_query_empty_list_response
)
import json


def exit_json(*args, **kwargs):
    """function to patch over exit_json; package return data into an exception"""
    if 'changed' not in kwargs:
        kwargs['changed'] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """function to patch over fail_json; package return data into an exception"""
    kwargs['failed'] = True
    raise AnsibleFailJson(kwargs)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""
    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""
    pass


def set_module_args(args):
    """prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class DkronClusterInfoTest(TestCase):

    maxDiff = None

    def setUp(self):
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json
        )
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    # Test cluster status query successful
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_status_success(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'type': 'status'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_status_response_success()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.cluster_status()
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertEqual(result, {
            'coordinate_resets': '0',
            'encrypted': 'false',
            'event_queue': '0',
            'event_time': '1',
            'failed': '0',
            'health_score': '0',
            'intent_queue': '0',
            'left': '0',
            'member_time': '2',
            'members': '2',
            'query_queue': '0',
            'query_time': '1'
        })

    # Test cluster status query 404 response
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_status_404_response(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'type': 'status'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_response_http_not_found()

        dkron_iface = DkronClusterInterface(module)

        with self.assertRaises(AnsibleFailJson):
            result = dkron_iface.cluster_status()
            mock_fetch_url.assert_called_once_with(
                module,
                'http://172.16.0.1:8080/v1/',
                headers=dkron_iface.headers,
                method='GET'
            )

    # Test cluster status query empty response
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_status_empty_response(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_empty_dict_response()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.cluster_status()
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertEqual(result, {})

    # Test cluster leader query successful
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_leader_success(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'type': 'leader'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_leader_response_success()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.leader_node()
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/leader',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertEqual(result, '172.16.0.1')

    # Test cluster leader query 404 response
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_leader_404_response(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'type': 'leader'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_response_http_not_found()

        dkron_iface = DkronClusterInterface(module)

        with self.assertRaises(AnsibleFailJson):
            result = dkron_iface.leader_node()
            mock_fetch_url.assert_called_once_with(
                module,
                'http://172.16.0.1:8080/v1/leader',
                headers=dkron_iface.headers,
                method='GET'
            )

    # Test cluster leader query empty response
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_leader_empty_response(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'type': 'leader'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_empty_dict_response()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.leader_node()
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/leader',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertEqual(result, '')

    # Test cluster members query successful
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_members_success(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'type': 'members'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_members_response_success()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.member_nodes()
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/members',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertEqual(result, [
            '172.16.0.1',
            '172.16.0.2'
        ])

    # Test cluster members query 404 response
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_members_404_response(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'type': 'members'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_response_http_not_found()

        dkron_iface = DkronClusterInterface(module)

        with self.assertRaises(AnsibleFailJson):
            result = dkron_iface.member_nodes()
            mock_fetch_url.assert_called_once_with(
                module,
                'http://172.16.0.1:8080/v1/members',
                headers=dkron_iface.headers,
                method='GET'
            )

    # Test cluster members query empty response
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_members_empty_response(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'type': 'members'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_empty_list_response()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.member_nodes()
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/members',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertEqual(result, [])

    # Test cluster job list query successful
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_job_list_success(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'type': 'jobs'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_job_list_response_success()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.job_list()
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/jobs',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertEqual(result, [
            'job',
            'job2',
            'job3'
        ])

    # Test cluster active job list query successful
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_active_job_list_success(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'type': 'jobs',
            'active_only': 'true'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_active_job_list_response_success()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.job_list()
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/busy',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertEqual(result, [
            'job2',
            'job3'
        ])

    # Test cluster job list query 404 response
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_job_list_404_response(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'type': 'members'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_response_http_not_found()

        dkron_iface = DkronClusterInterface(module)

        with self.assertRaises(AnsibleFailJson):
            result = dkron_iface.job_list()
            mock_fetch_url.assert_called_once_with(
                module,
                'http://172.16.0.1:8080/v1/jobs',
                headers=dkron_iface.headers,
                method='GET'
            )

    # Test cluster job list query empty response
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_cluster_job_list_empty_response(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'type': 'jobs'
        })
        module = dkron_cluster_info.init_module()
        mock_fetch_url.return_value = cluster_query_empty_list_response()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.job_list()
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/jobs',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertEqual(result, [])

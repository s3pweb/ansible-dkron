# Based on https://github.com/ansible-collections/community.grafana/blob/main/tests/unit/modules/grafana/grafana_user/test_grafana_user.py
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest import TestCase
from unittest.mock import call, patch, MagicMock
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.knightsg.dkron.plugins.modules import dkron_job_info
from ansible_collections.knightsg.dkron.plugins.module_utils.classes import DkronClusterInterface
from ansible_collections.knightsg.dkron.tests.unit.module_utils.dkron_cluster_responses import (
    cluster_query_job_config_response_success,
    cluster_query_full_job_history_response_success,
    cluster_query_limited_job_history_response_success,
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


class DkronJobInfoTest(TestCase):

    maxDiff = None

    def setUp(self):
        self.mock_module_helper = patch.multiple(
            basic.AnsibleModule,
            exit_json=exit_json,
            fail_json=fail_json)
        self.mock_module_helper.start()
        self.addCleanup(self.mock_module_helper.stop)

    # Test retrieving job config successfully
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_job_config_success(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1'
        })
        module = dkron_job_info.init_module()
        mock_fetch_url.return_value = cluster_query_job_config_response_success()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.get_job_config(job_name='job')
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/jobs/job',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertEqual(result, {
            'id': 'job',
            'name': 'job',
            'displayname': '',
            'timezone': '',
            'schedule': '@every 1m',
            'owner': 'guy',
            'owner_email': 'guy@bluebatgames.com',
            'success_count': 145154,
            'error_count': 0,
            'last_success': '2021-05-27T01:28:24.035128372Z',
            'last_error': 'null',
            'disabled': 'false',
            'tags': {
                'server': 'true:1'
            },
            'metadata': 'null',
            'retries': 0,
            'dependent_jobs': 'null',
            'parent_job': '',
            'processors': {},
            'concurrency': 'allow',
            'executor': 'shell',
            'executor_config': {
                'command': '/bin/true'
            },
            'status': 'success',
            'next': '2021-05-27T01:29:24Z'
        })

    # Test retrieving job history successfully
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_job_history_success(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1'
        })
        module = dkron_job_info.init_module()
        mock_fetch_url.return_value = cluster_query_full_job_history_response_success()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.get_job_history(job_name='job')
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/jobs/job/executions',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertCountEqual(result, [
            {
                'id': '1622079204013581868-ip-172-16-2-146',
                'job_name': 'job',
                'started_at': '2021-05-27T01:33:24.013581868Z',
                'finished_at': '2021-05-27T01:33:24.018975352Z',
                'success': 'true',
                'node_name': 'ip-172-16-2-146',
                'group': 1622079204001268640,
                'attempt': 2
            },
            {
                'id': '1622079204013581868-ip-172-16-2-147',
                'job_name': 'job',
                'started_at': '2021-05-27T01:33:24.013581869Z',
                'finished_at': '2021-05-27T01:33:24.018975353Z',
                'success': 'false',
                'node_name': 'ip-172-16-2-147',
                'group': 1622079204001268640,
                'attempt': 1
            }
        ])

    # Test retrieving limited job history successfully
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_limit_job_history_success(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'limit_history': 1
        })
        module = dkron_job_info.init_module()
        mock_fetch_url.return_value = cluster_query_limited_job_history_response_success()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.get_job_history(job_name='job')
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/jobs/job/executions',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertCountEqual(result, [
            {
                'id': '1622079204013581868-ip-172-16-2-146',
                'job_name': 'job',
                'started_at': '2021-05-27T01:33:24.013581868Z',
                'finished_at': '2021-05-27T01:33:24.018975352Z',
                'success': 'true',
                'node_name': 'ip-172-16-2-146',
                'group': 1622079204001268640,
                'attempt': 2
            }
        ])

    # Test job config query 404 response
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_job_config_404_response(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1'
        })
        module = dkron_job_info.init_module()
        mock_fetch_url.return_value = cluster_query_response_http_not_found()

        dkron_iface = DkronClusterInterface(module)

        with self.assertRaises(AnsibleFailJson):
            result = dkron_iface.get_job_config(job_name='job')

            mock_fetch_url.assert_called_once_with(
                module,
                'http://172.16.0.1:8080/v1/jobs/job',
                headers=dkron_iface.headers,
                method='GET'
            )

    # Test job history query 404 response
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_job_history_404_response(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1'
        })
        module = dkron_job_info.init_module()
        mock_fetch_url.return_value = cluster_query_response_http_not_found()

        dkron_iface = DkronClusterInterface(module)

        with self.assertRaises(AnsibleFailJson):
            result = dkron_iface.get_job_history(job_name='job')
            mock_fetch_url.assert_called_once_with(
                module,
                'http://172.16.0.1:8080/v1/jobs/job/executions',
                headers=dkron_iface.headers,
                method='GET'
            )

    # Test job config query empty response
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_info_job_config_empty_response(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1'
        })
        module = dkron_job_info.init_module()
        mock_fetch_url.return_value = cluster_query_empty_dict_response()

        dkron_iface = DkronClusterInterface(module)
        result = dkron_iface.get_job_config(job_name='job')
        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/jobs/job',
            headers=dkron_iface.headers,
            method='GET'
        )
        self.assertEqual(result, {})

# Based on https://github.com/ansible-collections/community.grafana/blob/main/tests/unit/modules/grafana/grafana_user/test_grafana_user.py
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest import TestCase
from unittest.mock import call, patch, MagicMock
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.knightsg.dkron.plugins.modules import dkron_job
from ansible_collections.knightsg.dkron.plugins.module_utils.classes import DkronClusterInterface
from ansible_collections.knightsg.dkron.tests.unit.module_utils.dkron_cluster_responses import (
    cluster_query_create_job_with_overwrite_response_success,
    cluster_query_response_http_not_found
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

    # Test create job with overwrite successfully
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_create_job_with_overwrite_success(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'name': 'job1',
            'schedule': '0 */15 * * * *',
            'shell_executor': {
                'command': '/bin/echo "hello world"',
                'cwd': '/tmp'
            }
        })
        module = dkron_job.init_module()
        mock_fetch_url.return_value = cluster_query_create_job_with_overwrite_response_success()

        dkron_iface = DkronClusterInterface(module)
        result, changed = dkron_iface.upsert_job()

        mock_fetch_url.assert_called_once_with(
            module,
            'http://172.16.0.1:8080/v1/jobs',
            data=json.dumps({
                'name': 'job1',
                'schedule': '0 */15 * * * *',
                'timezone': 'UTC',
                'concurrency': 'allow',
                'overwrite': True,
                'state': 'present',
                'executor': 'shell',
                'executor_config': {
                    'command': '/bin/echo "hello world"',
                    'cwd': '/tmp'
                }
            }),
            headers=dkron_iface.headers,
            method='POST'
        )
        self.assertEqual(result, {
            'id': 'job',
            'name': 'job',
            'displayname': '',
            'timezone': '',
            'schedule': '0 */15 * * * *',
            'owner': '',
            'owner_email': '',
            'success_count': 145693,
            'error_count': 0,
            'last_success': '2021-05-29T22: 16: 07.018850696Z',
            'last_error': 'null',
            'disabled': 'false',
            'tags': {
                'server': 'true: 1'
            },
            'metadata': 'null',
            'retries': 0,
            'dependent_jobs': 'null',
            'parent_job': '',
            'processors': {},
            'concurrency': 'allow',
            'executor': 'shell',
            'executor_config': {
                'command': '/bin/echo "hello world"',
                'cwd': '/tmp'
            },
            'status': 'success',
            'next': '2021-05-29T22: 17: 07Z'
        })

    # Test create job with overwrite 404 response
    @patch('ansible_collections.knightsg.dkron.plugins.module_utils.classes.fetch_url')
    def test_query_cluster_create_job_with_overwrite_404_response(self, mock_fetch_url):
        set_module_args({
            'endpoint': '172.16.0.1',
            'name': 'job1',
            'schedule': '0 */15 * * * *',
            'shell_executor': {
                'command': '/bin/echo "hello world"',
                'cwd': '/tmp'
            }
        })
        module = dkron_job.init_module()
        mock_fetch_url.return_value = cluster_query_response_http_not_found()

        dkron_iface = DkronClusterInterface(module)

        with self.assertRaises(AnsibleFailJson):
            result = dkron_iface.upsert_job()
            mock_fetch_url.assert_called_once_with(
                module,
                'http://172.16.0.1:8080/v1/jobs',
                headers=dkron_iface.headers,
                method='GET'
            )

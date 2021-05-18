# Based on https://github.com/ansible-collections/community.grafana/blob/main/tests/unit/modules/grafana/grafana_user/test_grafana_user.py
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

from unittest import TestCase
from unittest.mock import call, patch, MagicMock
from ansible.module_utils import basic
from ansible.module_utils._text import to_bytes
from ansible_collections.knightsg.dkron.plugins.modules import dkron_cluster_info
from ansible_collections.knightsg.dkron.plugins.module_utils.classes import DkronClusterInterface 
from ansible_collections.knightsg.dkron.tests.unit.modules.dkron.dkron_cluster_responses import (
	cluster_query_status_response_success
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

	def setUp(self):
		self.mock_module_helper = patch.multiple(basic.AnsibleModule,
													exit_json=exit_json,
													fail_json=fail_json)
		self.mock_module_helper.start()
		self.addCleanup(self.mock_module_helper.stop)


	# Test retrieving cluster status successfully
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
		self.assertEquals(result, {"cluster_info": {"status": {
			"coordinate_resets": 0,
			"encrypted": False,
			"event_queue": 0,
			"event_time": 1,
			"failed": 0,
			"health_score": 0,
			"intent_queue": 0,
			"left": 0,
			"member_time": 2,
			"members": 2,
			"query_queue": 0,
			"query_time": 1
    	}}})

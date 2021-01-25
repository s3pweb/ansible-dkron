#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)

from ansible.module_utils.urls import fetch_url

__metaclass__ = type

class DkronAPIInterface(object):

	def __init__(self, module):

		self.headers['Content-Type'] = 'application/json'

		if module.params['username']:

			if module.params['password']:
				self.headers['Authorization'] = basic_auth_header(module.params['username'], module.params['password'])

			else:
				self.module.fail_json(failed=True, msg="Username without password is invalid")

		if module.params['endpoint']
			self.endpoint = "{proto}://{endpoint}:{port}/v1".format(
				proto=('https' if self.module.params['use_ssl'] else 'http'), 
				endpoint=self.module.params['endpoint'],
				port=self.module.params['port']
			)

		else:
			self.module.fail_json(failed=True, msg="Cluster endpoint is required")

	def query(self, api_path):

		query_url = "{endpoint}{path}".format(endpoint=self.endpoint, path=api_path)
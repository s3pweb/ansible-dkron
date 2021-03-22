from __future__ import (absolute_import, division, print_function)

from ansible.module_utils.urls import fetch_url
import json

__metaclass__ = type

class DkronAPIInterface(object):

	def __init__(self, module):

		self.module = module

		self.headers = {
			'Content-Type':'application/json'
		}

		if module.params['username']:

			if module.params['password']:
				self.headers['Authorization'] = basic_auth_header(module.params['username'], module.params['password'])

			else:
				self.module.fail_json(failed=True, msg="Username without password is invalid")

		if module.params['endpoint']:
			self.uri_root = "{proto}://{endpoint}:{port}/v1".format(
				proto=('https' if self.module.params['use_ssl'] else 'http'), 
				endpoint=self.module.params['endpoint'],
				port=self.module.params['port']
			)

		else:
			self.module.fail_json(failed=True, msg="Cluster endpoint is required")

	def get(self, api_path, success_response=200, params=None):

		query_url = "{endpoint}{path}".format(endpoint=self.uri_root, path=api_path)

		if params:
			for param in params:
				if '?' not in query_url:
					query_url = "{url}?{param_name}={param_value}".format(url=query_url, param_name=param['name'], param_value=param['value'])
				else:
					query_url = "{url}&{param_name}={param_value}".format(url=query_url, param_name=param['name'], param_value=param['value'])
					
		response, info = fetch_url(self.module, query_url, headers=dict(self.headers), method='GET')

		if info['status'] != success_response:
			self.module.fail_json(msg="Dkron API GET request failed: {msg}".format(msg=info['msg']))

		json_response = json.loads(response.read().decode('utf8'))

		if json_response == "":
			return None

		return json_response

	def post(self, api_path, success_response=200, params=None, data=None):

		query_url = "{endpoint}{path}".format(endpoint=self.uri_root, path=api_path)

		if params:
			for param in params:
				if '?' not in query_url:
					query_url = "{url}?{param_name}={param_value}".format(url=query_url, param_name=param['name'], param_value=param['value'])
				else:
					query_url = "{url}&{param_name}={param_value}".format(url=query_url, param_name=param['name'], param_value=param['value'])

		if data:
			response, info = fetch_url(self.module, query_url, headers=dict(self.headers), method='POST', data=json.dumps(data))
		
		else:
			response, info = fetch_url(self.module, query_url, headers=dict(self.headers), method='POST')

		if info['status'] != success_response:
			self.module.fail_json(msg="Dkron API POST request failed: {msg}".format(msg=info['msg']))

		json_out = json.loads(response.read().decode('utf8'))

		return json_out, True

	def delete(self, api_path, success_response=200, params=None, data=None):

		response, info = fetch_url(self.module, api_url, headers=dict(self.headers), method='DELETE')

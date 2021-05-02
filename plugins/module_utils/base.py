from __future__ import (absolute_import, division, print_function)

from ansible.module_utils.urls import url_argument_spec, fetch_url
import json

__metaclass__ = type

class DkronRequestException(Exception):

	def __init__(self, error_code=None):

		if error_code:
			super().__init__("cluster API query failed with error {code}".format(code=error_code))
		else:
			super().__init__("cluster API query failed")

class DkronEmptyResponseException(Exception):

	def __init__(self):
		super().__init__('cluster response is empty')

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
			raise DkronRequestException(info['status'])

		json_response = json.loads(response.read().decode('utf8'))

		if json_response == "":
			raise DkronEmptyResponseException

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
			raise DkronRequestException(info['status'])

		json_response = json.loads(response.read().decode('utf8'))

		if json_response == "":
			raise DkronEmptyResponseException

		return json_response

	def delete(self, api_path, success_response=200, params=None, data=None):
		query_url = "{endpoint}{path}".format(endpoint=self.uri_root, path=api_path)
		response, info = fetch_url(self.module, query_url, headers=dict(self.headers), method='DELETE')

		if info['status'] == 404:
			return {}

		if info['status'] != success_response:
			 raise DkronRequestException(info['status'])

		if response:
			json_response = json.loads(response.read().decode('utf8'))
			return json_response
		else:
			return None
		
def dkron_argument_spec():
	argument_spec = url_argument_spec()

	del argument_spec['force']
	del argument_spec['force_basic_auth']
	del argument_spec['http_agent']

    # These params are common to all modules
	argument_spec.update(
		endpoint=dict(type='str', required=True),
		port=dict(type='int', required=False, default=8080),
		username=dict(type='str', required=False),
        password=dict(type='str', required=False, no_log=True),
        use_ssl=dict(type='bool', required=False, default=False)
	)

	return argument_spec

def dkron_required_together():
	return [['username', 'password']]
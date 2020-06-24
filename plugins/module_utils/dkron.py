#!/usr/bin/env python

from ansible.module_utils.urls import fetch_url
import json

class Dkron(object):

	def __init__(self, module):
		if 'username' in module.params and module.params['username'] != '':
			module.params['url_username'] = module.params['username']

			if 'password' in module.params and module.params['password'] != '':
				module.params['url_password'] = module.params['password']
			else:
				self.module.fail_json(msg="password is blank")

		else:
			self.module.fail_json(msg="username is blank")

		self.module = module
		self.root_url = "{0}://{1}{2}/v1".format(
			('https' if self.module.params['use_ssl'] else 'http'), 
			self.module.params['endpoint'],
			(':' + self.module.params['port'] if 'port' in self.module.params else '')
		)
		self.headers = {
			"Content-Type": "application/json"
		}

	# Return:
	#	* cluster status, and/or
	#	* leader node, and/or
	#	* member nodes, and/or
	#	* list of jobs
	def cluster_info(self):
		data = {}

		if self.module.params['type'] in ['all', 'status']:
			data['status'] = self.cluster_status()

		if self.module.params['type'] in ['all', 'leader']:
			data['leader'] = self.leader_node()

		if self.module.params['type'] in ['all', 'members']:
			data['members'] = self.member_nodes()

		if self.module.params['type'] in ['all', 'jobs']:
			data['jobs'] = self.job_list()

		return False, data, False

	# Return:
	#	* cluster status
	def cluster_status(self, http_call=fetch_url):
		api_url = api_url = "{0}/".format(self.root_url)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers)

		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain cluster status: {0}".format(info['msg']))

		json_out = self._read_response(response)

		return json_out

	# Return:
	#	* leader node
	def leader_node(self, http_call=fetch_url):
		api_url = api_url = "{0}/leader".format(self.root_url)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers)
		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain leader info: {0}".format(info['msg']))

		json_out = self._read_response(response)

		if json_out == "":
			return None

		return json_out

	# Return:
	#	* cluster members
	def member_nodes(self, http_call=fetch_url):
		api_url = "{0}/members".format(self.root_url)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers)
		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain list of cluster member nodes: {0}".format(info['msg']))

		json_out = self._read_response(response)

		return [member['Addr'] for member in json_out]

	# Return:
	#	* list of jobs
	def job_list(self, http_call=fetch_url):
		api_url = api_url = "{0}/jobs".format(self.root_url)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers)
		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain list of jobs: {0}".format(info['msg']))

		json_out = self._read_response(response)

		return [job['name'] for job in json_out]

	# Return:
	#	* job configuration
	#	* execution history
	def job_info(self):
		api_url = "{0}/jobs/{1}".format(self.root_url, self.module.params.name)
		headers = dict(self.headers)

		data = {}

		data['config'] = self.job_config
		data['history'] = self.job_history

		return False, data, False

	# Return:
	#	* job configuration
	def job_config(self):
		api_url = "{0}/jobs/{1}".format(self.root_url, self.module.params.name)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers)
		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain jbo configuration: {0}".format(info['msg']))

		json_out = self._read_response(response)

		return json_out

	# Return:
	#	* job execution history
	def job_history(self):
		api_url = "{0}/jobs/{1}/executions".format(self.root_url, self.module.params.name)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers)
		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain job execution history: {0}".format(info['msg']))

		json_out = self._read_response(response)

		return json_out

	# Return:
	#	* job create/update status
	def upsert_job(self):
		pass

	# Return:
	#	* job delete result
	def delete_job(self):
		api_url = "{0}/jobs/{1}".format(self.root_url, self.module.params.name)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers, method='DELETE')
		if info['status'] != 200:
			self.module.fail_json(msg="failed to delete job: {0}".format(info['msg']))

		json_out = self._read_response(response)

		return False, json_out, True

	# Return:
	#	* job execution successful
	def trigger_job(self):
		api_url = "{0}/jobs/{1}".format(self.root_url, self.module.params.name)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers, method='POST')
		if info['status'] != 200:
			self.module.fail_json(msg="failed to trigger job: {0}".format(info['msg']))

		json_out = self._read_response(response)

		return False, json_out, True

	# Return:
	#	* job enable/disable status
	def toggle_job(self):
		api_url = "{0}/jobs/{1}/toggle".format(self.root_url, self.module.params.name)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers, method='POST')
		if info['status'] != 200:
			self.module.fail_json(msg="failed to trigger: {0}".format(info['msg']))

		json_out = self._read_response(response)

		return False, json_out, True

	def _read_response(self, response):
		try:
		    return json.loads(response.read())
		except Exception:
		    return ""

#!/usr/bin/env python

from ansible.module_utils.urls import fetch_url
import json

class DkronAPI(object):

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
		self.root_url = "{proto}://{endpoint}:{port}/v1".format(
			proto=('https' if self.module.params['use_ssl'] else 'http'), 
			endpoint=self.module.params['endpoint'],
			port=self.module.params['port']
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
		changed = False

		if self.module.params['type'] in ['all', 'status']:
			status = self.get_cluster_status()

			if status is not None:
				data['status'] = status
				changed = True

		if self.module.params['type'] in ['all', 'leader']:
			leader = self.get_leader_node()

			if leader is not None:
				data['leader'] = leader
				changed = True

		if self.module.params['type'] in ['all', 'members', 'nodes']:
			members = self.get_member_nodes()

			if members is not None:
				data['members'] = members
				changed = True

		if self.module.params['type'] in ['all', 'jobs']:
			jobs = self.get_job_list()
			
			if jobs is not None:
				data['jobs'] = jobs
				changed = True

		return data, changed

	# Return:
	#	* cluster status
	def get_cluster_status(self, http_call=fetch_url):
		api_url = api_url = "{0}/".format(self.root_url)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers)

		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain cluster status: {0}".format(info['msg']))

		json_out = self._read_response(response)

		if json_out == "":
			return None

		return json_out

	# Return:
	#	* leader node
	def get_leader_node(self, http_call=fetch_url):
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
	def get_member_nodes(self, http_call=fetch_url):
		api_url = "{0}/members".format(self.root_url)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers)
		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain list of cluster member nodes: {0}".format(info['msg']))

		json_out = self._read_response(response)

		if json_out == "":
			return None

		return [member['Addr'] for member in json_out]

	# Return:
	#	* list of jobs
	def get_job_list(self, http_call=fetch_url):
		api_url = api_url = "{0}/jobs".format(self.root_url)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers)
		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain list of jobs: {0}".format(info['msg']))

		json_out = self._read_response(response)

		if json_out == "":
			return None

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

		return data, False

	# Return:
	#	* job configuration
	def job_config(self):
		api_url = "{0}/jobs/{1}".format(self.root_url, self.module.params.name)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers)
		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain job configuration: {0}".format(info['msg']))

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

		return json_out, True

	# Return:
	#	* job execution successful
	def trigger_job(self):
		api_url = "{0}/jobs/{1}".format(self.root_url, self.module.params.name)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers, method='POST')
		if info['status'] != 200:
			self.module.fail_json(msg="failed to trigger job: {0}".format(info['msg']))

		json_out = self._read_response(response)

		return json_out, True

	# Return:
	#	* job enable/disable status
	def toggle_job(self):
		api_url = "{0}/jobs/{1}/toggle".format(self.root_url, self.module.params.name)
		headers = dict(self.headers)

		response, info = http_call(self.module, api_url, headers=headers, method='POST')
		if info['status'] != 200:
			self.module.fail_json(msg="failed to trigger: {0}".format(info['msg']))

		json_out = self._read_response(response)

		return json_out, True

	def _read_response(self, response):
		try:
		    return json.loads(response.read())
		except Exception:
		    return ""

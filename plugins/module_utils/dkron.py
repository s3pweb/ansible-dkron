#!/usr/bin/env python

from ansible.module_utils.urls import fetch_url
from operator import itemgetter
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
	def get_cluster_info(self):
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
	def get_cluster_status(self):
		api_url = api_url = "{0}/".format(self.root_url)

		response, info = fetch_url(self.module, api_url, headers=dict(self.headers), method='GET')

		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain cluster status: {msg}".format(msg=info['msg']))

		json_out = json.loads(response.read().decode('utf8'))

		if json_out == "":
			return None

		return json_out

	# Return:
	#	* leader node
	def get_leader_node(self):
		api_url = api_url = "{0}/leader".format(self.root_url)

		response, info = fetch_url(self.module, api_url, headers=dict(self.headers), method='GET')

		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain leader info: {msg}".format(msg=info['msg']))

		json_out = json.loads(response.read().decode('utf8'))

		if json_out == "":
			return None

		return json_out

	# Return:
	#	* cluster members
	def get_member_nodes(self):
		api_url = "{0}/members".format(self.root_url)

		response, info = fetch_url(self.module, api_url, headers=dict(self.headers))
		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain list of cluster member nodes: {msg}".format(msg=info['msg']))

		json_out = json.loads(response.read().decode('utf8'))

		if json_out == "":
			return None

		return [member['Addr'] for member in json_out]

	# Return:
	#	* list of jobs
	def get_job_list(self):
		api_url = api_url = "{0}/jobs".format(self.root_url)

		response, info = fetch_url(self.module, api_url, headers=dict(self.headers))
		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain list of jobs: {msg}".format(msg=info['msg']))

		json_out = json.loads(response.read().decode('utf8'))

		if json_out == "":
			return None

		return [job['name'] for job in json_out]

	# Return:
	#	* running job executions
	def get_running_jobs(self):
		api_url = api_url = "{0}/busy".format(self.root_url)

		response, info = fetch_url(self.module, api_url, headers=dict(self.headers), method='GET')

		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain list of busy jobs: {msg}".format(msg=info['msg']))

		json_out = json.loads(response.read().decode('utf8'))

		if json_out == "":
			return None

		return [job['job_name'] for job in json_out]

	# Return:
	#	* job configuration
	#	* execution history
	def get_job_info(self):
		data = {}
		changed = False

		job_info = []

		if not self.module.params['job_names']:
			jobs = self.get_job_list()
		else:
			jobs = self.module.params['job_names']

		for job_name in jobs:
			if self.module.params['limit_history'] != 0:
				job_info.append({
					'configuration': self.get_job_config(job_name),
					'history': sorted(self.get_job_history(job_name), key=itemgetter('started_at'), reverse=True)[:self.module.params['limit_history']]
				})
			else:
				job_info.append({
					'configuration': self.get_job_config(job_name),
					'history': sorted(self.get_job_history(job_name), key=itemgetter('started_at'), reverse=True)
				})				

		changed = True

		return job_info, changed

	# Return:
	#	* job configuration
	def get_job_config(self, job_name):
		api_url = "{root_url}/jobs/{job_name}".format(root_url=self.root_url, job_name=job_name)

		response, info = fetch_url(self.module, api_url, headers=dict(self.headers))

		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain job configuration: {msg}".format(msg=info['msg']))

		json_out = json.loads(response.read().decode('utf8'))

		return json_out

	# Return:
	#	* job execution history
	def get_job_history(self, job_name):
		api_url = "{root_url}/jobs/{job_name}/executions".format(root_url=self.root_url, job_name=job_name)

		response, info = fetch_url(self.module, api_url, headers=dict(self.headers))
		if info['status'] != 200:
			self.module.fail_json(msg="failed to obtain job execution history: {msg}".format(msg=info['msg']))

		json_out = json.loads(response.read().decode('utf8'))

		return json_out

	# Return:
	#	* job create/update status
	def upsert_job(self, job_config=None):

		if not job_config:
			self.module.fail_json(msg="job configuration not valid: {config}".format(config=job_config))

		# If the overwrite flag is False then just return the content of the existing job if it already exists.
		if not self.module.params['overwrite']:
			job_list = self.get_job_list()

			if self.module.params['job_name'] in job_list:
				job_config = self.get_job_config(self.module.params['job_name'])
				
				return job_config, False

		# No existing job config has been returned so continue and create/overwrite the job.
		api_url = "{0}/jobs".format(self.root_url)

		if self.module.params['run_on_create']:
			api_url = "{url}?runoncreate=true".format(url=api_url)

		response, info = fetch_url(self.module, api_url, headers=dict(self.headers), method='POST', data=json.dumps(job_config))
		if info['status'] != 201:
			self.module.fail_json(msg="failed to create or update job: {msg}".format(msg=info['msg']))

		json_out = json.loads(response.read().decode('utf8'))

		return json_out, True

	# Return:
	#	* job delete result
	def delete_job(self):
		job_list = self.get_job_list()

		if self.module.params['job_name'] in job_list:
			api_url = "{0}/jobs/{1}".format(self.root_url, self.module.params['job_name'])

			response, info = fetch_url(self.module, api_url, headers=dict(self.headers), method='DELETE')
			if info['status'] != 200:
				self.module.fail_json(msg="failed to delete job: {msg}".format(msg=info['msg']))

			json_out = json.loads(response.read().decode('utf8'))

			return json_out, True

		return None, False

	# Return:
	#	* job execution successful
	def trigger_job(self, job_name):
		api_url = "{0}/jobs/{1}".format(self.root_url, job_name)

		response, info = fetch_url(self.module, api_url, headers=dict(self.headers), method='POST')
		if info['status'] != 200:
			self.module.fail_json(msg="failed to trigger job: {msg}".format(msg=info['msg']))

		json_out = json.loads(response.read().decode('utf8'))

		return json_out, True

	# Return:
	#	* job enable/disable status
	def toggle_job(self):
		job_list = self.get_job_list()

		if self.module.params['job_name'] in job_list:
			api_url = "{0}/jobs/{1}/toggle".format(self.root_url, self.module.params['job_name'])

			response, info = fetch_url(self.module, api_url, headers=dict(self.headers), method='POST')
			if info['status'] != 200:
				self.module.fail_json(msg="failed to trigger: {msg}".format(msg=info['msg']))

			json_out = json.loads(response.read().decode('utf8'))

			return json_out, True

	def _read_response(self, response):
		try:
		    return json.loads(response.read())
		except Exception:
		    return ""

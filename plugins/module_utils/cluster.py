from __future__ import (absolute_import, division, print_function)

from .base import DkronAPIInterface

class DkronCluster(DkronAPIInterface):

	def __init__(self, module):
		super().__init__(module)

	def info(self):
		data = {}

		if self.module.params['type'] in ['all', 'status']:
			data['status'] = self.cluster_status()

		if self.module.params['type'] in ['all', 'leader']:
			data['leader'] = self.leader_node()

		if self.module.params['type'] in ['all', 'members', 'nodes']:
			data['members'] = self.member_nodes()

		if self.module.params['type'] in ['all', 'jobs']:
			data['jobs'] = self.job_list()

		return data, True

	## Return:
	#	* cluster (serf) status
	def cluster_status(self):
		uri = "/"

		try:
			response = self.get(uri)

			if 'serf' in response:
				status = response['serf']
			else:
				status = {}

		except DkronLookupException as e:
			self.module.fail_json(msg="cluster status query failed ({err})".format(err=str(e)))

		except DkronEmptyResponseException as e:
			self.module.fail_json(msg="cluster status query failed ({err})".format(err=str(e)))

		return status

	## Return:
	#	* leader node address
	def leader_node(self):
		uri = "/leader"

		try:
			response = self.get(uri)

			if response:
				leader = response['Addr']
			else:
				leader = None

		except DkronLookupException as e:
			self.module.fail_json(msg="cluster leader query failed ({err})".format(err=str(e)))

		except DkronEmptyResponseException as e:
			self.module.fail_json(msg="cluster leader query failed ({err})".format(err=str(e)))

		return leader

	## Return:
	#	* cluster members
	def member_nodes(self):
		uri = "/members"

		try:
			response = self.get(uri)
			node_list = [member['Addr'] for member in response]

		except DkronLookupException as e:
			self.module.fail_json(msg="cluster members query failed ({err})".format(err=str(e)))

		except DkronEmptyResponseException as e:
			return []

		return node_list

	## Return:
	#	* list of jobs
	def job_list(self):
		uri = "/jobs"

		try:
			response = self.get(uri)
			if self.module.params['busy_only']:
				job_list = [job['name'] for job in response if job['name'] in self.running_jobs()]
			else:
				job_list = [job['name'] for job in response]

		except DkronLookupException as e:
			self.module.fail_json(msg="cluster job list query failed ({err})".format(err=str(e)))

		except DkronEmptyResponseException as e:
			return []

		return job_list

	## Return:
	#	* running job executions
	def running_jobs(self):
		uri = "/busy"

		try:
			response = self.get(uri)
			job_list = [job['job_name'] for job in response]

		except DkronLookupException as e:
			self.module.fail_json(msg="cluster status query failed ({err})".format(err=str(e)))

		except DkronEmptyResponseException as e:
			return []

		return job_list
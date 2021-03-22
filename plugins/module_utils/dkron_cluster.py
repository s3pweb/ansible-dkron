from __future__ import (absolute_import, division, print_function)

from .dkron_api_interface import DkronAPIInterface

class DkronCluster(DkronAPIInterface):

	def __init__(self, module):
		super().__init__(module)

	def get_cluster_info(self):
		data = {}
		changed = False

		if self.module.params['type'] in ['all', 'status']:
			status, changed = self.get_cluster_status()

			data['status'] = status
			changed = True

		if self.module.params['type'] in ['all', 'leader']:
			leader, changed = self.get_leader_node()

			data['leader'] = leader
			changed = True

		if self.module.params['type'] in ['all', 'members', 'nodes']:
			members = self.get_member_nodes()

			data['members'] = members
			changed = True

		if self.module.params['type'] in ['all', 'jobs']:
			jobs = self.get_job_list()
			
			if jobs:
				data['jobs'] = jobs
				changed = True


		return data, changed

	## Return:
	#	* cluster (serf) status
	def get_cluster_status(self):
		uri = "/"

		return self.get(uri)

	## Return:
	#	* leader node address
	def get_leader_node(self):
		uri = "/leader"

		response = self.get(uri)
		if response:
			leader = response['Addr']
		else:
			leader = None

		return leader

	## Return:
	#	* cluster members
	def get_member_nodes(self):
		uri = "/members"

		response = self.get(uri)

		if response:
			return [member['Addr'] for member in response]
		else:
			return []

	## Return:
	#	* list of jobs
	def get_job_list(self):
		uri = "/jobs"

		response = self.get(uri)

		if response:
			if self.module.params['busy_only']:
				running_jobs = self.get_running_jobs()

				return [job['name'] for job in response if job['name'] in running_jobs]
			else:
				return [job['name'] for job in response]
		else:
			return None

	## Return:
	#	* running job executions
	def get_running_jobs(self):
		uri = "/busy"

		response = self.get(uri)

		if response:
			return [job['job_name'] for job in response]
		else:
			return []
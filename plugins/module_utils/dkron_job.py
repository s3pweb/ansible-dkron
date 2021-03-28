from __future__ import (absolute_import, division, print_function)

from .dkron_module_base import DkronAPIInterface, DkronLookupException, DkronEmptyResponseException
from operator import itemgetter

class DkronJob(DkronAPIInterface):

	job_attributes = [
		'name',
		'displayname',
		'schedule',
		'timezone',
		'owner',
		'owner_email',
		'disabled',
		'tags',
		'metadata',
		'retries',
		'parent_job',
		'concurrency',
		'processors',
		'executor',
		'executor_config'
	]
	
	def __init__(self, module):
		
		super().__init__(module)

		if 'name' in self.module.params:
			self.name = self.module.params['name']

		if 'display_name' in self.module.params:
			self.displayname = self.module.params['display_name']

		if 'file_processor' in self.module.params or 'log_processor' in self.module.params or 'syslog_processor' in self.module.params:
			self.processors = {}

			if 'file_processor' in self.module.params:
				self.processors['files'] = self.module.params['file_processor']

			if 'log_processor' in self.module.params:
				self.processors['log'] = self.module.params['log_processor']

			if 'syslog_processor' in self.module.params:
				self.processors['syslog'] = self.module.params['syslog_processor']

		if 'shell_executor' in self.module.params:
			self.executor = 'shell'
			self.executor_config = self.module.params['shell_executor']

		if 'http_executor' in self.module.params:
			self.executor = 'http'
			self.executor_config = self.module.params['http_executor']

		if 'limit_history' in self.module.params:
			self.limit_history = self.module.params['limit_history']

	###
	# Description: Query the job configuration.
	#
	# Return:
	#   - job configuration dict
	def config(self):
		uri = "/jobs/{job_name}".format(job_name=self.name)

		try:
			response = self.get(uri)
		except DkronLookupException as e:
			self.module.fail_json(msg="job config query failed ({err})".format(err=str(e)))
		except DkronEmptyResponseException as e:
			self.module.fail_json(msg="job config query failed ({err})".format(err=str(e)))

		return response, True

	###
	# Description: Query the job execution history.
	#
	# Return:
	#   - job executions list (limited list if specified)
	def history(self):
		uri = "/jobs/{job_name}/executions".format(job_name=self.name)

		response = self.get(uri)

		try:
			response = self.get(uri)

			if self.limit_history != 0:
				history = sorted(response, key=itemgetter('started_at'), reverse=True)[:self.limit_history]
			else:
				history = sorted(response, key=itemgetter('started_at'), reverse=True)
		except DkronLookupException as e:
			self.module.fail_json(msg="job execution history query failed ({err})".format(err=str(e)))
		except DkronEmptyResponseException as e:
			self.module.fail_json(msg="job execution history query failed ({err})".format(err=str(e)))

		return history, True

	###
	# Description: Update a job in a cluster from the job's instance configuration.
	#
	# Return:
	#   - job create/update status
	def upsert(self):

		uri = "/jobs"
		params = None

		if self.run_on_create:
			params = { 'run_on_create': 'true' }

		request_data = {}

		for item in self.job_attributes:
			if self.__dict__[item]:
				data[item] = self.__dict__[item]

		response = self.post(uri, success_response=201, params=params, data=request_data)

		return response, True
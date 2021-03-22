from __future__ import (absolute_import, division, print_function)

from .dkron_api_interface import DkronAPIInterface
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
	
	def __init__(self, **kwargs):
		
		super().__init__(module)
		self.__dict__.update(kwargs)

		if self.job_name:
			self.name = self.job_name

		if self.display_name:
			self.displayname = self.display_name

		if not self.file_processor and not self.log_processor and not self.syslog_processor:
			raise Exception('Job instance creation failed, no valid processor supplied')
		else:
			self.processors = {}

			if self.file_processor:
				self.processors['files'] = self.file_processor
				# Let's free up some memory
				del self.file_processor

			if self.log_processor:
				self.processors['log'] = self.log_processor
				del self.log_processor

			if self.syslog_processor:
				self.processors['syslog'] = self.syslog_processor
				del self.syslog_processor

		if self.shell_executor:
			self.executor = 'shell'
			self.executor_config = self.shell_executor
			# Let's free up some memory
			del self.shell_executor

		if self.http_executor:
			self.executor = 'http'
			self.executor_config = self.http_executor
			del self.http_executor

	###
	# Description: Query the job configuration.
	#
	# Return:
	#   - job configuration dict
	def get_job_config():
		uri = "/jobs/{job_name}".format(job_name=self.name)

		response = self.get(uri)

		return response

	###
	# Description: Query the job execution history.
	#
	# Return:
	#   - job executions list (limited list if specified)
	def get_job_history():
		uri = "/jobs/{job_name}/executions".format(job_name=self.name)

		response = self.get(uri)

		if self.limit_history != 0:
			history = sorted(response, key=itemgetter('started_at'), reverse=True)[:self.limit_history]
		else:
			history = sorted(response, key=itemgetter('started_at'), reverse=True)

		return history

	###
	# Description: Update a job in a cluster from the job's instance configuration.
	#
	# Return:
	#   - job create/update status
	def to_data(self):

		uri = "/jobs"
		params = None

		if self.run_on_create:
			params = { 'run_on_create': 'true' }

		request_data = {}

		for item in self.job_attributes:
			if self.__dict__[item]:
				data[item] = self.__dict__[item]

		response = self.post(uri, success_response=201, params=params, data=request_data)
		changed = True

		return response, changed
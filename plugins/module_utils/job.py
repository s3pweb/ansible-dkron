from __future__ import (absolute_import, division, print_function)

from .base import DkronAPIInterface, DkronLookupException, DkronEmptyResponseException
from operator import itemgetter

class DkronJob(DkronAPIInterface):

	simple_job_attributes = [
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
		'run_on_create',
		'concurrency',
		'overwrite',
		'limit_history',
		'toggle',
		'state'
	]
	
	complex_job_attributes = [
		'file_processor',
		'log_processor',
		'syslog_processor',
		'shell_executor',
		'http_executor'
	]

	def __init__(self, module, load_config=True):
		
		super().__init__(module)

		for job_attribute in self.simple_job_attributes:
			if job_attribute not in self.complex_job_attributes and job_attribute in self.module.params.keys():
				setattr(self, job_attribute, self.module.params[job_attribute])

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

		if load_config:
			self.read_config()

	###
	# Description: Query the job configuration and set instance params from response fields.
	#
	# Return:
	#   - True
	def read_config(self):
		uri = "/jobs/{job_name}".format(job_name=self.name)

		try:
			response = self.get(uri)
		except DkronLookupException as e:
			self.module.fail_json(msg="job config query failed ({err})".format(err=str(e)))
		except DkronEmptyResponseException as e:
			self.module.fail_json(msg="job config query failed ({err})".format(err=str(e)))

		if not response:
			return False

		for field in response:
			setattr(self, field, response[field])
			return True	

	def get_config(self):

		config = {}

		for attribute in self.simple_job_attributes:
			config[attribute] = getattr(self, attribute)

		return config

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
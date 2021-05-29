from __future__ import (absolute_import, division, print_function)

from ansible.module_utils.urls import url_argument_spec, fetch_url
from operator import itemgetter
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


class DkronClusterInterface(object):

    def __init__(self, module):
        self.module = module
        self.headers = {
            'Content-Type': 'application/json'
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

    def cluster_status(self):
        uri = "/"

        try:
            response = self.get(uri)

            if 'serf' in response:
                status = response['serf']
            else:
                status = {}

            return status

        except DkronRequestException as e:
            self.module.fail_json(msg="cluster status query failed ({err})".format(err=str(e)))

        except DkronEmptyResponseException as e:
            self.module.fail_json(msg="cluster status query failed ({err})".format(err=str(e)))

    def leader_node(self):
        uri = "/leader"

        try:
            response = self.get(uri)

            if response:
                leader = response['Addr']
            else:
                leader = ''

            return leader

        except DkronRequestException as e:
            self.module.fail_json(msg="cluster leader query failed ({err})".format(err=str(e)))

        except DkronEmptyResponseException as e:
            self.module.fail_json(msg="cluster leader query failed ({err})".format(err=str(e)))

    def member_nodes(self):
        uri = "/members"

        try:
            response = self.get(uri)
            node_list = [member['Addr'] for member in response]

            return node_list

        except DkronRequestException as e:
            self.module.fail_json(msg="cluster members query failed ({err})".format(err=str(e)))

        except DkronEmptyResponseException as e:
            return []

    def job_list(self):
        if not self.module.params['active_only']:
            uri = "/jobs"

            try:
                response = self.get(uri)
                job_list = [job['name'] for job in response]

                return job_list

            except DkronRequestException as e:
                self.module.fail_json(msg="cluster job list query failed ({err})".format(err=str(e)))

            except DkronEmptyResponseException as e:
                return []

        else:
            uri = "/busy"

            try:
                response = self.get(uri)
                job_list = [job['job_name'] for job in response]

                return job_list

            except DkronRequestException as e:
                self.module.fail_json(msg="cluster status query failed ({err})".format(err=str(e)))

            except DkronEmptyResponseException as e:
                return []


    def get_job_config(self, job_name=None):
        if job_name:
            uri = "/jobs/{name}".format(name=job_name)
        else:
            return False

        try:
            response = self.get(uri)

            if not response:
                return {}

            return response

        except DkronRequestException as e:
            self.module.fail_json(msg="job config query failed ({err})".format(err=str(e)))

        except DkronEmptyResponseException as e:
            self.module.fail_json(msg="job config query failed ({err})".format(err=str(e)))

    def compare_job_configs(self):
        # Use self.get_job_config to compare new config with one in cluster
        pass

    def get_job_history(self, job_name=None):
        if job_name:
            uri = "/jobs/{name}/executions".format(name=job_name)
        else:
            return False

        try:
            response = self.get(uri)

            if not response:
                return []

            if self.module.params['limit_history'] != 0:
                history = sorted(response, key=itemgetter('started_at'), reverse=True)[:self.module.params['limit_history']]
            else:
                history = sorted(response, key=itemgetter('started_at'), reverse=True)

            return history

        except DkronRequestException as e:
            self.module.fail_json(msg="job execution history query failed ({err})".format(err=str(e)))

        except DkronEmptyResponseException as e:
            self.module.fail_json(msg="job execution history query failed ({err})".format(err=str(e)))

    def upsert_job(self):

        uri = "/jobs"

        simple_options = [
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
        params = None

        job_config = {
            'name': self.module.params['name']
        }

        # Add basic parameters directly to job config
        for param in self.module.params:
            if self.module.params[param] and param in simple_options:
                job_config[param] = self.module.params[param]

        # Construct complex parameters and add to job config
        if self.module.params['concurrency']:
            job_config['concurrency'] = 'allow'
        else:
            job_config['concurrency'] = 'forbid'

        if self.module.params['file_processor'] or self.module.params['log_processor'] or self.module.params['syslog_processor']:
            job_config['processors'] = {}

            if self.module.params['file_processor']:
                job_config['processors']['files'] = self.module.params['file_processor']

            if self.module.params['log_processor']:
                job_config['processors']['log'] = self.module.params['log_processor']

            if self.module.params['syslog_processor']:
                job_config['processors']['syslog'] = self.module.params['syslog_processor']

        if self.module.params['shell_executor']:
            job_config['executor'] = 'shell'
            job_config['executor_config'] = self.module.params['shell_executor']
        elif self.module.params['http_executor']:
            job_config['executor'] = 'http'
            job_config['executor_config'] = self.module.params['http_executor']
        else:
            self.module.fail_json(msg="Module requires shell_executor or http_executor parameter specified.")

        if self.module.params['run_on_create']:
            params = {'run_on_create': 'true'}

        if not self.module.check_mode:
            try:
                response = self.post(uri, success_response=201, params=params, data=job_config)

                return response, True

            except DkronRequestException as e:
                self.module.fail_json(msg="job create/update failed ({err})".format(err=str(e)))

            except Exception as e:
                self.module.fail_json(msg="unknown error ({err})".format(err=str(e)))

        else:
            return {}, True

    def delete_job(self, job_name=None):
        if job_name:
            uri = "/jobs/{name}".format(name=job_name)
        else:
            self.module.fail_json(msg="unable to delete job, job name not provided")

        if not self.module.check_mode:
            try:
                response = self.delete(uri)

                return response, True

            except DkronRequestException as e:
                self.module.fail_json(msg="job deletion failed ({err})".format(err=str(e)))

            except Exception as e:
                self.module.fail_json(msg="unknown error ({err})".format(err=str(e)))

        else:
            return {}, True

    def toggle_job(self, job_name=None):
        if job_name:
            uri = "/jobs/{name}/toggle".format(name=job_name)
        else:
            self.module.fail_json(msg="unable to toggle job, job name not provided")

        if not self.module.check_mode:
            try:
                response = self.post(uri)

                return {'disabled': response['disabled']}, True

            except DkronRequestException as e:
                self.module.fail_json(msg="job toggle failed ({err})".format(err=str(e)))

            except Exception as e:
                self.module.fail_json(msg="unknown error ({err})".format(err=str(e)))

        else:
            return {}, True

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

        json_response = json.loads(response.read())

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

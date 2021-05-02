#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# Copyright: (c) 2020, Guy Knights <contact@guyknights.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: dkron_job_info
short_description: Gathers information about jobs in a Dkron cluster
description:
- Gathers information about jobs in a Dkron cluster.
options:
  names:
    description:
      - Name (or list of names) of job to query.
      - Will query all jobs if omitted.
    type: list
    aliases:
      - name
  limit_history:
    description
      - Limit the history returned for each job to the amount specified by this parameter (eg. 5)
      - Will return full history for each job if omitted.
    type: int
extends_documentation_fragment:
- knightsg.dkron.connect

seealso:
- module: knightsg.dkron.dkron_job
- module: knightsg.dkron.dkron_cluster_info

author:
- Guy Knights (contact@guyknights.com)
'''

EXAMPLES = r'''
- name: Get config and full history for all defined jobs
  knightsg.dkron.dkron_job_info:
    endpoint: 192.168.1.1

- name: Get config and full history for a list of jobs from secured cluster
  knightsg.dkron.dkron_job_info:
    endpoint: myclusterendpoint.com
    use_ssl: true
    username: myusername
    password: mypassword
    job_names:
      - my_job_1
      - my_job_2
      - my_job_3

- name: Get config for all defined jobs but limit history to last execution only
  knightsg.dkron.dkron_job_info:
    endpoint: 192.168.1.1
    limit_history: 1

'''

RETURN = r'''
configuration:
  description: Job configuration as returned by the Dkron cluster API (https://dkron.io/api/).
  returned: always
  type: dict
  sample: { "concurrency": "allow", "dependent_jobs": null, "disabled": false, "displayname": "", "error_count": 0, "executor": "shell", "executor_config": { "command": "/bin/true" }, "last_error": null, "last_success": "2020-11-14T17:32:15.010781048Z", "metadata": null, "name": "job", "next": "2020-11-14T17:33:15Z", "owner": "guy", "owner_email": "someone@example.com", "parent_job": "", "processors": {}, "retries": 0, "schedule": "@every 1m", "status": "success", "success_count": 185, "tags": { "server": "true:1" }, "timezone": ""}
  contains: see Dkron usage documentation for complete breakdown of returned values (https://dkron.io/usage/)
history:
  description: List of job executions with result status.
  returned: always
  type: dict
  sample: { "attempt": 1, "finished_at": "2020-11-14T17:32:15.010781048Z", "group": 1605375135000263778, "job_name": "job", "node_name": "myhostname", "started_at": "2020-11-14T17:32:15.007570195Z", "success": true }
  
'''

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.knightsg.dkron.plugins.module_utils.base import DkronAPIInterface, DkronRequestException, DkronEmptyResponseException, dkron_argument_spec, dkron_required_together
from operator import itemgetter

def get_job_config(module, api):
  uri = "/jobs/{name}".format(name=module.params['name'])

  try:
    response = api.get(uri)

  except DkronRequestException as e:
    self.module.fail_json(msg="job config query failed ({err})".format(err=str(e)))

  except DkronEmptyResponseException as e:
    self.module.fail_json(msg="job config query failed ({err})".format(err=str(e)))

  if not response:
    return False
  
  return response 


###
# Description: Query the job execution history.
#
# Return:
#   - job executions list (limited list if specified)
#   - empty list if response is empty
def get_job_history(module, api):
  uri = "/jobs/{name}/executions".format(name=module.params['name'])

  response = api.get(uri)

  try:
    response = api.get(uri)

    if not response:
      return []

    if module.params['limit_history'] != 0:
      history = sorted(response, key=itemgetter('started_at'), reverse=True)[:module.params['limit_history']]
    else:
      history = sorted(response, key=itemgetter('started_at'), reverse=True)

  except DkronRequestException as e:
    module.fail_json(msg="job execution history query failed ({err})".format(err=str(e)))
    
  except DkronEmptyResponseException as e:
    module.fail_json(msg="job execution history query failed ({err})".format(err=str(e)))

  return history

if __name__ == '__main__':
    module_args = dkron_argument_spec()
    module_args.update(
      names=dict(type='list', required=False, aliases=['name']),
      limit_history=dict(type='int', required=False, default=0)
    )

    result = dict(
        changed=False,
        failed=False,
        ansible_module_results={}
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
        required_together=dkron_required_together()
    )

    data = {}
    api = DkronAPIInterface(module)

    data['job_config'] = get_job_config(module, api)
    data['history'] = get_job_history(module, api)

    if data['job_config'] == False:
      result['failed'] = True
    else:
      result['ansible_module_results'] = data
      result['changed'] = True
    
    module.exit_json(**result)
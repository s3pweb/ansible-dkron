#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)

# Copyright: (c) 2920, Guy Knights <contact@guyknights.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: dkron_cluster_info
short_description: Gathers information about a Dkron cluster
description:
- Gathers information about a Dkron cluster.
options:
  type:
    description:
      - Which information to return.
    type: str
    choices: [ all, status , leader , members , nodes , jobs ]
    default: all
  busy_only:
    description:
      - If set to true only currently executing jobs will be returned in a returned jobs list.
      - Has an effect only if a job list is returned, eg. type = 'all' or 'jobs'.
    type: bool
    default: False
extends_documentation_fragment:
- knightsg.dkron.connect

seealso:
- module: knightsg.dkron.dkron_job_info
- module: knightsg.dkron.dkron_job

author:
- Guy Knights (contact@guyknights.com)
'''

EXAMPLES = r'''
- name: Get all cluster info
  knightsg.dkron.dkron_cluster_info:
    endpoint: 192.168.1.1

- name: Get only cluster member list (from secured cluster)
  knightsg.dkron.dkron_cluster_info:
    endpoint: myclusterendpoint.com
    use_ssl: true
    username: myusername
    password: mypassword
    type: members

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
from ansible_collections.knightsg.dkron.plugins.module_utils.base import DkronAPIInterface, DkronLookupException, DkronEmptyResponseException, dkron_argument_spec, dkron_required_together

def cluster_status(module, api):
  uri = "/"

  try:
    response = api.get(uri)

    if 'serf' in response:
      status = response['serf']
    else:
      status = {}

  except DkronLookupException as e:
    module.fail_json(msg="cluster status query failed ({err})".format(err=str(e)))

  except DkronEmptyResponseException as e:
    module.fail_json(msg="cluster status query failed ({err})".format(err=str(e)))

  return status

def leader_node(module, api):
  uri = "/leader"

  try:
    response = api.get(uri)

    if response:
      leader = response['Addr']
    else:
      leader = None

  except DkronLookupException as e:
    module.fail_json(msg="cluster leader query failed ({err})".format(err=str(e)))

  except DkronEmptyResponseException as e:
    module.fail_json(msg="cluster leader query failed ({err})".format(err=str(e)))

  return leader

def member_nodes(module, api):
  uri = "/members"

  try:
    response = api.get(uri)
    node_list = [member['Addr'] for member in response]

  except DkronLookupException as e:
    module.fail_json(msg="cluster members query failed ({err})".format(err=str(e)))

  except DkronEmptyResponseException as e:
    return []

  return node_list

def job_list(module, api):
  uri = "/jobs"

  try:
    response = api.get(uri)
    if 'busy_only' in module.params and module.params['busy_only']:
      job_list = [job['name'] for job in response if job['name'] in running_jobs(module, api)]
    else:
      job_list = [job['name'] for job in response]

  except DkronLookupException as e:
    module.fail_json(msg="cluster job list query failed ({err})".format(err=str(e)))

  except DkronEmptyResponseException as e:
    return []

  return job_list

def running_jobs(module, api):
  uri = "/busy"

  try:
    response = api.get(uri)
    job_list = [job['job_name'] for job in response]

  except DkronLookupException as e:
    module.fail_json(msg="cluster status query failed ({err})".format(err=str(e)))

  except DkronEmptyResponseException as e:
    return []

  return job_list

if __name__ == '__main__':
    module_args = dkron_argument_spec()
    module_args.update(
        type=dict(type='str', choices=['all','status','leader','members','nodes','jobs'], default='all'),
        busy_only=dict(type='bool', required=False, default=False)
    )

    result = dict(
        changed=False,
        failed=False,
        ansible_module_results={}
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_together=dkron_required_together()
    )

    data = {}
    api = DkronAPIInterface(module)

    if module.params['type'] in ['all', 'status']:
      data['status'] = cluster_status(module, api)
      changed = True

    if module.params['type'] in ['all', 'leader']:
      data['leader'] = leader_node(module, api)
      changed = True

    if module.params['type'] in ['all', 'members', 'nodes']:
      data['members'] = member_nodes(module, api)
      changed = True

    if module.params['type'] in ['all', 'jobs']:
      data['jobs'] = job_list(module, api)
      changed = True

    if changed:
      result['ansible_module_results'] = data

    module.exit_json(**result)
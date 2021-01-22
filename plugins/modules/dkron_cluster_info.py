#!/usr/bin/env python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# Copyright: (c) 2920, Guy Knights <contact@guyknights.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: dkron_cluster_info
short_description: Gathers information about a Dkron cluster
description:
- Gathers information about a Dkron cluster.
options:
  endpoint:
    description:
      - The IP or hostname of a node in the cluster
    type: str
  port:
    description:
      - The port used to connect to the cluster node.
    type: int
    default: 8080
  username:
    description:
      - The username, if the cluster is protected by a reverse proxy with basic authentication.
    type: str
  password:
    description:
      - The password, if the cluster is protected by a reverse proxy with basic authentication.
    type: str
  use_ssl:
    description:
      - Use HTTPS to connect to the cluster node instead of HTTP.
    type: bool
  type:
    description:
      - Which information to return.
    type: str
    choices: [ all, status , leader , members , nodes , jobs ]
    default: all
  busy_only:
    description:
      - If set to true, only currently executing jobs will be returned in a returned jobs list
    type: bool
    default: False

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
from ansible_collections.knightsg.dkron.plugins.module_utils.dkron import DkronAPI

def run_module():
    module_args = dict(
        endpoint=dict(type='str', required=True),
        port=dict(type='int', required=False, default=8080),
        username=dict(type='str', required=False),
        password=dict(type='str', required=False, no_log=True),
        use_ssl=dict(type='bool', required=False, default=False),
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
        supports_check_mode=True
    )

    api = DkronAPI(module)

    data, changed = api.get_cluster_info()

    if data:
        result['ansible_module_results'] = data
    else:
        result['failed'] = True

    result['changed'] = changed
    
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
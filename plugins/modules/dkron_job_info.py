#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
    default: all (query all jobs)
    aliases:
      - name
  limit_history:
    description
      - Limit the history returned for each job to the amount specified by this parameter (eg. 5)
      - Will return full history for each job if omitted.
    type: int
    default: 0 (do not limit)
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
    names:
      - my_job_1
      - my_job_2
      - my_job_3

- name: Get config and history of last 10 executions for a specific job
  knightsg.dkron.dkron_job_info:
    endpoint: 192.168.1.1
    name: myjobname
    limit_history: 10

- name: Get config for all defined jobs but limit history to last execution only
  knightsg.dkron.dkron_job_info:
    endpoint: 192.168.1.1
    limit_history: 1

'''

RETURN = r'''
---
configuration:
  description: Job configuration as returned by the Dkron cluster API (https://dkron.io/api/).
  returned: always
  type: dict
  sample: {
    concurrency: "allow"
    dependent_jobs: null
    disabled: false
    displayname: ""
    error_count: 0
    executor: "shell"
    executor_config:
      command: "/bin/true"
    last_error: null
    last_success: "2020-11-14T17:32:15.010781048Z"
    metadata: null
    name: "job"
    next: "2020-11-14T17:33:15Z"
    owner: "john smith"
    owner_email: "johnsmith@example.com"
    parent_job: ""
    processors: {}
    retries: 0
    schedule: "@every 1m"
    status: "success"
    success_count: 185
    tags:
      server: "true:1"
    timezone: "UTC"
  }
  contains: see Dkron usage documentation for complete breakdown of returned values (https://dkron.io/usage/)
history:
  description: List of job executions with result status.
  returned: always
  type: list of dicts
  sample: [
    {
      attempt: 1
      finished_at: "2020-11-14T17:32:15.010781048Z"
      group: 1605375135000263778
      job_name: "myjobname"
      node_name: "myhostname"
      started_at: "2020-11-14T17:31:15.007570195Z"
      success: True
    },
    {
      attempt: 2
      finished_at: "2020-11-14T16:32:15.010781048Z"
      group: 1605375135000263778
      job_name: "myjobname"
      node_name: "myhostname"
      started_at: "2020-11-14T16:31:15.007570195Z"
      success: True
    }
  ]
'''

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.knightsg.dkron.plugins.module_utils.classes import (
    DkronClusterInterface,
    DkronRequestException,
    DkronEmptyResponseException
)
from ansible_collections.knightsg.dkron.plugins.module_utils.support import (
    dkron_argument_spec,
    dkron_required_together
)


def init_module():
    module_args = dkron_argument_spec()
    module_args.update(
        names=dict(type='list', required=False, aliases=['name']),
        limit_history=dict(type='int', required=False, default=0)
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
        required_together=dkron_required_together()
    )

    return module


def main():
    module = init_module()
    result = dict(
        changed=False,
        failed=False,
        jobs={}
    )

    jobs = []
    api = DkronClusterInterface(module)

    if module.params['names']:
        for name in module.params['names']:
            job_data = {}
            job_data['job_config'] = api.get_job_config(name)
            job_data['history'] = api.get_job_history(name)
            jobs.append(job_data)

    else:
        job_list = api.job_list()
        for job_name in job_list:
            job_data = {}
            job_data['job_config'] = api.get_job_config(job_name)
            job_data['history'] = api.get_job_history(job_name)
            jobs.append(job_data)

    result['jobs'] = jobs
    result['changed'] = True
    module.exit_json(**result)


if __name__ == '__main__':
    main()

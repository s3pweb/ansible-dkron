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
    descrption:
      - Use HTTPS to connect to the cluster node instead of HTTP.
    type: bool
  job_names:
    description:
      - Name (or list of names) of job to query.
      - Will query all jobs if omitted.
    type: list
    aliases:
      - job_name
  limit_history:
    description
      - Limit the history returned for each job to the amount specified by this parameter (eg. 5)
      - Will return full history for each job if omitted.
    type: int
author:
- Guy Knights (contact@guyknights.com)

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
        job_names=dict(type='list', required=False, aliases=['job_name']),
        limit_history=dict(type='int', required=False)
    )

    result = dict(
        changed=False,
        failed=False
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    api = DkronAPI(module)

    data, changed = api.get_job_info()

    if data:
        result['data'] = data
    else:
        result['failed'] = True

    result['changed'] = changed
    
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
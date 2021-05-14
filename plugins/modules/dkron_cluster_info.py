#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
      - 'nodes' and 'members' are aliases.
    type: str
    choices:
      - all
      - status
      - leader
      - members
      - nodes
      - jobs
    default: all
  active_only:
    description:
      - If set to true only currently executing jobs will be returned.
      - Has an effect only if type = 'jobs' (or 'all').
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

- name: Get only cluster member list (from SSL authenticated cluster)
  knightsg.dkron.dkron_cluster_info:
    endpoint: myclusterendpoint.com
    use_ssl: true
    username: myusername
    password: mypassword
    type: members

'''

RETURN = r'''
---
cluster_info:
  status:
    description: Cluster serf status.
    returned: success, if 'all' or 'status' are specified for 'type'
    type: dict
    sample: {}
    contains: see Dkron usage documentation for complete breakdown of returned values (https://dkron.io/usage/)
  leader:
    description: Cluster leader node.
    returned: success, if 'all' or 'leader' are specified for 'type'
    type: string
    sample: '172.16.1.1'
  members:
    description: Cluster member nodes.
    returned: success, if 'all' or 'members' (or 'nodes') are specified for 'type'
    type: list
    sample: ['172.16.1.1', '172.16.1.2', '172.16.1.3']
  jobs:
    description: Jobs configured in cluster.
    returned: success, if 'all' or 'jobs'are specified for 'type'
    type: list (of dicts)
    sample: [{}, {}, {}]
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

if __name__ == '__main__':
    module_args = dkron_argument_spec()
    module_args.update(
        type=dict(type='str', choices=['all', 'status', 'leader', 'members', 'nodes', 'jobs'], default='all'),
        active_only=dict(type='bool', required=False, default=False)
    )

    result = dict(
        changed=False,
        failed=False,
        cluster_info={}
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_together=dkron_required_together()
    )

    data = {}
    api = DkronClusterInterface(module)

    if module.params['type'] in ['all', 'status']:
        data['status'] = api.cluster_status()
        result['changed'] = True

    if module.params['type'] in ['all', 'leader']:
        data['leader'] = api.leader_node()
        result['changed'] = True

    if module.params['type'] in ['all', 'members', 'nodes']:
        data['members'] = api.member_nodes()
        result['changed'] = True

    if module.params['type'] in ['all', 'jobs']:
        data['jobs'] = api.job_list()
        result['changed'] = True

    if result['changed']:
        result['cluster_info'] = data

    module.exit_json(**result)

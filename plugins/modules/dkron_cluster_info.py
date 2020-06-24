#!/usr/bin/env python

# Copyright: (c) 2920, Guy Knights <contact@guyknights.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.dkron import Dkron

def run_module():
    module_args = dict(
        endpoint=dict(type='str', required=True),
        port=dict(type='str', required=False, default='8080'),
        username=dict(type='str', required=False),
        password=dict(type='str', required=False, no_log=True),
        use_ssl=dict(type='bool', required=False, default=False),
        type=dict(type='str', required=False, default='all')
    )

    result = dict(
        changed=False,
        failed=False,
        results={}
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    dkron = Dkron(module)

    rc, data, changed = dkron.cluster_info()

    module.exit_json(msg="success", result=data, changed=changed)

def main():
    run_module()

if __name__ == '__main__':
    main()
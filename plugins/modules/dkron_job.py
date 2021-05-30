#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

# Copyright: (c) 2020, Guy Knights <contact@guyknights.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r'''
---
module: dkron_job
short_description: Manage a Dkron job
description:
- Create, update or delete a Dkron job.
options:
  name:
    description:
      - Name of job to create, update or delete.
    type: string
    required: true
  displayname:
    description:
      - Alternate name of job that will be displayed.
    type: string
  schedule:
    description:
      - Job schedule in 'Dkron' cron format (https://dkron.io/usage/cron-spec/).
    type: string
    default: '@every 1m'
  timezone:
    description:
      - Timezone for job execution.
    type: string
    default: UTC
  owner:
    description:
      - Name of job owner.
    type: string
    default: ''
  owner_email:
    description:
      - Email of job owner.
    type: string
    default: ''
  disabled:
    description:
      - Whether to disable the job when it's created.
    type: bool
    default: false
  tags:
    description:
      - Tags to apply to the job (https://dkron.io/usage/target-nodes-spec/).
    type: dict
    default: {}
  metadata:
    description
      - Metadata to apply to job (https://dkron.io/usage/metatags/).
    type: dict
    default: {}
  retries:
    description:
      - Number of times the job should retry execution on failure.
    type: int
    default: 0
  parent_job:
    description:
      - Name of parent job that this job depends on.
    type: string
    default: ''
  run_on_create:
    description:
      - Run the job immediately after creation.
    type: bool
    default: false
  file_processor:
    description:
      - Dkron file processor configuration (https://dkron.io/usage/processors/file/).
    type: dict
    suboptions:
      log_dir:
        description:
          - Path to the location where the log files will be saved.
        type: string
      forward:
        description:
          - Forward log output to the next processor.
        type: bool
  log_processor:
    description:
      - Dkron log processor configuration (https://dkron.io/usage/processors/log/).
    type: dict
    suboptions:
      forward:
        description:
          - Forward the output to the next processor.
        type: bool
  syslog_processor:
    description:
      - Dkron syslog processor configuration (https://dkron.io/usage/processors/syslog/).
    type: dict
    suboptions:
      forward:
        description:
          - Forward the output to the next processor.
        type: bool
  concurrency:
    description:
      - Allow concurrent job executions.
    type: bool
    default: true
  shell_executor:
    description:
      - Dkron shell executor configuration (https://dkron.io/usage/executors/shell/).
      - Mutually exclusive with http_executor.
    type: dict
    suboptions:
      command:
        description:
          - Shell command to be run.
        type: string
        required: true
      env:
        description:
          - Variables to set in shell environment.
        type: dict
      cwd:
        description:
          - Working directory in which command will be executed.
        type: string
  http_executor:
    description:
      - Dkron HTTP executor configuration (https://dkron.io/usage/executors/http/).
      - Mutually exclusive with shell_executor.
    type: dict
    suboptions:
      method:
        description:
          - HTTP request method (in uppercase).
        type: string
        choices:
          - GET
          - POST
      url:
        description:
          - Request URL.
        type: string
      headers:
        description:
          - HTTP headers.
        type: dict
      body:
        description:
          - POST request body.
        type: string
      timeout:
        description:
          - Request timeout.
        type: int
      expect_code:
        description:
          - HTTP response code to expect.
        type: string
      expect_body:
        description:
          - Response body to expect (supports regexes).
        type: string
      debug:
        description:
          - Enable debug log output.
        type: bool
      tls_verify:
        description:
          - Disable verification of remote SSL cert (if cert required).
        type: bool
        default: true
      tls_cert:
        description:
          - Path to PEM file containing the client cert (if cert required).
        type: string
      tls_key:
        description:
          - Path to PEM file containing the client cert private key (if cert required).
        type: string
      tls_ca:
        description:
          - Path to PEM file containing certs to use as root CAs (if cert required)
        type: string
  overwrite:
    description:
      - Overwrite the job configuration if it already exists.
      - Will still report the job status as changed even if existing config matches new config.
      - If set to false, existing job config will be returned.
    type: bool
    default: true
  toggle:
    description:
      - If set to true and job with the same name exists, this will enable/disable the job.
      - If toggle is set the only other required parameter is name. All other parameters with values will be ignored.
    type: bool
    default: false
  state:
    description:
      - Whether to create/update the job ('present') or remove the job ('absent')
    type: str
    default: present
extends_documentation_fragment:
- knightsg.dkron.connect

seealso:
- module: knightsg.dkron.dkron_job_info
- module: knightsg.dkron.dkron_cluster_info

author:
- Guy Knights (contact@guyknights.com)
'''

EXAMPLES = r'''
- name: Create a basic shell executor job that runs on nodes with a specific tag set and retry value
  knightsg.dkron.dkron_job_info:
    endpoint: 192.168.1.1
    job_name: mytestjob1
    displayname: my_alt_job_name_1
    schedule: '0 */10 * * * *'
    timezone: UTC
    owner: 'John Smith'
    owner_email: jsmith@example.com
    tags:
      my_example_tag: somevalue
      my_defined_region: eu1
    retries: 3
    shell_executor
      command: '/bin/sh echo "Hello ${MY_FIRST_NAME} ${MY_LAST_NAME}!"'
      env: 'MYNAME=John,MY_LAST_NAME=Smith'
      cwd: '/home/jsmith'

'''

RETURN = r'''
---
configuration:
  description: Copy of job configuration (for reference).
  returned: when job is created or updated
  type: complex
  contains: see Dkron usage documentation for complete breakdown of returned values (https://dkron.io/usage/)
  sample: {
    "name": "mytestjob1",
    "displayname": "my_alt_job_name_1",
    "schedule": "0 */10 * * * *",
    "timezone"": "UTC",
    "owner": "John Smith"
  }
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
        name=dict(type='str', required=True),
        displayname=dict(type='str', required=False),
        schedule=dict(type='str', required=False, default='@every 1m'),
        timezone=dict(type='str', required=False, default='UTC'),
        owner=dict(type='str', required=False),
        owner_email=dict(type='str', required=False),
        disabled=dict(type='bool', required=False, default=False),
        tags=dict(type='dict', required=False),
        metadata=dict(type='dict', required=False),
        retries=dict(type='int', required=False, default=0),
        parent_job=dict(type='str', required=False),
        run_on_create=dict(type='bool', required=False, default=False),
        file_processor=dict(type='dict', required=False),
        log_processor=dict(type='dict', required=False),
        syslog_processor=dict(type='dict', required=False),
        concurrency=dict(type='bool', required=False, default=True),
        shell_executor=dict(type='dict', required=False),
        http_executor=dict(type='dict', required=False),
        overwrite=dict(type='bool', required=False, default=True),
        toggle=dict(type='bool', required=False, default=False),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent'])
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        required_together=dkron_required_together()
    )

    return module


def main():
    module = init_module()
    result = dict(
        changed=False,
        failed=False,
        job_config={}
    )
    
    api = DkronClusterInterface(module)

    if module.params['state'] == 'present':
        if not module.params['toggle']:
            if module.params['overwrite']:
                data, changed = api.upsert_job()
                result['job_config'] = data
                result['changed'] = changed
            else:
                existing_jobs = api.job_list()
                if module.params['name'] not in existing_jobs:
                    data, changed = api.upsert_job()
                    result['job_config'] = data
                    result['changed'] = changed
                else:
                    result['job_config'] = api.get_job_config(module.params['name'])
                    result['changed'] = False
        else:
            data, changed = api.toggle_job(job_name=module.params['name'])
            result['job_config'] = {'disabled': data}
            result['changed'] = changed

    else:
        data, changed = api.delete_job()
        result['ansible_module_results'] = data
        result['changed'] = changed

    module.exit_json(**result)


if __name__ == '__main__':
    main()

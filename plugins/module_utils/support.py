from __future__ import (absolute_import, division, print_function)

from ansible.module_utils.urls import url_argument_spec, fetch_url
import json

__metaclass__ = type


def dkron_argument_spec():
    argument_spec = url_argument_spec()

    del argument_spec['force']
    del argument_spec['force_basic_auth']
    del argument_spec['http_agent']

    # These params are common to all modules
    argument_spec.update(
        endpoint=dict(type='str', required=True),
        port=dict(type='int', required=False, default=8080),
        username=dict(type='str', required=False),
        password=dict(type='str', required=False, no_log=True),
        use_ssl=dict(type='bool', required=False, default=False)
    )

    return argument_spec


def dkron_required_together():
    return [['username', 'password']]

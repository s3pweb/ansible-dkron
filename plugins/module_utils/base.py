# -*- coding: utf-8 -*-
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright: (c) 2019, Rémi REY (@rrey)

from __future__ import (absolute_import, division, print_function)
from ansible.module_utils.urls import url_argument_spec

__metaclass__ = type

def dkron_argument_spec():
	argument_spec = url_argument_spec()

	del argument_spec['force']
    del argument_spec['force_basic_auth']
    del argument_spec['http_agent']

	argument_spect.update(
		endpoint=dict(type='str', required=True),
		port=dict(type='int', required=False, default=8080),
		username=dict(type='str', required=False),
        password=dict(type='str', required=False, no_log=True),
        use_ssl=dict(type='bool', required=False, default=False)
	)

	return argument_spec

def dkron_required_together():
	return [['username', 'password']]


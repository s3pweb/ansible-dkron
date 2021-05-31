# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Guy Knights
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r'''options:
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
        '''

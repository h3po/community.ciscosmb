#
# (c) 2017 Red Hat Inc.
#
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
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
author: Egor Zaitsev (@heuels)
cliconf: ciscosmb
short_description: Use ciscosmb cliconf to run command on Cisco SMB network devices.
description:
  - This ciscosmb plugin provides low level abstraction apis for
    sending and receiving CLI commands from Cisco SMB network devices.
'''

import re
import json

from ansible.module_utils._text import to_text
from ansible.plugins.cliconf import CliconfBase, enable_mode


class Cliconf(CliconfBase):

    def get_device_info(self):
        device_info = {}
        device_info['network_os'] = 'ciscosmb'

        resource = self.get('show verison')
        data = to_text(resource, errors='surrogate_or_strict').strip()
        match = re.search(r'SW version  +(\S+) \(.*$', data)
        if match:
            device_info['network_os_version'] = match.group(1)

        model = self.get('show inventory')
        data = to_text(model, errors='surrogate_or_strict').strip()
        match = re.search(r'PID: (.+)$', data, re.M)
        if match:
            device_info['network_os_model'] = match.group(1)

        identity = self.get('show system')
        data = to_text(identity, errors='surrogate_or_strict').strip()
        match = re.search(r'System Name: +(\S+)', data, re.M)
        if match:
            device_info['network_os_hostname'] = match.group(1)

        return device_info

    @enable_mode
    def get_config(self, source='running', format=None, flags=None):
        if source not in ("running", "startup"):
            raise ValueError(
                "fetching configuration from %s is not supported" % source
            )

        if format:
            raise ValueError(
                "'format' value %s is not supported for get_config" % format
            )

        if flags:
            raise ValueError(
                "'flags' value %s is not supported for get_config" % flags
            )

        if source == "running":
            cmd = "show running-config "
        else:
            cmd = "show startup-config "

        return self.send_command(cmd)

    def edit_config(self, command):
        return

    def get(self, command, prompt=None, answer=None, sendonly=False, newline=True, check_all=False):
        return self.send_command(command=command, prompt=prompt, answer=answer, sendonly=sendonly, newline=newline, check_all=check_all)

    def get_capabilities(self):
        result = super().get_capabilities()
        return json.dumps(result)

"""
Purpose: Intended for allowing import of the scripting wrapper automatically on Jupyter notebooks

Copyright (c) Plaxis bv. All rights reserved.

Unless explicitly acquired and licensed from Licensor under another
license, the contents of this file are subject to the Plaxis Public
License ("PPL") Version 1.0, or subsequent versions as allowed by the PPL,
and You may not copy or use this file in either source code or executable
form, except in compliance with the terms and conditions of the PPL.

All software distributed under the PPL is provided strictly on an "AS
IS" basis, WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESS OR IMPLIED, AND
LICENSOR HEREBY DISCLAIMS ALL SUCH WARRANTIES, INCLUDING WITHOUT
LIMITATION, ANY WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
PURPOSE, QUIET ENJOYMENT, OR NON-INFRINGEMENT. See the PPL for specific
language governing rights and limitations under the PPL.
"""

import os
from ipykernel.ipkernel import IPythonKernel
from ipykernel.comm import CommManager
from plxscripting.easy import *

ENV_VAR_IS_OUTPUT = 'IS_OUTPUT'
ENV_VAR_PLAXIS_SERVER_ADDRESS = 'PLAXIS_SERVER_ADDRESS'
ENV_VAR_PLAXIS_SERVER_PORT = 'PLAXIS_SERVER_PORT'
ENV_VAR_PLAXIS_SERVER_PASSWORD = 'PLAXIS_SERVER_PASSWORD'


class PlaxisIPythonKernel(IPythonKernel):
    banner = "IPythonKernel used to interact with PLAXIS"

    def __init__(self, **kwargs):
        super(IPythonKernel, self).__init__(**kwargs)

        # Initialize the InteractiveShell subclass
        self.user_ns = self.get_user_ns()
        self.shell = self.shell_class.instance(parent=self,
            profile_dir = self.profile_dir,
            user_module = self.user_module,
            user_ns     = self.user_ns,
            kernel      = self,
        )
        self.shell.displayhook.session = self.session
        self.shell.displayhook.pub_socket = self.iopub_socket
        self.shell.displayhook.topic = self._topic('execute_result')
        self.shell.display_pub.session = self.session
        self.shell.display_pub.pub_socket = self.iopub_socket

        self.comm_manager = CommManager(parent=self, kernel=self)

        self.shell.configurables.append(self.comm_manager)
        comm_msg_types = ['comm_open', 'comm_msg', 'comm_close']
        for msg_type in comm_msg_types:
            self.shell_handlers[msg_type] = getattr(self.comm_manager, msg_type)

    def get_user_ns(self):
        is_output = os.environ.get(ENV_VAR_IS_OUTPUT, '').title() == 'True'
        address = os.environ.get(ENV_VAR_PLAXIS_SERVER_ADDRESS, 'localhost')
        password = os.environ.get(ENV_VAR_PLAXIS_SERVER_PASSWORD, '')
        port = os.environ.get(ENV_VAR_PLAXIS_SERVER_PORT, 10000 if is_output else 10001)

        server_object_name = "s_o" if is_output else "s_i"
        global_object_name = "g_o" if is_output else "g_i"

        s, g = new_server(address, port, password=password)
        namespace = {
            server_object_name: s,
            global_object_name: g,
            'get_equivalent': get_equivalent,
            'ge': ge
        }

        return namespace


def main():
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=PlaxisIPythonKernel)


if __name__ == '__main__':
    main()

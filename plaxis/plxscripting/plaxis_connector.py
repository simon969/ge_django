"""
Purpose: PlaxisConnector provides methods to start PLAXIS 2D or PLAXIS 3D and make the plxscripting server
ready to be used

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
import socket
import string
import random
import time
import psutil
import winreg as wr
from contextlib import closing
import subprocess as sp
from .const import (PLAXIS_2D, PLAXIS_3D, PLAXIS_PATH, PLAXIS_BASE_REGEDIT_PATH, PLAXIS_2D_INPUT_EXECUTABLE_FILENAME,
                    PLAXIS_CLASSIC_2D_INPUT_EXECUTABLE_FILENAME, PLAXIS_3D_INPUT_EXECUTABLE_FILENAME,
                    PLAXIS_3D_OUTPUT_EXECUTABLE_FILENAME, PLAXIS_2D_OUTPUT_EXECUTABLE_FILENAME)
from .easy import new_server

# This is needed to prevent the OSError: [WinError 6] The handle is invalid
sp._cleanup = lambda *args, **kwargs: None


def get_free_port():
    """
    Searches for a free port that can be used on localhost
    :return int: The port number
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def generate_random_key(length=20):
    """
    Generates a random string using upper and lower case letter or numbers
    :param int length: The length of the string to generate
    :return string: A random generated string
    """
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def retrieve_installed_plaxis_software():
    """
    Retrieves a dictionary with all the PLAXIS applications that are installed in the machine and the path where
    its located
    :return: dict
    """
    installed_plaxis_dict = dict()
    for plaxis_app in PLAXIS_2D, PLAXIS_3D:
        connector = PlaxisConnector(plx_server_name=plaxis_app)
        plaxis_app_path = connector.get_plaxis_path_from_registry()
        if plaxis_app_path:
            installed_plaxis_dict[plaxis_app] = {PLAXIS_PATH: plaxis_app_path}
    return installed_plaxis_dict


def _retrieve_registry_path(plaxis_reg_path):
    try:
        with wr.OpenKey(wr.HKEY_LOCAL_MACHINE, plaxis_reg_path, 0) as rk:
            return wr.QueryValueEx(rk, 'Path')[0]
    except EnvironmentError:
        pass


class PlaxisConnectorException(Exception):
    """Base class for exceptions raised due to errors while using the PlaxisConnector"""
    pass


class TimeoutPlaxisConnectorException(PlaxisConnectorException):
    """Exception raised since call to PLAXIS timed out"""
    pass


class OtherPlaxisInstanceConnectorException(PlaxisConnectorException):
    """Exceptions raised when there is another instance of PLAXIS already open"""
    pass


class PlaxisConnector(object):
    """
    This class is used to start PLAXIS input application and make the plxscripting server available to be used by
    clients
    """
    PASSWORD_SIZE = 20

    def __init__(self, plx_path=None, timeout=60.0, plx_server_name=PLAXIS_3D, extra_args=None, is_input=True,
                 password=None):
        """
        :param str plx_path: Path of the PLAXIS application to open (if it's not provided than it will try to find
        one trough the registry
        :param float timeout: Number of seconds that it will wait for the plxscripting server to be ready before
        raising a TimeoutPlaxisConnectorException
        :param str plx_server_name: The name of the PLAXIS server name ('PLAXIS 2D' or 'PLAXIS 3D')
        :param list extra_args: List of extra arguments that will be passed when starting the PLAXIS application
        :param bool is_input: True will open Input. False will open Output
        :param str password: sets password to communicate with the PLAXIS server
        """
        self.plx_server_name = plx_server_name
        self.is_input = is_input
        self.plx_path = self.get_plaxis_path_from_registry() if plx_path is None else plx_path
        self._timeout = timeout
        self.filename = None
        self.process = None
        self.port = None
        self.password = password
        self.server = None
        self.plx_global = None
        self.extra_args = extra_args

    def __enter__(self):
        self.enter()
        return self

    def __exit__(self, *args):
        self.exit()

    def enter(self):
        self.port = get_free_port()
        if self.password is None:
            self.password = generate_random_key(self.PASSWORD_SIZE)
        self.process, self.server, self.plx_global = self._open_server()

    def exit(self):
        self.terminate_process_and_child_processes()

    def _get_plx_executable_path(self):
        if not self.plx_path:
            return
        for executable in self._get_server_executables():
            plx_exe_path = os.path.join(self.plx_path, executable)
            if os.path.isfile(plx_exe_path):
                return plx_exe_path

    def _open_server(self):
        plx_exe_path = self._get_plx_executable_path()
        if not plx_exe_path:
            raise PlaxisConnectorException('Did not find {}'.format(self.plx_server_name))
        if self.is_input:  # User can have only one Input instance opened at once
            self._check_no_other_plaxis_is_running()
        try:
            args = [plx_exe_path, '--AppServerPort={}'.format(self.port),
                    '--AppServerPassword={}'.format(self.password)]
            if self.extra_args:
                args.extend(self.extra_args)
            process = sp.Popen(args, stdin=sp.DEVNULL, shell=True)
        except FileNotFoundError:
            raise PlaxisConnectorException('Did not find {}'.format(plx_exe_path))
        server, plx_global = new_server('localhost', self.port, password=self.password)
        self._wait_for_server(server)
        return process, server, plx_global

    def _wait_for_server(self, server):
        """If PLAXIS is not ready try again until timeout is exceeded or PLAXIS becomes ready"""
        start_time = time.clock()
        while time.clock() < start_time + self._timeout:
            if self._get_plaxis_pid() is None:
                raise PlaxisConnectorException('Did not find a running PLAXIS application')
            elif server.active:
                return
            else:
                time.sleep(0.1)
        self.terminate_process_and_child_processes()
        raise TimeoutPlaxisConnectorException('Timeout exceeded when trying to connect to PLAXIS server')

    def get_plaxis_path_from_registry(self):
        server_executables = self._get_server_executables(force_input=True)
        for executable in server_executables:
            plaxis_reg_path = PLAXIS_BASE_REGEDIT_PATH + '{}'
            plaxis_reg_path = plaxis_reg_path.format(executable)
            path_found = _retrieve_registry_path(plaxis_reg_path)
            if path_found:
                return path_found

    def terminate_process_and_child_processes(self):
        """A Windows OS specific approach"""
        startupinfo = sp.STARTUPINFO()
        startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW
        pid = self._get_plaxis_pid()
        command = ['TASKKILL', '/F', '/T', '/PID', str(pid)]
        sp.Popen(command, startupinfo=startupinfo)
        while self.is_plaxis_running():
            time.sleep(0.2)

    def is_plaxis_running(self):
        return self._get_plaxis_pid() is not False

    def _get_plaxis_pid(self):
        for proc in psutil.process_iter():
            if proc.name().lower() in self._get_server_executables():
                return proc.pid
        return False

    def _check_no_other_plaxis_is_running(self):
        if self.is_plaxis_running():
            raise OtherPlaxisInstanceConnectorException('PLAXIS 3D is already running')

    def _get_server_executables(self, force_input=False):
        mapping = {
            (PLAXIS_3D, True): (PLAXIS_3D_INPUT_EXECUTABLE_FILENAME.lower(),),
            (PLAXIS_2D, True): (PLAXIS_2D_INPUT_EXECUTABLE_FILENAME.lower(),
                                PLAXIS_CLASSIC_2D_INPUT_EXECUTABLE_FILENAME.lower()),
            (PLAXIS_3D, False): (PLAXIS_3D_OUTPUT_EXECUTABLE_FILENAME.lower(),),
            (PLAXIS_2D, False): (PLAXIS_2D_OUTPUT_EXECUTABLE_FILENAME.lower(),),
        }
        return mapping.get((self.plx_server_name, force_input or self.is_input))

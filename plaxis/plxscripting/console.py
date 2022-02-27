"""
Purpose: Utilities for creating an interactive console

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

import sys
import code
from distutils.version import StrictVersion
from .const import ARG_APP_SERVER_ADDRESS, ARG_APP_SERVER_PORT, ARG_PASSWORD
from .server import new_server

try:
    _input = raw_input # Py < 3.0
except Exception:
    _input = input # Py >= 3.0


def get_IPython_module():
    try:
        import IPython
        if StrictVersion(IPython.__version__) >= StrictVersion('1.1.0'):
            return IPython
        else:
            return None
    except ImportError:
        return None


def get_jupyter_qt_console_module():
    try:
        import qtconsole
        return qtconsole
    except ImportError:
        return None


def print_splash(ipython):
    splash_lines = []
    splash_lines.append("\nPLAXIS Interactive Python Console")
    version = sys.version_info

    python_version_line = "Python {}.{}.{}".format(
        version.major, version.minor, version.micro)
    if ipython is not None:
        python_version_line += " - IPython {}".format(ipython.__version__)

    splash_lines.append(python_version_line)

    print('\n'.join(splash_lines))
    print('=' * max(len(line) for line in splash_lines))


def build_instructions(address, port, server_object_name, global_object_name):
    messages = []
    messages.append('Connected to {} on port {}'.format(address, port))
    messages.append('Available variables:')
    messages.append('    {}: the application server'.format(server_object_name))
    messages.append('    {}: the global environment'.format(global_object_name))

    messages.append('Example session:')
    if server_object_name == "s_i":
        messages.append('    >>> s_i.new()')
        messages.append('    >>> g_i.borehole(0) # for 3D: g_i.borehole(0, 0)')
        messages.append('    >>> g_i.soillayer(2)')
    else:
        messages.append('    >>> s_o.open(r"C:\\path\\to\\your\\project")')
        messages.append('    >>> result_type = g_o.ResultTypes.Soil.Utot')
        messages.append('    >>> results = g_o.getresults(g_o.Phases[-1], result_type, "node")')
        messages.append('    >>> max_result = g_o.filter(results, "max")')
        messages.append('    >>> g_o.echo(max_result)')

    messages.insert(0, '-' * max(len(m) for m in messages))
    messages.append(messages[0])
    return '\n'.join(messages)


def start_console(address, port, is_output, password):
    """Allows starting up an interactive console with a 'blank slate' namespace
    This is currently used in the 'Expert -> Python -> Interpreter' option in PLAXIS"""
    if not address:
        address = _input('Address (leave blank for localhost): ')

    if not address:
        address = 'localhost'

    while port <= 0:
        port = _input('Port number: ')
        try:
            port = int(port)
            if port < 0:
                raise Exception('')
        except Exception:
            print('Invalid port number: {}\n'.format(port))
            port = 0

    if password is None:
        password = _input('Password (leave blank for empty password): ')

    server_object_name = "s_o" if is_output else "s_i"
    global_object_name = "g_o" if is_output else "g_i"

    # Remove the other command line options as it would otherwise cause the terminal to print its usage.
    sys.argv = sys.argv[0:1]
    qtconsole = get_jupyter_qt_console_module()
    starting_message = build_instructions(address, port, server_object_name, global_object_name)
    if qtconsole is not None:
        from plxscripting.run_jupyter import set_environment_variables_with_plaxis_vars
        from qtconsole import qtconsoleapp
        set_environment_variables_with_plaxis_vars(address, port, is_output, password)
        # Print instructions before starting Jupyter QtConsole as it doesn't accept any starting message.
        print(starting_message)
        qtconsoleapp.JupyterQtConsoleApp.launch_instance(kernel_name="plaxis_python3")
    else:
        s, g = new_server(address, port, password=password)
        namespace = {
            ARG_APP_SERVER_ADDRESS: address,
            ARG_APP_SERVER_PORT: port,
            ARG_PASSWORD: password,
            server_object_name: s,
            global_object_name: g,
            'get_equivalent': get_equivalent,
            'ge': ge
        }

        open_ipython_or_interactive_console(namespace, starting_message)


def open_ipython_or_interactive_console(namespace, pre_banner=''):
    ipython = get_IPython_module()
    if ipython is not None:
        print_splash(ipython)
        # Print pre_banner before starting IPython as it doesn't accept any starting message.
        print(pre_banner)
        ipython.start_ipython(user_ns=namespace, display_banner=False)
    else:
        ic = code.InteractiveConsole(namespace)
        try:
            ic.interact(pre_banner)
        except SystemExit:
            print('Terminated')


def inplace_console():
    """Using either IPython or the Python console itself, Jupyter QtConsole doesn't allow passing namespaces
    This is to be used inline while using the SciTE editor included with PLAXIS"""
    invoking_module_namespace = sys._getframe(1).f_locals
    open_ipython_or_interactive_console(invoking_module_namespace)


def get_equivalent(object, envi=None):
    """
    Returns the equivalent staged construction object if provided with a geometry
    object or vice versa.

    Can also be used to get objects from a different environment
    (i.e. Input and Output) by providing the second argument.

    Examples:
        # The '_g' suffix indicates that this object is from geometry mode
        plate_g = g_i.Plate_1 # Plate created in geometry mode
        # Switch to staged construction before this line
        plate_s = get_equivalent(plate_g)

        phase_1_output = get_equivalent(g_i.Phase_1, g_o)
    """
    if envi is None:
        return object.get_equivalent()
    else:
        return envi.get_equivalent(object)


ge = get_equivalent

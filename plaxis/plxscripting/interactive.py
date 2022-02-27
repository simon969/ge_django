"""
Purpose: Intended for quickly starting an interactive Python session
    with import of the scripting wrapper. Usage:

	python interactive.py
	python "c:\Program Files (x86)\Plaxis\PLAXIS 3D\plxscripting\interactive.py"

Subversion data:
    $Id: interactive.py 16030 2014-03-31 09:21:45Z ac $
    $URL: https://tools.plaxis.com/svn/sharelib/trunk/PlxObjectLayer/Server/plxscripting/interactive.py $

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

import os.path
import sys
import imp
import argparse

paths = []
defpath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
if defpath:
    paths.append(defpath)

if len(sys.argv) > 1:
    paths.append(sys.argv[1])

found_module = imp.find_module('plxscripting', paths)
plxscripting = imp.load_module('plxscripting', *found_module)
from plxscripting.const import ARG_APP_SERVER_ADDRESS, ARG_APP_SERVER_PORT, ARG_PASSWORD
from plxscripting.console import start_console


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('--{}'.format(ARG_APP_SERVER_ADDRESS), type=str, default='',
                        help='The address of the server to connect to.')
    parser.add_argument('--{}'.format(ARG_APP_SERVER_PORT), type=int, default=0,
                        help='The port of the server to connect to.')
    parser.add_argument('--isoutput', action='store_true',
                        help='Use to indicate this script is being run from PLAXIS Output.')
    parser.add_argument('--{}'.format(ARG_PASSWORD), type=str, default=None,
                        help='The password that will be used to secure the communication.')
    return parser


def parse_args():
    parser = create_parser()
    args = vars(parser.parse_args())
    return args[ARG_APP_SERVER_ADDRESS], args[ARG_APP_SERVER_PORT], args['isoutput'], args[ARG_PASSWORD]


if __name__ == '__main__':
    address, port, is_output, password = parse_args()
    start_console(address, port, is_output, password)

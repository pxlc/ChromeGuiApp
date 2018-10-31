# -------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2018 pxlc@github
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -------------------------------------------------------------------------------

import os
import sys
import ctypes
import subprocess

import maya.cmds as mc

CHROMEGUI_ROOT = os.path.sep.join( os.path.realpath(__file__).replace('\\','/').split('/')[:-2] )
MAYA_APP_RUNNER_SCRIPT = os.path.sep.join( [CHROMEGUI_ROOT, 'bin', 'run_maya_app_server.py'] )

sys.path.append(CHROMEGUI_ROOT)
import chromegui


def launch_pychrome_maya_gui(app_module_path, start_html_file, config_filepath=None):

    MAYA_PORT = chromegui.get_next_port_num( load_config_file(config_filepath) )

    maya_port_name = ':%s' % MAYA_PORT
    if maya_port_name not in mc.commandPort(listPorts=True, q=True):
        mc.commandPort(name=maya_port_name, bufferSize=4096)  # default buffer size is 4096

    if sys.platform == 'win32':
        SEM_NOGPFAULTERRORBOX = 0x0002 # From MSDN
        ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX);
        CREATE_NO_WINDOW = 0x08000000 # From Windows API
        subprocess_flags = CREATE_NO_WINDOW
    else:
        subprocess_flags = 0
            
    cmd_and_args = ['C:/Program Files/Python27/python.exe', MAYA_APP_RUNNER_SCRIPT, app_module_path,
                    start_html_file, str(MAYA_PORT)]
    DEBUG = True
    if DEBUG:
        subprocess.Popen(cmd_and_args)
    else:
        subprocess.Popen(cmd_and_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         creationflags=subprocess_flags)


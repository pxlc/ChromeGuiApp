# -------------------------------------------------------------------------------
# MIT License
#
# Copyright (c) 2018 pxlc
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
import json
import logging
import traceback


def usage():

    print('')
    print('  Usage: python {0} <app_module_path> <maya_port_num>'.format(sys.argv[0]))
    print('')


if __name__ == '__main__':

    try:
        args = sys.argv[1:]
        if len(args) != 2:
            print('')
            print('*** ERROR: expecting 2 arguments ...')
            usage()
            sys.exit(1)

        app_module_filepath = os.path.realpath(args[0])
        app_module_name = os.path.basename(app_module_filepath).replace('.py', '')
        app_dir_path = os.path.dirname(app_module_filepath)

        MAYA_PORT = int(args[1])

        sys.path.append(app_dir_path)
        import_stmt = 'import {0} as app_module'.format(app_module_name)
        exec(import_stmt)

        app = app_module.MayaChromeGuiApp(MAYA_PORT, app_module_filepath, width=800, height=600)
        app.launch()

    except:
        open('C:/TEMP/maya_test_err.txt', 'w').write(traceback.format_exc())



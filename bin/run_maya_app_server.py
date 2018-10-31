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
import json
import logging
import traceback


def usage():

    print('')
    print('  Usage: python {0} <app_module_path> <start_html_filename> <port_num> <maya_port_num>'.format(
            sys.argv[0]))
    print('')


if __name__ == '__main__':

    try:
        args = sys.argv[1:]
        if len(args) != 4:
            print('')
            print('*** ERROR: expecting 4 arguments ...')
            usage()
            sys.exit(1)

        app_module_name = os.path.basename(args[0]).replace('.py','')
        app_dir_path = os.path.dirname(os.path.realpath(args[0])).replace('\\', '/')

        start_html_filename = args[1]
        PORT = int(args[2])
        MAYA_PORT = int(args[3])

        cap_words = [ w.capitalize() for w in app_module_name.replace('_app.py','').replace('.py','').split('_') ]
        app_code = ''.join(cap_words)
        default_app_title = ' '.join(cap_words)

        sys.path.append(app_dir_path)
        import_stmt = 'import {0} as app_module'.format(app_module_name)
        exec(import_stmt)

        app = app_module.MayaChromeGuiApp(PORT, MAYA_PORT, app_code, '{0} - Chrome App'.format(default_app_title),
                                          app_dir_path, start_html_filename, width=800, height=600)

        app.launch()

    except:
        open('A:/maquino/maya_test_err.txt', 'w').write(traceback.format_exc())



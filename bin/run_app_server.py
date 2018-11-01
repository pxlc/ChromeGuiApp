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
import getopt


def usage():

    print('')
    print('  Usage: python {} [OPTIONS] <app_module_path> <start_html_filename>'.format( sys.argv[0]))
    print('')
    print('     -h | --help ... print this usage message')
    print('     -s | --shell-logging ... log messages to shell console as well')
    print('     -l <LOGLEVEL> | --log-level <LOGLEVEL> ... "DEBUG", "INFO", "WARNING", "ERROR", or "CRITICAL"')
    print('     -c <CONFIGFILE> | --config-file <CONFIGFILE> ... /Not Implemented Yet/')
    print('')


if __name__ == '__main__':

    short_opt_str = 'hsl:c:'
    long_opt_list = ['help', 'shell-logging', 'log-level=', 'config-file=']

    try:
        opt_list, arg_list = getopt.getopt(sys.argv[1:], short_opt_str, long_opt_list)
    except getopt.GetoptError as err:
        print('')
        print(str(err))
        usage()
        sys.exit(2)

    shell_logging = False
    log_level_str = 'ERROR'
    config_filepath = ''

    for opt_flag, opt_value in opt_list:
        if opt_flag in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif opt_flag in ('-s', '--shell-logging'):
            shell_logging = True
        elif opt_flag in ('-l', '--log-level'):
            log_level_str = opt_value
        elif opt_flag in ('-c', '--config-file'):
            config_filepath = opt_value

    if len(arg_list) != 2:
        print('')
        print('*** ERROR: expecting 2 arguments ...')
        usage()
        sys.exit(3)

    app_module_name = os.path.basename(arg_list[0]).replace('.py','')
    app_dir_path = os.path.dirname(os.path.realpath(arg_list[0])).replace('\\', '/')

    start_html_filename = arg_list[1]

    cap_words = [ w.capitalize() for w in app_module_name.replace('_app.py','').replace('.py','').split('_') ]
    app_code = ''.join(cap_words)
    default_app_title = ' '.join(cap_words)

    sys.path.append(app_dir_path)
    import_stmt = 'import {0} as app_module'.format(app_module_name)
    exec(import_stmt)

    app = app_module.ChromeGuiApp(app_code, '{0} - Chrome App'.format(default_app_title), app_dir_path,
                                  start_html_filename, width=800, height=600, config_filepath=config_filepath,
                                  log_to_shell=shell_logging, log_level_str=log_level_str)
    app.launch()


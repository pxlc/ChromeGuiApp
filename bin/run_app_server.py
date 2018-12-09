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
    print('  Usage: python {} [OPTIONS] <app_module_path> [ <start_html_filename> ]'.format( sys.argv[0]))
    print('')
    print('     -h | --help ... print this usage message')
    print('     -s | --shell-logging ... log messages to shell console as well')
    print('     -l <LOGLEVEL> | --log-level <LOGLEVEL> ... "DEBUG", "INFO", "WARNING", "ERROR", or "CRITICAL"')
    print('     -c <CONFIGFILE> | --config-file <CONFIGFILE> ... full path to config file to use')
    print('     -t <TEMPLATEDIR> | --template-dir <TEMPLATEDIR> ... full path to template directory')
    print('     -x <WIN_X_WIDTH> | --x-width <WIN_X_WIDTH> ... specify window x-width')
    print('     -y <WIN_Y_HEIGHT> | --y-height <WIN_Y_HEIGHT> ... specify window y-height')
    print('')


if __name__ == '__main__':

    short_opt_str = 'hsl:c:t:x:y:'
    long_opt_list = ['help', 'shell-logging', 'log-level=', 'config-file=', 'template-dir=',
                     'x-width=', 'y-height=']

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
    template_dirpath = ''

    x_width = 600
    y_height = 600

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
        elif opt_flag in ('-t', '--template-dir'):
            template_dirpath = opt_value
        elif opt_flag in ('-x', '--x-width'):
            x_width = int(opt_value)
        elif opt_flag in ('-y', '--y-height'):
            y_height = int(opt_value)

    if len(arg_list) < 1:
        print('')
        print('*** ERROR: expecting at least 1 argument ...')
        usage()
        sys.exit(3)

    app_module_path = os.path.realpath(arg_list[0])

    app_module_name = os.path.basename(app_module_path).replace('.py','')
    app_dir_path = os.path.dirname(app_module_path).replace('\\', '/')

    start_html_filename = ''
    if len(arg_list) > 1:
        start_html_filename = arg_list[1]

    sys.path.append(app_dir_path)
    import_stmt = 'import {0} as app_module'.format(app_module_name)
    exec(import_stmt)

    app = app_module.ChromeGuiApp(app_module_path, width=x_width, height=y_height,
                                  start_html_filename=start_html_filename, template_dirpath=template_dirpath,
                                  config_filepath=config_filepath, log_to_shell=shell_logging,
                                  log_level_str=log_level_str)
    app.launch()


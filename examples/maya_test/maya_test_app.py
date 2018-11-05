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

import jinja2

os.environ['PXLC_CHROMEGUI_ROOT'] = os.path.sep.join(os.path.realpath(__file__).replace('\\','/').split('/')[:-3])

CHROMEGUI_ROOT = os.getenv('PXLC_CHROMEGUI_ROOT')

sys.path.append(CHROMEGUI_ROOT)
import chromegui


class MayaChromeGuiApp(chromegui.MayaChromeGuiAppBase):

    def __init__(self, maya_port, app_module_path, width=480, height=600, start_html_filename='',
                 template_dirpath='', config_filepath='', log_to_shell=False, log_level_str=''):

        super(MayaChromeGuiApp, self).__init__(maya_port, app_module_path, width=width, height=height,
                                               template_dirpath=template_dirpath, config_filepath=config_filepath,
                                               log_to_shell=log_to_shell, log_level_str=log_level_str)

        self.start_html_fname = start_html_filename if start_html_filename else self.auto_template_filename()

        # Set up your app data (and anything you will use for template data) here.

        self.extra_template_vars = self._setup_extra_template_vars()
        self._setup_callbacks()

    def _setup_extra_template_vars(self):

        res_image_path = os.path.realpath( os.path.join(CHROMEGUI_ROOT, 'res', 'images') )
        res_icon_path = os.path.realpath( os.path.join(CHROMEGUI_ROOT, 'res', 'icons') )

        extra_vars = {
            'RES_IMG_PATH': res_image_path.replace('\\', '/'),
            'RES_ICON_PATH': res_icon_path.replace('\\', '/'),
        }
        return extra_vars

    def _setup_callbacks(self):

        self.add_op_handler('print_message', self.print_message)
        self.add_op_handler('user_info_submit', self.user_info_submit)

    def launch(self):

        self.start_()

    # --------------------------------------------------------------------------------------------------------
    #  Callback function handlers
    # --------------------------------------------------------------------------------------------------------
    def print_message(self, op, op_data, c_app_runner):

        logging.info('')
        logging.info(':: got message "{0}"'.format(op_data.get('message','')))
        logging.info('')

    def user_info_submit(self, op, op_data, c_app_runner):

        logging.info('')
        logging.info(':: got submitted user info: {0}'.format(json.dumps(op_data, indent=2, sort_keys=True)))
        logging.info('')

        try:
            res = self.send_to_maya(os.path.join(self.get_app_dir_path(), 'maya_scripts', 'mtest.py'), 'test_one', data_filepath=None)

            logging.info('')
            logging.info(':: result from maya command: {0}'.format(res))
            logging.info('')

            open('A:/maquino/maya_test_log.txt', 'w').write('\n:: result from maya: {0}\n\n'.format(res))
        except:
            open('A:/maquino/maya_test_err.txt', 'w').write(traceback.format_exc())



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
import getpass
import logging
import datetime
import traceback
import subprocess

try:
    unicode
except:
    unicode = str

LAUNCHER_APP_ROOT = os.path.dirname(os.path.abspath(__file__)).replace('\\', '/')
os.environ['LAUNCHER_APP_ROOT'] = LAUNCHER_APP_ROOT

CHROMEGUI_ROOT = os.environ['PXLC_CHROMEGUI_ROOT']

sys.path.insert(0, CHROMEGUI_ROOT)

import chromegui  # NOTE: requires jinja2 package to be in Python environment

_BASE_SYS_PATH = sys.path[:]
_BASE_OS_ENVIRON = dict(os.environ.copy())


class ChromeGuiApp(chromegui.ChromeGuiAppBase):

    BTN_HTML_TEMPLATE = '''
<button class="btn btn-secondary tool_img_btn" onclick="launch_app('{APP}');" style="padding: 4px;"
        title="{LABEL}">
    <img class="tool_img highlight" src="file://{ICON_PATH}" />
</button>'''

    def __init__(self, app_module_path, width=600, height=240,
                 start_html_filename='', template_dirpath='', config_filepath='',
                 log_to_shell=False, log_level_str=''):

        if sys.platform == 'win32':
            user_app_temp_root = os.path.join(os.getenv('TEMP'), 'CHROMEAPPGUI_LAUNCHER_APP').replace('\\', '/')
        else:
            user_app_temp_root = os.path.join(os.getenv('HOME'), '.CHROMEAPPGUI_LAUNCHER_APP').replace('\\', '/')

        if not os.path.exists(user_app_temp_root):
            os.makedirs(user_app_temp_root)

        super(ChromeGuiApp, self).__init__(app_module_path, width=width, height=height,
                                           template_dirpath=template_dirpath, config_filepath=config_filepath,
                                           log_to_shell=log_to_shell, log_level_str=log_level_str,
                                           app_temp_root=user_app_temp_root)

        self.app_window_title = 'My Custom Launcher'

        self.user_app_temp_root = user_app_temp_root
        self.start_html_fname = start_html_filename if start_html_filename else self.auto_template_filename()

        self.launcher_config_d = {}

        # Set up your app data (and anything you will use for template data) here.

        self.extra_template_vars = self._setup_extra_template_vars()
        self._setup_callbacks()

    def _setup_extra_template_vars(self):

        user = getpass.getuser()

        extra_vars = {
            'LAUNCHER_APP_ROOT': LAUNCHER_APP_ROOT,
            'LOG_FILES_ROOT': self.user_app_temp_root,
            'USER_LOGIN': user,
            'WINDOW_TITLE': self.app_window_title,
        }
        return extra_vars


    def _setup_callbacks(self):

        self.add_op_handler('print_message', self.print_message)
        self.add_op_handler('launch_app', self.launch_app)
        self.add_op_handler('build_app_buttons', self.build_app_buttons)


    def launch(self):

        self.start_()


    # --------------------------------------------------------------------------------------------------------
    #  Callback function handlers
    # --------------------------------------------------------------------------------------------------------
    def print_message(self, op, op_data):

        self.info('')
        self.info(':: got message "{0}"'.format(op_data.get('message','')))
        self.info('')

    def _get_btn_info_exe_path(self, app_button_info):

        exe_path_value = app_button_info['exe_path'].get(sys.platform, None)

        if type(exe_path_value) is list:
            for exe_path in exe_path_value:
                if os.path.isfile(exe_path):
                    return exe_path
            return None

        elif type(exe_path_value) in (str, unicode):
            return exe_path_value if os.path.isfile(exe_path_value) else None

        else:
            return None

    def build_app_buttons(self, op, op_data):

        try:
            show_code = op_data.get('show_code', '')

            launcher_config_file = '%s/launcher_config.json' % LAUNCHER_APP_ROOT

            with open(launcher_config_file, 'r') as fp:
                self.launcher_config_d = json.load(fp)

            for app_button_info in self.launcher_config_d.get('app_buttons', []):

                exe_path = self._get_btn_info_exe_path(app_button_info)
                if not exe_path:
                    continue

                app_button_info['exe_path'] = exe_path
                icon_path = os.path.expandvars(app_button_info['icon_path'])
                btn_entry_html_str = self.BTN_HTML_TEMPLATE.format(
                                            LABEL=app_button_info['label'],
                                            ICON_PATH=icon_path,
                                            APP=app_button_info['app'])

                self.send_to_chrome('add_app_button', {'btn_entry_html': btn_entry_html_str})
        except:
            self.error('')
            self.error(traceback.format_exc())
            self.error('')

    def launch_app(self, op, op_data):

        try:
            self.info('')
            self.info(':: op_data is %s' % op_data)
            self.info('')

            app = op_data['app_name']
            show_code = op_data['show_code']

            found_app_button_info = {}

            for app_button_info in self.launcher_config_d.get('app_buttons', []):
                if app == app_button_info['app']:
                    found_app_button_info.update(app_button_info)
                    break

            if not found_app_button_info:
                raise Exception('No app button info found for app "%s"' % app)

            # TODO: Set show environment here using your studio's environment system using show_code

            # Then run the application
            cmd_and_args = [ found_app_button_info['exe_path'] ]

            if 'exe_args' in found_app_button_info:
                exe_args = []
                exe_args_value = found_app_button_info['exe_args']
                if type(exe_args_value) is dict:
                    exe_args = exe_args_value.get(sys.platform, None)
                    if type(exe_args) is None:
                        raise Exception('No arguments specified for platform "%s"' % sys.platform)
                elif type(exe_args_value) is list:
                    exe_args = exe_args_value
                else:
                    raise Exception('Only expecting either dict or list for "exe_args" key value.')

                cmd_and_args += [ os.path.expandvars(arg) for arg in exe_args ]

            cflags = 0
            if sys.platform == 'win32':
                # be sure to open subprocess in a new process group so closing launcher doesn't kill
                # subprocess
                cflags = subprocess.CREATE_NEW_PROCESS_GROUP
            else:
                # not sure if anything is needed on linux side to fork subprocess but do it here if so
                pass

            p = subprocess.Popen(cmd_and_args, creationflags=cflags)

            # Reset environment back to vanilla settings
            sys.path = _BASE_SYS_PATH[:]
            os.environ.clear()
            os.environ.update(_BASE_OS_ENVIRON)

        except:
            self.error('')
            self.error(traceback.format_exc())
            self.error('')



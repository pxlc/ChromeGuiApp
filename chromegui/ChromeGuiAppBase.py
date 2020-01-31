
import os
import sys
import json
import ctypes
import getpass
import subprocess
import traceback
import logging

import jinja2

from . import util
from .websocket import WebsocketServer
from .get_js import get_js_file_url
from .config import load_config_file
from .util import get_next_port_num

CHROMEGUI_ROOT = '/'.join(os.path.realpath(__file__).replace('\\','/').split('/')[:-2])


class ChromeGuiAppBase(object):

    JS_FILE_URL = get_js_file_url()

    def __init__(self, app_module_filepath, width=480, height=600, template_dirpath='',
                 config_filepath='', log_to_shell=False, log_level_str='', app_temp_root=''):

        self.app_temp_root = app_temp_root

        self.app_module_filepath = app_module_filepath.replace('\\','/')
        self.app_dir_path = os.path.dirname(self.app_module_filepath)
        self.app_module_filename = os.path.basename(self.app_module_filepath)

        cap_words = [ w.capitalize() for w in
                            self.app_module_filename.replace('_app.py','').replace('.py','').split('_') ]

        self.app_short_name = ''.join(cap_words)
        self.app_title_label = ' '.join(cap_words)  # default App Title

        self.config = load_config_file(config_filepath)

        self.user = getpass.getuser()

        # self.app_short_name = app_short_name
        # self.app_title_label = app_title_label
        # self.app_dir_path = app_dir_path

        tmpl_dir_path = template_dirpath if template_dirpath else self.app_dir_path
        self.j2_template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(tmpl_dir_path))

        self.port = get_next_port_num(self.config)

        self.session_start_dt_str = util.now_datetime_str('compact')
        self.session_id = '{a}_{u}_{dt}'.format(a=self.app_short_name, u=self.user, dt=self.session_start_dt_str)

        # use session_id as logger name
        if not self.app_temp_root:
            self.app_temp_root = self.config.get('user_temp_root', os.getenv('TEMP'))
        self.log_file = util.get_app_session_logfile(self.app_short_name, dt_str=self.session_start_dt_str,
                                                     temp_root=self.app_temp_root)
        # make sure log directory exists
        log_dirpath = os.path.dirname(self.log_file)
        if not os.path.isdir(log_dirpath):
            os.makedirs(log_dirpath)

        log_level_map = {
            'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'WARNING': logging.WARNING, 'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        log_level = logging.ERROR
        if log_level_str in log_level_map:
            log_level = log_level_map.get(log_level_str)

        self.logger = logging.getLogger('{a}{dt}'.format(a=self.app_short_name,
                                                         dt=self.session_start_dt_str.replace('_','')))
        self.logger.setLevel( log_level )
        util.setup_logger(self.logger, self.log_file, log_level, log_to_shell=log_to_shell)

        self.session_file_path_pre = self.log_file.replace('.log', '')
        self.session_temp_dir_path = os.path.dirname(self.log_file)

        if not os.path.isdir(self.session_temp_dir_path):
            os.makedirs(self.session_temp_dir_path)

        self.ws_server = WebsocketServer(self.port)

        self.ws_server.set_fn_new_client(self._ws_new_client)
        self.ws_server.set_fn_client_left(self._ws_client_left)
        self.ws_server.set_fn_message_received(self._ws_message_from_client)

        self.chrome_client = None

        self.session_data = {}
        self.op_handler_info = {} # {'op_name': {'cb_fn': fn}}
        self.default_op_handler_fn = None

        self.width = width
        self.height = height

        self.chrome_process = None

        self.start_html_fname = ''
        self.extra_template_vars = {}

    def auto_template_filename(self):

        return 'T_{0}.html'.format(self.app_module_filename.replace('_app.py','').replace('.py',''))

    def generate_html_file(self, template_filename):

        template = self.j2_template_env.get_template(template_filename)

        template_vars = {
            'CHROMEGUI_JS_URL': self.get_js_file_url(),
            'PORT': str(self.get_port_num()),
            'SESSION_ID': self.get_session_id(),
            'WIN_TITLE': self.get_app_title(),
            'APP_DIR_PATH': self.get_app_dir_path().replace('\\', '/'),
        }
        template_vars.update(self.extra_template_vars)

        html = template.render(template_vars)

        html_file_path = self.build_session_filepath('APP_START', '.html')
        with open(html_file_path, 'w') as html_fp:
            html_fp.write(html)

        return html_file_path

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def _ws_new_client(self, client, server):

        if not self.chrome_client:
            self.chrome_client = client
            msg_obj = {'op': 'connection_status', 'session_id': self.session_id, 'data': {'status': 'CONNECTED'}}
            self.ws_server.send_message(client, json.dumps(msg_obj))

    def clean_up(self):
        pass

    def _ws_client_left(self, client, server):

        if client == self.chrome_client:
            if self.chrome_process:
                self.chrome_process.kill()
            self.ws_server.shutdown()
            self.clean_up()

    def _ws_message_from_client(self, client, server, message):

        if client != self.chrome_client:
            return

        msg_data = {}
        try:
            msg_data = json.loads(message)
        except:
            # TODO: log warning/error message
            return
        op = msg_data.get('op')
        session_id = msg_data.get('session_id')
        op_data = msg_data.get('data', {})

        if not op or not session_id or not op_data:
            # TODO: log warning/error
            return
        if session_id != self.session_id:
            # TODO: log warning/error
            return

        # delegate operation and its data to handlers
        if op not in self.op_handler_info:
            if self.default_op_callback_fn:
                self.default_op_callback_fn(op, op_data)
            else:
                # TODO: log warning/error
                pass
            return

        fn = self.op_handler_info.get(op, {}).get('cb_fn')
        if fn:
            fn(op, op_data)

    def set_app_title(self, title):
        self.app_title_label = title

    def get_app_dir_path(self):
        return self.app_dir_path

    def get_app_short_name(self):
        return self.app_short_name

    def get_app_title(self):
        return self.app_title_label

    def get_port_num(self):
        return self.port

    def get_session_id(self):
        return self.session_id

    def get_log_filepath(self):
        return self.log_file

    def get_js_file_url(self):
        return self.JS_FILE_URL

    def build_session_filepath(self, file_suffix, file_ext):
        return '{pre}_{suf}{ext}'.format(pre=self.session_file_path_pre, suf=file_suffix, ext=file_ext)

    def add_op_handler(self, op, op_callback_fn):

        self.op_handler_info[op] = {'cb_fn': op_callback_fn}

    def set_default_op_handler(self, default_op_callback_fn):

        self.default_op_handler_fn = default_op_callback_fn

    def send_to_chrome(self, chrome_op, chrome_op_data):

        if not self.chrome_client:
            # TODO: log warning/error
            return
        msg_data = json.dumps({'op': chrome_op, 'session_id': self.session_id, 'data': chrome_op_data})
        self.ws_server.send_message(self.chrome_client, msg_data)

    def start_(self):

        try:
            chrome_path_by_platform = {
                'win32': r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            }
            chrome_exe_path = chrome_path_by_platform.get(sys.platform, '')

            chrome_data_dir = os.path.join(self.config.get('user_temp_root', os.getenv('TEMP')),
                                           '_chrome_app_user_data')
            cmd_arr = [
                chrome_exe_path,
                '--allow-file-access-from-files',
                '--window-size={w},{h}'.format(w=self.width, h=self.height),
                '--user-data-dir={0}'.format(chrome_data_dir),
                '--app=file:///{0}'.format(self.generate_html_file(self.start_html_fname)),
            ]

            if sys.platform == 'win32':
                SEM_NOGPFAULTERRORBOX = 0x0002 # From MSDN
                ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX);
                CREATE_NO_WINDOW = 0x08000000 # From Windows API
                subprocess_flags = CREATE_NO_WINDOW
            else:
                subprocess_flags = 0
                
            self.chrome_process = subprocess.Popen(cmd_arr, creationflags=subprocess_flags)
            self.ws_server.run_forever()
        except:
            self.error('')
            self.error(traceback.format_exc())
            self.error('')


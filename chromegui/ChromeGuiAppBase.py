
import os
import sys
import json
import ctypes
import getpass
import subprocess

from . import util
from .websocket import WebsocketServer
from .get_js import get_js_file_url
from .config import load_config_file
from .util import get_next_port_num

CHROMEGUI_ROOT = '/'.join(os.path.realpath(__file__).replace('\\','/').split('/')[:-2])


class ChromeGuiAppBase(object):

    JS_FILE_URL = get_js_file_url()

    def __init__(self, app_short_name, app_title_label, app_dir_path, width=480, height=600, config_filepath=None):

        self.config = load_config_file(config_filepath)

        self.user = getpass.getuser()
        self.app_short_name = app_short_name
        self.app_title_label = app_title_label
        self.app_dir_path = app_dir_path

        self.port = get_next_port_num(self.config)

        self.session_start_dt_str = util.now_datetime_str('compact')
        self.session_id = '{a}_{u}_{dt}'.format(a=self.app_short_name, u=self.user, dt=self.session_start_dt_str)

        self.log_file = util.get_app_session_logfile(app_short_name, folder_pre='_',
                                                     dt_str=self.session_start_dt_str[:-3],
                                                     temp_root=self.config.get('user_temp_root',os.getenv('TEMP')))

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

    def _ws_new_client(self, client, server):

        if not self.chrome_client:
            self.chrome_client = client
            msg_obj = {'op': 'message', 'session_id': self.session_id, 'data': {'msg': 'connection established'}}
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
                self.default_op_callback_fn(op, op_data, self)
            else:
                # TODO: log warning/error
                pass
            return

        fn = self.op_handler_info.get(op, {}).get('cb_fn')
        if fn:
            fn(op, op_data, self)

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

    def start_(self, html_file_path):

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
            '--app=file:///{0}'.format(html_file_path),
        ]

        if sys.platform == 'win32':
            SEM_NOGPFAULTERRORBOX = 0x0002 # From MSDN
            ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX);
            CREATE_NO_WINDOW = 0x08000000 # From Windows API
            subprocess_flags = CREATE_NO_WINDOW
        else:
            subprocess_flags = 0
            
        self.chrome_process = subprocess.Popen(cmd_arr, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                               creationflags=subprocess_flags)
        self.ws_server.run_forever()


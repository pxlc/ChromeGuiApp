
import os
import sys
import socket
import threading
import time
import cgi

CHROMEGUI_ROOT = '/'.join(os.path.realpath(__file__).replace('\\','/').split('/')[:-2])

sys.path.insert(0, '/'.join([ CHROMEGUI_ROOT, 'thirdparty', 'python' ]))
sys.path.insert(0, '/'.join([ CHROMEGUI_ROOT, 'dcc' ]))

import websocket

from .ChromeGuiAppBase import ChromeGuiAppBase
from . import util


def _on_message(ws, message):

    print('>>> on_message OK')

    msg_data = {}
    try:
        msg_data = json.loads(message)
    except:
        print('[NOT-JSON]: %s' % message)
        ws.maya_client.send('print("[NOT-JSON]: %s")' % cgi.escape(message))
        return

    if type(msg_data) is dict:

        if msg_data.get('op') == 'maya_python_cmd':
            print('>>> Sending Maya python cmd ...')
            ws.maya_socket.send(msg_data.get('cmd_str','print("??? NO python command provided")'))
            data = ws.maya_socket.recv(1024)
            print("[%s]" % data.strip())
            ws.send('maya_python_cmd:COMPLETED')

        elif msg_data.get('op') == 'maya_module_fn_run':
            data_filepath = '%s_MayaData_%s.json' % (self.session_file_path_pre, util.now_datetime_str('compact'))
            data_filepath = data_filepath.replace('\\', '/')

            op_data = msg_data.get('op_data', {})

            maya_python_cmd_str = ''

            if 'module_name' in op_data:
                maya_python_cmd_str = '''import hook; hook.run_fn("{mod}", "{fn}", "{dat}")'''.format(
                                        mod=op_data.get('module_name'), fn=op_data.get('fn_name'),
                                        dat=data_filepath)
            elif 'module_filepath' in op_data:
                maya_python_cmd_str = '''import hook; hook.run_fn_dynamic("{mod_fp}", "{fn}", "{dat}")'''.format(
                                        mod_fp=op_data.get('module_filepath'), fn=op_data.get('fn_name'),
                                        dat=data_filepath)
            if maya_python_cmd_str:
                with open(data_filepath, 'w') as fp:
                    fp.write(json.dumps(op_data, indent=2, sort_keys=True))
                ws.maya_socket.send(maya_python_cmd_str)
                data = ws.maya_socket.recv(1024)
                print("[%s]" % data.strip())
                result_data_str = ''
                with open(data_filepath, 'r') as fp:
                    result_data_str = fp.read()
                    # validate
                    try:
                        r_data = json.loads(result_data_str)
                    except:
                        r_data = {'status': 'ERROR', 'msg': traceback.format_exc()}
                        result_data_str = json.dumps(r_data)
                ws.send(result_data_str)

def _on_error(ws, error):
    print(error)

def _on_close(ws):
    print("### closed ###")

def _on_open(ws):
    print('')
    print(':: on_open() called')
    print('')


class MayaChromeGuiAppBase(ChromeGuiAppBase):

    def __init__(self, maya_port_num, app_module_path, width=480, height=600, start_html_filename='',
                 template_dirpath='', config_filepath='', log_to_shell=False, log_level_str=''):

        super(MayaChromeGuiAppBase, self).__init__(app_module_path, width=width, height=height,
                                                   template_dirpath=template_dirpath,
                                                   config_filepath=config_filepath,
                                                   log_to_shell=log_to_shell, log_level_str=log_level_str)
        self.maya_port_num = maya_port_num
        self.maya_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.maya_socket.connect(('127.0.0.1', self.maya_port_num))

        self.w_socket = None
        self.maya_client = None

    def post_ws_first_new_client(self, first_client, server):

        self.w_socket = websocket.WebSocketApp('ws://localhost:%s/' % self.port,
                                                on_message = _on_message,
                                                on_error = _on_error,
                                                on_close = _on_close)
        self.w_socket.on_open = _on_open
        self.w_socket.maya_socket = self.maya_socket

        threading.Thread(target=self._run_w_socket_forever).start()

    def handle_other_new_client(self, other_client, server):

        if not self.maya_client:
            self.maya_client = other_client

    def ws_message_from_client(self, client, server, message):

        if self.chrome_client and client == self.chrome_client:
            if message in ['maya_python_cmd:COMPLETED']:
                print('[Maya-Client]: %s' % message)
                return
            if message.startswith('[JS-ERROR]'):
                self.error(message)
                return
            #---DEBUG
            with open('C:/TEMP/__MayaTest_ERROR.txt', 'w') as fp:
                fp.write(message)
            #---DEBUG
            msg_data = {}
            try:
                msg_data = json.loads(message.encode('ASCII'))
            except:
                self.error("Message from Chrome not JSON format ... exception follows.")
                self.error(traceback.format_exc())
                return
            if msg_data.get('send_to_maya'):
                if self.maya_client is None:
                    self.error("Maya web-socket client not available yet.")
                    return
                self.ws_server.send_message(self.maya_client, message)
            else:
                return False

        elif self.maya_client and client == self.maya_client:
            msg_data = {}
            try:
                msg_data = json.loads(message.encode('ASCII'))
            except:
                self.error("Message from Chrome not JSON format ... exception follows.")
                self.error(traceback.format_exc())
                return
            if msg_data.get('send_to_chrome'):
                self.ws_server.send_message(self.chrome_client, message)
            else:
                return False

        return True

    def _run_w_socket_forever(self):

        self.w_socket.run_forever()

    def on_chrome_gui_closing(self):

        if self.maya_client:
            # attempt to close command port first?
            cmd_str = 'import maya.cmds as __mc; __mc.commandPort(name=":%s", close=True)' % self.maya_port_num
            msg_data = {
                'op': 'maya_python_cmd',
                'cmd_str': cmd_str,
            }
            self.ws_server.send_message(self.maya_client, json.dumps(msg_data))
            self.maya_client.get('handler').finish()



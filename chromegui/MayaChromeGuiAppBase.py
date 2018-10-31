
import os
import sys
import socket

from .ChromeGuiAppBase import ChromeGuiAppBase


# meant to be instantiated and run from within Maya session

class MayaChromeGuiAppBase(ChromeGuiAppBase):

    def __init__(self, maya_port_num, app_short_name, app_title_label, app_dir_path, width=480, height=600):

        super(MayaChromeGuiAppBase, self).__init__(app_short_name, app_title_label, app_dir_path, width, height)

        self.maya_port_num = maya_port_num
        self.maya_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.maya_client.connect(('127.0.0.1', self.maya_port_num))

    def send_to_maya(self, module_filepath, module_fn_name, data_filepath=None):

        module_dirpath = os.path.dirname(module_filepath).replace('\\', '/')
        module_name = os.path.basename(module_filepath).replace('.py', '')

        data_path_arg = ''
        if data_filepath:
            data_path_arg = "'{0}'".format(data_filepath('\\','/'))

        command = '''python("import sys; sys.path.append('{mod_dp}'); import {mod}; ''' \
                  '''{mod}.{mod_fn}({dat_p});");'''.format(mod_dp=module_dirpath, mod=module_name,
                                                           mod_fn=module_fn_name, dat_p=data_path_arg)
        self.maya_client.send(command)
        data_returned = self.maya_client.recv(1024)

        return data_returned

    def clean_up(self):

        # TODO: confirm that this code is running!

        self.send_to_maya(
            '''python("import maya.cmds as __mc; __mc.commandPort(name='{0}', close=True)");'''.format(
                ':%s' % self.maya_port_num))  # this doesn't seem to work to close the command port
        self.maya_client.close()



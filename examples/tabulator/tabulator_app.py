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
import logging
import jinja2

sys.path.append( os.path.sep.join(os.path.realpath(__file__).replace('\\','/').split('/')[:-3]) )
import chromegui


class ChromeGuiApp(chromegui.ChromeGuiAppBase):

    def __init__(self, port_num, app_short_name, app_title_label, app_dir_path, start_html_filename,
                 width=480, height=600):

        super(ChromeGuiApp, self).__init__(port_num, app_short_name, app_title_label, app_dir_path, width, height)

        self.start_html_fname = start_html_filename

        self.template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(self.get_app_dir_path()))

        logging.basicConfig(
            level=logging.DEBUG,
            # format="%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s",
            format="%(asctime)s [%(levelname)-5.5s]:  %(message)s",
            handlers=[
                logging.FileHandler(self.get_log_filepath()),
                logging.StreamHandler(sys.stdout)
            ])

        self._setup_callbacks()

    def _generate_html_file(self, template_filename):

        res_image_path = os.path.realpath( os.path.join( self.get_app_dir_path(), '../../res/images' ) )
        res_icon_path = os.path.realpath( os.path.join( self.get_app_dir_path(), '../../res/icons' ) )

        template = self.template_env.get_template(template_filename)
        html = template.render({
            'CHROMEGUI_JS_URL': self.get_js_file_url(),
            'PORT': str(self.get_port_num()),
            'SESSION_ID': self.get_session_id(),
            'WIN_TITLE': self.get_app_title(),
            'APP_DIR_PATH': self.get_app_dir_path().replace('\\', '/'),
            'RES_IMG_PATH': res_image_path.replace('\\', '/'),
            'RES_ICON_PATH': res_icon_path.replace('\\', '/'),
        })
        html_file_path = self.build_session_filepath('APP_START', '.html')
        with open(html_file_path, 'w') as html_fp:
            html_fp.write(html)

        return html_file_path

    def launch(self):

        html_file_path = self._generate_html_file(self.start_html_fname)
        self.start_(html_file_path)

    def _setup_callbacks(self):

        self.add_op_handler('print_message', self.print_message)

    def print_message(self, op, op_data, c_app_runner):

        logging.info('')
        logging.info(':: got message "{0}"'.format(op_data.get('message','')))
        logging.info('')



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

os.environ['PXLC_CHROMEGUI_ROOT'] = os.path.sep.join(os.path.realpath(__file__).replace('\\','/').split('/')[:-3])

CHROMEGUI_ROOT = os.getenv('PXLC_CHROMEGUI_ROOT')

sys.path.append(CHROMEGUI_ROOT)

import chromegui


class ChromeGuiApp(chromegui.ChromeGuiAppBase):

    def __init__(self, app_short_name, app_title_label, app_dir_path, start_html_filename, width=480, height=600,
                 config_filepath='', log_to_shell=False, log_level_str='', template_dirpath=''):

        super(ChromeGuiApp, self).__init__(app_short_name, app_title_label, app_dir_path, width=width,
                                           height=height, config_filepath=config_filepath,
                                           log_to_shell=log_to_shell, log_level_str=log_level_str,
                                           template_dirpath=template_dirpath)

        self.start_html_fname = start_html_filename

        self.shot_data_list = [
                {'show': 'pxlc', 'seq_code': 'pxlc_010', 'shot_code': 'pxlc_010_0010', 'status': 'inp',
                    'status_layout': 'appr', 'status_anim': 'rev', 'status_fx': 'na',
                    'status_light': 'wtg', 'status_comp': 'wtg', 'id': 100},

                {'show': 'pxlc', 'seq_code': 'pxlc_010', 'shot_code': 'pxlc_010_0020', 'status': 'inp',
                    'status_layout': 'appr', 'status_anim': 'appr', 'status_fx': 'na',
                    'status_light': 'inp', 'status_comp': 'wtg', 'id': 101},

                {'show': 'pxlc', 'seq_code': 'pxlc_010', 'shot_code': 'pxlc_010_0030', 'status': 'rdy',
                    'status_layout': 'wtg', 'status_anim': 'wtg', 'status_fx': 'wtg',
                    'status_light': 'wtg', 'status_comp': 'wtg', 'id': 102},
        ]

        status_select_edit_params = [
            # option group
            {
                # 'label': 'Statuses',
                # options in option group
                'options': [
                    {'label': 'Waiting', 'value': 'wtg' },
                    {'label': 'Ready to Start', 'value': 'rdy' },
                    {'label': 'In Progress', 'value': 'inp' },
                    {'label': 'Not Needed', 'value': 'na' },
                    {'label': 'Approved', 'value': 'appr' },
                    {'label': 'In Rewiew', 'value': 'rev' },
                ]
            }
        ]

        self.col_defs = [
            {'rowHandle': True, 'formatter': 'handle', 'headerSort': False, 'frozen': True,
                'width': 30, 'minWidth': 30},
            {'title': 'ID', 'field': 'id', 'align': 'center'},
            {'title': 'Show', 'field': 'show', 'align': 'center'},
            {'title': 'Sequence', 'field': 'seq_code', 'align': 'left'},
            {'title': 'Shot', 'field': 'shot_code', 'align': 'left'},

            {'title': 'Status', 'field': 'status', 'align': 'left',
                'editor': 'select', 'editorParams': status_select_edit_params
            },

            {'title': 'Layout', 'field': 'status_layout', 'align': 'left',
                'editor': 'select', 'editorParams': status_select_edit_params
            },

            {'title': 'Animation', 'field': 'status_anim', 'align': 'left',
                'editor': 'select', 'editorParams': status_select_edit_params
            },

            {'title': 'FX', 'field': 'status_fx', 'align': 'left',
                'editor': 'select', 'editorParams': status_select_edit_params
            },

            {'title': 'Lighting', 'field': 'status_light', 'align': 'left',
                'editor': 'select', 'editorParams': status_select_edit_params
            },

            {'title': 'Comp', 'field': 'status_comp', 'align': 'left',
                'editor': 'select', 'editorParams': status_select_edit_params
            },
        ]

        self.extra_template_vars = self._setup_extra_template_vars()
        self._setup_callbacks()

    def _setup_extra_template_vars(self):

        res_image_path = os.path.realpath( os.path.join( CHROMEGUI_ROOT, 'res/images' ) )
        res_icon_path = os.path.realpath( os.path.join( CHROMEGUI_ROOT, 'res/icons' ) )

        extra_vars = {
            'RES_IMG_PATH': res_image_path.replace('\\', '/'),
            'RES_ICON_PATH': res_icon_path.replace('\\', '/'),
            'TABLE_COL_DEFS': json.dumps(self.col_defs),
            'TABLE_DATA_ROWS': json.dumps(self.shot_data_list),
        }
        return extra_vars

    def _setup_callbacks(self):

        self.add_op_handler('print_message', self.print_message)

    def launch(self):

        self.start_()

    # --------------------------------------------------------------------------------------------------------
    #  Callback function handlers
    # --------------------------------------------------------------------------------------------------------
    def print_message(self, op, op_data):

        self.info('')
        self.info(':: got message "{0}"'.format(op_data.get('message','')))
        self.info('')



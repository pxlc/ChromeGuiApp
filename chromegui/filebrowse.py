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

CHROMEGUI_ROOT = '/'.join(os.path.realpath(__file__).replace('\\','/').split('/')[:-2])
sys.path.insert(0, '/'.join([ CHROMEGUI_ROOT, 'thirdparty', 'python' ]))

import jinja2


def process(op_data):

    sub_op = op_data.get('sub_op')

    if sub_op == 'path_check.exists':
        path = os.path.abspath(op_data.get('path',''))
        result_op_data = {}
        result_op_data.update(op_data)
        result_op_data.update({'sub_op_return': os.path.exists(path), 'path': path})

        return result_op_data

    return op_data


def get_filebrowse_modal_html():

    html_filepath = '%s/FILEBROWSE_SNIPPET.html' % os.path.dirname(os.path.abspath(__file__).replace('\\','/'))
    with open(html_filepath, 'r') as fp:
        html_str = fp.read()
    return html_str



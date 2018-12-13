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
import datetime
import subprocess

CHROMEGUI_ROOT = '/'.join(os.path.realpath(__file__).replace('\\','/').split('/')[:-2])
sys.path.insert(0, '/'.join([ CHROMEGUI_ROOT, 'thirdparty', 'python' ]))

import jinja2


def human_readable_filesize(num, suffix='B'):
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


def _get_drive_roots():

    if sys.platform != 'win32':
        return []

    p = subprocess.Popen("fsutil fsinfo drives",
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    (out, err) = p.communicate()

    drive_list = out.splitlines()[1].split()[1:]
    for d in drive_list:
        print('    %s' % d)

    return drive_list


def _get_dir_items(dir_path):

    dir_items = []

    item_list = os.listdir(dir_path)
    item_list.sort()

    for idx, item in enumerate(item_list):

        i_path = os.path.join(dir_path, item)
        i_type = 'dir' if os.path.isdir(i_path) else 'file'

        dt_format = '%Y-%m-%d %H:%M:%S'

        i_mtime_str = datetime.datetime.fromtimestamp(os.path.getmtime(i_path)).strftime(dt_format)
        i_ctime_str = datetime.datetime.fromtimestamp(os.path.getctime(i_path)).strftime(dt_format)
        i_size = os.path.getsize(i_path)

        i_size_str = ''
        if i_type == 'file':
            i_size_str = human_readable_filesize(i_size)

        dir_items.append({
            'id': idx, 'name': item, 'size': i_size_str, '_size': i_size,
            'last_mod_dt': i_mtime_str, 'created_dt': i_ctime_str, '_type': i_type
        })

    return dir_items


def process(op_data):

    sub_op = op_data.get('sub_op')

    result_op_data = {}
    result_op_data.update(op_data)

    if sub_op == 'path_check.exists':
        dir_items = []
        path = os.path.abspath(op_data.get('path',''))
        path_type = 'unknown'
        if os.path.isfile(path):
            path_type = 'file'
            dir_items = _get_dir_items(os.path.dirname(path))
        elif os.path.isdir(path):
            path_type = 'dir'
            dir_items = _get_dir_items(path)

        result_op_data.update({'sub_op_return': os.path.exists(path), 'path': path, 'path_type': path_type})
        result_op_data.update({'dir_items': dir_items, '_parent_path': os.path.dirname(path)})

    return result_op_data


def _get_root_path_item_html( root_path ):

    item_html_template = '''<a href="#" class="list-group-item list-group-item-action" ''' \
                            '''onclick="chromegui.filebrowse.set_root('{0}');">{1}</a>'''

    return item_html_template.format(root_path.replace('\\','/'), root_path)


def get_filebrowse_modal_html(extra_root_path_list=[]):

    html_filepath = '%s/FILEBROWSE_SNIPPET.html' % os.path.dirname(os.path.abspath(__file__).replace('\\','/'))
    with open(html_filepath, 'r') as fp:
        html_str = fp.read()

    root_path_list = _get_drive_roots()
    root_path_list += extra_root_path_list

    rpath_item_html_list = []

    for root_path in root_path_list:
        rpath_item_html_list.append( _get_root_path_item_html(root_path) )

    join_str = '\n%s' % (24 * ' ')
    html_str = html_str.format(ROOT_PATH_ITEMS=join_str.join(rpath_item_html_list))
    return html_str



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
import traceback


def _run_fn( module_name, fn_name, data_filepath ):

    data = {}
    if os.path.isfile(data_filepath):
        try:
            with open(data_filepath, 'r') as fp:
                data = json.loads(fp.read())
        except:
            return {'status': 'ERROR', 'msg': traceback.format_exc()}

    stmt = 'import {mod}; reload({mod}); fn = {mod}.{fn}'.format(module_name, fn_name)
    try:
        exec(stmt)
    except:
        return {'status': 'ERROR', 'msg': traceback.format_exc()}

    fn_return_value = fn(data)
    return {'status': 'OK', 'data': fn_return_value, 'data_type': str(type(fn_return_value)).split("'")[1] }


def run_fn( module_name, fn_name, data_filepath ):

    result_data = _run_fn( module_name, data_filepath )

    with open(data_filepath, 'w') as fp:
        fp.write(json.dumps(result_data, indent=2, sort_keys=True))


def _run_fn_dynamic( module_filepath, fn_name, data_filepath ):

    data = {}
    if os.path.isfile(data_filepath):
        try:
            with open(data_filepath, 'r') as fp:
                data = json.loads(fp.read())
        except:
            return {'status': 'ERROR', 'msg': traceback.format_exc()}

    module_file = os.path.basename(module_filepath)
    module_name = module_file.replace('.py', '')
    module_dirpath = os.path.dirname(module_filepath).replace('\\', '/')

    sys.path.insert(0, module_dirpath)
    result_data = _run_fn(module_name, fn_name, data_filepath)
    sys.path.pop(0)

    return result_data


def run_fn_dynamic( module_filepath, fn_name, data_filepath ):

    result_data = _run_fn_dynamic( module_filepath, fn_name, data_filepath )

    with open(data_filepath, 'w') as fp:
        fp.write(json.dumps(result_data, indent=2, sort_keys=True))



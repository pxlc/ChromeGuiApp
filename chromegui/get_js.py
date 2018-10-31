
import os
import sys


def get_js_file_url():

    prefix = 'file://'
    if sys.platform == 'win32':
        prefix += '/'
    js_url = '{0}/js/chromegui.js'.format(
                os.path.dirname(os.path.dirname(os.path.realpath(__file__))).replace('\\', '/') )
    return js_url




import os
import sys
import datetime
import getpass


def now_datetime_str( format='full', trim_micro=False, two_digit_year=False ):

    # format is 'display', 'full', 'compact', or provided format string
    # %Y%m%d-%H%M%S%f
    now_dt = datetime.datetime.now()

    if '%' in format:
        return now_dt.strftime(format)

    idx_map = {'yr': 0, 'mo': 1, 'day': 2, 'hr': 3, 'min': 4, 'sec': 5, 'mic': 6}

    bits = now_dt.strftime('%Y.%m.%d.%H.%M.%S.%f').split('.')

    year = bits[idx_map['yr']][2:] if two_digit_year else bits[idx_map['yr']]
    month = bits[idx_map['mo']]
    day = bits[idx_map['day']]

    hour = bits[idx_map['hr']]
    minute = bits[idx_map['min']]
    second = bits[idx_map['sec']]
    ms = bits[idx_map['mic']][:3] if trim_micro else bits[idx_map['mic']]

    if format == 'compact':
        return '{yr}{mo}{day}_{hr}{m}{s}{ms}'.format(
                yr=year, mo=month, day=day, hr=hour, m=minute, s=second, ms=ms)
    elif format == 'compact_time':
        return '{yr}-{mo}-{day}_{hr}{m}{s}{ms}'.format(
                yr=year, mo=month, day=day, hr=hour, m=minute, s=second, ms=ms)
    elif format == 'full':
        return '{yr}-{mo}-{day}_{hr}-{m}-{s}.{ms}'.format(
                yr=year, mo=month, day=day, hr=hour, m=minute, s=second, ms=ms)
    # otherwise return display format
    return '{yr}-{mo}-{day} {hr}:{m}:{s}.{ms}'.format(
            yr=year, mo=month, day=day, hr=hour, m=minute, s=second, ms=ms)


def get_temp_path():

    if os.getenv('TEMP'):
        return os.getenv('TEMP')

    if sys.platform == 'win32':
        return os.path.join(os.getenv('USERPROFILE'), 'AppData', 'Local', 'Temp')

    return '/usr/tmp'


def get_app_user_temp_path(app_name, folder_pre=''):

    return os.path.join(get_temp_path(), '{p}{app}_{u}'.format(p=folder_pre, app=app_name, u=getpass.getuser()))


def get_app_session_logfile(app_name, folder_pre='', dt_str=''):

    if not dt_str:
        dt_str = now_datetime_str('compact', trim_micro=True)
    log_filename = 'session_{}.log'.format(dt_str)

    return os.path.join(get_app_user_temp_path(app_name, folder_pre), log_filename)




import os
import sys
import datetime
import getpass
import logging


def setup_logger(logger, log_filepath, logging_level, log_to_shell=False):

    log_formatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]:  %(message)s")

    file_handler = logging.FileHandler(log_filepath)
    file_handler.setLevel(logging_level)
    file_handler.setFormatter(log_formatter)

    logger.addHandler(file_handler)

    if log_to_shell:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging_level)
        console_handler.setFormatter(log_formatter)

        logger.addHandler(console_handler)


def now_datetime_str( format='full', two_digit_year=False ):

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
    ms = bits[idx_map['mic']][:3]

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

    # if os.getenv('TEMP'):
    #     return os.getenv('TEMP')

    if sys.platform == 'win32':
        return os.path.join(os.getenv('USERPROFILE'), 'AppData', 'Local', 'Temp', 'ChromeAppGui')

    if sys.platform in ('linux2', 'linux', 'darwin'):
        return os.path.expandvars('${HOME}/.ChromeAppGui')

    raise Exception('System platform "%s" is not a supported platform.' % sys.platform)


def get_app_user_temp_path(app_name, folder_pre='', temp_root=''):

    t_root = temp_root if temp_root else get_temp_path()

    return os.path.join(t_root, '{p}{app}_{u}'.format(p=folder_pre, app=app_name, u=getpass.getuser()))


def get_app_session_logfile(app_name, folder_pre='', dt_str='', temp_root=''):

    if not dt_str:
        dt_str = now_datetime_str('compact', trim_micro=True)
    log_filename = 'session_{0}.log'.format(dt_str)

    return os.path.join(get_app_user_temp_path(app_name, folder_pre, temp_root), log_filename)


def get_app_session_log_filename(dt_str=''):

    if not dt_str:
        dt_str = now_datetime_str('compact', trim_micro=True)
    log_filename = 'session_{0}.log'.format(dt_str)
    return log_filename


def get_next_port_num(config):

    user_cache = config.get('user_info_cache')
    user_temp = config.get('user_temp_root')

    target_dir = user_cache
    if not os.path.isdir(user_cache):
        target_dir = user_temp

    port_file = '/'.join([ target_dir, 'NEXT_PORT' ])

    port_start = config.get('port_cycle_range',{}).get('start',9000)
    port_end = config.get('port_cycle_range',{}).get('end',9999)

    next_port = port_start

    if os.path.isfile(port_file):
        with open(port_file, 'r') as fp:
            next_port = int(fp.read().strip())

    if next_port > port_end:
        next_port = port_start

    with open(port_file, 'w') as fp:
        fp.write('%s' % (next_port+1))

    return next_port


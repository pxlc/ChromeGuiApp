
import os
import sys
import json

import logging
import traceback

CHROMEGUI_ROOT = '/'.join(os.path.realpath(__file__).replace('\\','/').split('/')[:-2])


def load_config_file(config_filepath=None):

    use_config_filepath = '/'.join([ CHROMEGUI_ROOT, 'config', 'default_chromegui_config.json' ])
    if config_filepath:
        use_config_filepath = config_filepath
    elif os.getenv('PXLC_CHROMEGUI_CONFIG_FILEPATH',''):
        use_config_filepath = os.getenv('PXLC_CHROMEGUI_CONFIG_FILEPATH')

    config_data = {}
    try:
        with open(use_config_filepath, 'r') as fp:
            config_data = json.loads(fp.read())
    except:
        logging.error(traceback.format_exc())

    final_config_data = {}
    for option, info in config_data.items():
        if option == '#':
            continue  # skip comment entries

        opt_type = info.get('_type_')
        if opt_type == 'single_path_create':
        #{
            p_list = []
            if sys.platform in info:
                p_list = info.get(sys.platform)
            elif 'default' in info:
                p_list = info.get('default')

            final_config_data[option] = ''
            for p in p_list:
                p_exp = os.path.expandvars(p).replace('\\','/')
                if '$' in p_exp:
                    continue # not able to expand due to env var not defined, so skip
                if not os.path.isdir(p_exp):
                    try:
                        os.makedirs(p_exp)
                    except:
                        pass
                if os.path.isdir(p_exp):
                    final_config_data[option] = p_exp
                    break
        #}
        elif opt_type == "multi_path":
        #{
            p_list = []
            if sys.platform in info:
                p_list = info.get(sys.platform)
            elif 'default' in info:
                p_list = info.get('default')

            final_config_data[option] = []
            for p in p_list:
                p_exp = os.path.expandvars(p).replace('\\','/')
                final_config_data[option].append(p_exp)
        #}
        else:
            final_config_data[option] = info

    return final_config_data



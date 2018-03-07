import os
import yaml
import logging.config
import logging


def setup_logging(path, debug_mode):
    default_level = 'INFO'

    if os.path.exists(path):
        with open(path, 'rt') as f:
            try:
                config = yaml.safe_load(f.read())
                loggers = config['loggers']
                for logger, value in loggers.items():
                    if debug_mode:
                        loggers[logger]['level'] = 'DEBUG'
                    else:
                        current_level = value.get('level')
                        is_level_not_set = value['level'] == 0 or current_level is None
                        loggers[logger]['level'] = default_level if is_level_not_set else current_level

                logging.config.dictConfig(config)
            except Exception as e:
                print(e)
                print('Failed to load configuration file.\
                      Using default configs. Kqueen generic logging, user logging will not work properly')
                logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        print('Failed to load configuration file.\
              Using default configs. Kqueen generic logging, user logging will not work properly')


# Import user data from flask session to provide user_logging
def user_prefix(session):
    user_prefix = '[USER: {} ID:{}]'.format(session['user']['username'], session['user']['id'])
    return user_prefix

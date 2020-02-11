from configparser import ConfigParser
import json

def create_config(config_path):
    config = dict()
    config_raw = ConfigParser()
    config_raw.read("default.ini")
    config_raw.read(config_path)

    # Config #
    config['bot_token'] = config_raw.get(
        'Config',
        'BOT_TOKEN')
    config['language'] = config_raw.get(
        'Config',
        'LANGUAGE')
    config['prefix'] = config_raw.get(
        'Config',
        'PREFIX')


    # Commands #
    config['pokemon_aliases'] = json.loads(config_raw.get(
        'Commands',
        'POKEMON_ALIASES'))


    # DB #
    config['db_scan_schema'] = config_raw.get(
        'DB',
        'SCANNER_DB_SCHEMA')
    config['db_host'] = config_raw.get(
        'DB',
        'HOST')
    config['db_port'] = config_raw.getint(
        'DB',
        'PORT')
    config['db_user'] = config_raw.get(
        'DB',
        'USER')
    config['db_pass'] = config_raw.get(
        'DB',
        'PASSWORD')
    config['db_portal_dbname'] = config_raw.get(
        'DB',
        'PORTAL_DB_NAME')
    config['db_dbname'] = config_raw.get(
        'DB',
        'SCANNER_DB_NAME')

    return config
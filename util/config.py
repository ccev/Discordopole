from configparser import ConfigParser
import json
import os

def create_config(config_path):
    config = dict()
    config_raw = ConfigParser()
    config_raw.read("config/default.ini")
    config_raw.read(config_path)

    # Config #
    config['bot_token'] = config_raw.get(
        'Config',
        'BOT_TOKEN')
    config['language'] = config_raw.get(
        'Config',
        'LANGUAGE')
    config['timezone'] = config_raw.get(
        'Config',
        'TIMEZONE_OFFSET')
    config['prefix'] = config_raw.get(
        'Config',
        'PREFIX')
    config['admins'] = config_raw.get(
        'Config',
        'ADMINS')
    config['admins'] = list(map(int, list(config['admins'].split(','))))
    config['mon_icon_repo'] = config_raw.get(
        'Config',
        'POKEMON_ICON_REPO')
    config['emote_repo'] = config_raw.get(
        'Config',
        'EMOTE_REPO')


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
    config['db_dbname'] = config_raw.get(
        'DB',
        'SCANNER_DB_NAME')

    return config
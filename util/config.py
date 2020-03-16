from configparser import ConfigParser
import json
import os

def create_config(config_path):
    config = dict()
    config_raw = ConfigParser()
    config_raw.read("default.ini")
    config_raw.read(config_path)

    # Config #
    config['bot_token'] = config_raw.get('Config','bot_token')
    config['language'] = config_raw.get('Config','language')
    config['timezone'] = config_raw.get('Config','timezone_offset')
    config['prefix'] = config_raw.get('Config','prefix')
    config['admins'] = config_raw.get('Config','admins')
    config['admins'] = list(map(int, list(config['admins'].split(','))))
    config['mon_icon_repo'] = config_raw.get('Config','pokemon_icon_repo')
    config['emote_repo'] = config_raw.get('Config','emote_repo')
    config['host_channel'] = config_raw.get('Config','trash_channel')
    config['host_server'] = config_raw.get('Config','trash_server')



    # Maps #
    config['use_static'] = config_raw.getboolean('Maps','use_static_maps')
    config['static_provider'] = config_raw.get('Maps','provider')
    config['tileserver_url'] = config_raw.get('Maps','tileserver_url')
    config['use_map'] = config_raw.getboolean('Maps','use_map_frontend')
    config['map'] = config_raw.get('Maps','frontend')
    config['map_url'] = config_raw.get('Maps','map_url')



    # Commands #
    config['pokemon_aliases'] = json.loads(config_raw.get('Commands','pokemon_aliases'))
    config['gyms_aliases'] = json.loads(config_raw.get('Commands','gyms_aliases'))


    # DB #
    config['db_scan_schema'] = config_raw.get('DB','scanner_db_schema')
    config['db_host'] = config_raw.get('DB','host')
    config['db_port'] = config_raw.getint('DB','port')
    config['db_user'] = config_raw.get('DB','user')
    config['db_pass'] = config_raw.get('DB','password')
    config['db_dbname'] = config_raw.get('DB','scanner_db_name')

    return config
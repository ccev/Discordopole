from configparser import ConfigParser
import json
import os

class Config():
    def __init__(self, config_path):
        config_raw = ConfigParser(interpolation=None)
        config_raw.read("default.ini")
        config_raw.read(config_path)

        # Config #
        self.bot_token = config_raw.get('Config','bot_token')
        self.language = config_raw.get('Config','language')
        self.timezone = config_raw.get('Config','timezone_offset')
        self.prefix = config_raw.get('Config','prefix')
        self.admins = config_raw.get('Config','admins')
        self.admins = list(map(int, list(self.admins.split(','))))
        self.mon_icon_repo = config_raw.get('Config','pokemon_icon_repo')
        self.emote_repo = config_raw.get('Config','emote_repo')
        self.host_channel = config_raw.get('Config','trash_channel')
        self.host_server = config_raw.get('Config','trash_server')



        # Maps #
        self.use_map = config_raw.getboolean('Maps','use_map_frontend')
        self.map = config_raw.get('Maps','frontend')
        self.map_url = config_raw.get('Maps','map_url')
        self.tileserver_url = config_raw.get('Maps','tileserver_url')



        # Commands #
        self.cmd_roles = json.loads(config_raw.get('Commands','required_roles'))
        self.cmd_channels = json.loads(config_raw.get('Commands','channels'))
        self.pokemon_aliases = json.loads(config_raw.get('Commands','pokemon_aliases'))
        self.gyms_aliases = json.loads(config_raw.get('Commands','gyms_aliases'))
        self.quest_aliases = json.loads(config_raw.get('Commands','quest_aliases'))


        # DB #
        self.db_scan_schema = config_raw.get('DB','scanner_db_schema')
        self.db_host = config_raw.get('DB','host')
        self.db_port = config_raw.getint('DB','port')
        self.db_user = config_raw.get('DB','user')
        self.db_pass = config_raw.get('DB','password')
        self.db_dbname = config_raw.get('DB','scanner_db_name')
        
        # alt DB for pokemon#

        self.use_alt_table_for_pokemon = config_raw.getboolean('alternative_table_for_pokemon','use_alt_table_for_pokemon')
        self.alt_db_scan_schema = config_raw.get('alternative_table_for_pokemon','alt_scanner_db_schema')
        self.alt_db_host = config_raw.get('alternative_table_for_pokemon','alt_host')
        self.alt_db_port = config_raw.getint('alternative_table_for_pokemon','alt_port')
        self.alt_db_user = config_raw.get('alternative_table_for_pokemon','alt_user')
        self.alt_db_pass = config_raw.get('alternative_table_for_pokemon','alt_password')
        self.alt_db_dbname = config_raw.get('alternative_table_for_pokemon','alt_scanner_db_name')
        self.alt_pokemon_table = config_raw.get('alternative_table_for_pokemon', 'alt_pokemon_table')
        self.alt_shiny_table = config_raw.get('alternative_table_for_pokemon', 'alt_shiny_table')
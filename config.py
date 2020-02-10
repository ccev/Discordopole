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

    return config
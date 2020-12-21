#from .boards import 
from .config import Config
from .gamedata import GameData
from .maps import MapUrl, StaticMap
from .queries import Queries
from .templates import Templates

from dp.utils.util import get_json_file
from discord.ext import commands

class DPfiles:
    def __init__(self, config):
        self.boards = get_json_file("config/boards.json")
        self.geofences = get_json_file("config/geofence.json")
        self.custom_emotes = get_json_file("config/emotes.json")

        if config.language not in ["de", "en", "es", "fr", "pl"]:
            config.language = "en"
        self.locale = get_json_file(f"dp/data/locale/{config.language}.json")
        if config.language not in ["de", "en", "es", "fr"]:
            config.language = "en"
        self.form_locale = get_json_file(f"dp/data/forms/{config.language}.json")

class DPvars:
    def __init__(self):
        self.config = Config("config/config.ini")
        self.bot = commands.Bot(command_prefix=self.config.prefix, case_insensitive=1)
        self.queries = Queries(self.config)
        self.gamedata = None
        self.map_url = MapUrl(self.config.map, self.config.map_url)
        self.static_map = None

        self.files = DPfiles(self.config)

        self.templates = Templates(self, get_json_file("config/templates.json"))

dp = DPvars()
dp.gamedata = GameData(dp.config.language)
import discord
import requests

from discord.ext import commands

from dp.dp_objects import Config, Queries, Templates, MapUrl, StaticMap, GameData
from dp.utils.logging import log
from dp.utils.util import get_json_file

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

log.info("Initializing Discordopole")
dp = DPvars()

log.info("Loading Pogo data")
dp.gamedata = GameData(dp.config.language)

"""# File Loading
needed_langs = {
    "locale": ["de", "en", "es", "fr", "pl"],
    "mons": ["de", "en", "es", "fr"],
    "items": ["de", "en", "es", "fr"],
    "forms": ["de", "en", "es", "fr"],
    "moves": ["de", "en", "es", "fr"]
}

for k, v in needed_langs.items():
    if bot.config.language not in v:
        needed_langs[k] = "en"
    else:
        needed_langs[k] = bot.config.language

bot.locale = get_json_file(f"dp/data/locale/{needed_langs['locale']}.json")
bot.mon_names = get_json_file(f"dp/data/mon_names/{needed_langs['mons']}.json")
bot.item_names = get_json_file(f"dp/data/items/{needed_langs['items']}.json")
bot.forms = get_json_file(f"dp/data/forms/{needed_langs['forms']}.json")
bot.moves = get_json_file(f"dp/data/moves/{needed_langs['moves']}.json")
log.info("Loaded Language files")"""

# Cog Loading

cogs = [
#    "dp.cogs.usercommands",
#    "dp.cogs.admincommands",
    "dp.cogs.boardloop",
#    "dp.cogs.channelloop"
]
for extension in cogs:
    dp.bot.load_extension(extension)
log.info("Connecting to Discord")

@dp.bot.event
async def on_ready():
    #await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="Discordopole"))
    log.success("Done loading. Ready for action.")
    trash_channel = await dp.bot.fetch_channel(dp.config.host_channel)
    dp.static_map = StaticMap(trash_channel, dp.config.tileserver_url)

dp.bot.run(dp.config.bot_token)
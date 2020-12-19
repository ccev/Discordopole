import discord
import requests

from discord.ext import commands

from dp.objects import Config, Queries, Templates, MapUrl, StaticMap, GameData
from dp.utils.logging import log
from dp.utils.util import get_json_file

class DPfiles:
    def __init__(self):
        self.boards = get_json_file("config/boards.json")
        self.geofences = get_json_file("config/geofence.json")
        self.custom_emotes = get_json_file("config/emotes.json")
        self.available_grunts = {}

class DPvars:
    def __init__(self):
        self.config = None
        self.bot = None
        self.queries = None
        self.gamedata = None
        self.templates = None
        self.map_url = None
        self.static_map = None

        self.files = DPfiles()


dp = DPvars()

log.info("Initializing...")

dp.config = Config("config/config.ini")
log.info("Parsed config")

dp.bot = commands.Bot(command_prefix=dp.config.prefix, case_insensitive=1)

dp.queries = Queries(dp.bot)
log.info("Imported queries")

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

log.info("Loading up-to-date proto and gamemaster data...")
dp.gamedata = GameData(dp.config.language)

## Config files

dp.templates = Templates(dp.config, get_json_file("config/templates.json"))
dp.map_url = MapUrl(dp.config.map, dp.config.map_url)

for gid, data in requests.get("https://raw.githubusercontent.com/ccev/pogoinfo/info/grunts.json").json().items():
    encounters = data.get("encounters", {}).get("first", [])
    if data.get("second_reward", False):
        encounters += data.get("encounters", {}).get("second", [])
    #encounters = [int(e.split("_")[0]) for e in encounters]
    dp.files.available_grunts[gid] = encounters

log.info("Loaded rest of the needed data")

# Cog Loading

cogs = [
#    "dp.cogs.usercommands",
    "dp.cogs.admincommands",
    "dp.cogs.boardloop",
#    "dp.cogs.channelloop"
]
for extension in cogs:
    dp.bot.load_extension(extension)
log.info("Loaded cogs. Connecting to Discord now")

@dp.bot.event
async def on_ready():
    #await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="Discordopole"))
    log.success("Connected to Discord. Ready to take commands.")
    trash_channel = await dp.bot.fetch_channel(dp.config.host_channel)
    dp.static_map = StaticMap(dp.bot, trash_channel)

dp.bot.run(dp.config.bot_token)
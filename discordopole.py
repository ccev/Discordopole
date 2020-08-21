import discord

from discord.ext import commands

from dp.utils.config import Config
from dp.utils.queries import Queries
from dp.utils.logging import log
from dp.utils.util import get_json_file
from dp.utils.models.templates import Templates
from dp.utils.models.maps import MapUrl, StaticMap

log.info("Initializing...")

config = Config("config/config.ini")
log.info("Parsed config")

bot = commands.Bot(command_prefix=config.prefix, case_insensitive=1)
bot.config = config

bot.queries = Queries(bot)
log.info("Imported queries")

# File Loading
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
log.info("Loaded Language files")

## Config files

bot.templates = Templates(bot, get_json_file("config/templates.json"))
bot.map_url = MapUrl(config.map, config.map_url)
bot.boards = get_json_file("config/boards.json")
bot.geofences = get_json_file("config/geofence.json")
bot.custom_emotes = get_json_file("config/emotes.json")
log.info("Loaded rest of the needed data")

# Cog Loading

cogs = [
#    "dp.cogs.usercommands",
    "dp.cogs.admincommands",
    "dp.cogs.boardloop",
#    "dp.cogs.channelloop"
]
for extension in cogs:
    bot.load_extension(extension)
log.info("Loaded cogs. Connecting to Discord now")

@bot.event
async def on_ready():
    #await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="Discordopole"))
    log.success("Connected to Discord. Ready to take commands.")
    trash_channel = await bot.fetch_channel(bot.config.host_channel)
    bot.static_map = StaticMap(bot, trash_channel)

bot.run(bot.config.bot_token)
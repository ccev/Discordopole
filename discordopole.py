from dp.utils.logging import log
log.info("Initializing Discordopole")

import discord
import requests

from discord.ext import commands

from dp.dp_objects import Config, Queries, Templates, MapUrl, StaticMap, GameData
from dp.dp_objects import dp


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
    dp.static_map = StaticMap(dp.config.tileserver_url, trash_channel)

dp.bot.run(dp.config.bot_token)
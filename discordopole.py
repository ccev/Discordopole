import discord
import json
from discord.ext import commands
import aiomysql
import asyncio

from mondetails import details
import queries
import config

config = config.create_config("config.ini")
bot = commands.Bot(command_prefix=config['prefix'], case_insensitive=1)

with open(f"data/dts/{config['language']}.json") as localejson:
    locale = json.load(localejson)

@bot.event
async def on_ready():
    print("Connected to Discord. Ready to take commands.")

@bot.command(pass_context=True, aliases=config['pokemon_aliases'])
async def pokemon(ctx, stat_name):
    mon = details(stat_name, config['language'])
    print(f"Generating {mon.name} Stats...")

    text = ""
    embed = discord.Embed(title=mon.name, description=text)
    embed.set_thumbnail(url=mon.icon)
    embed.set_footer(text=f"{locale['loading']} {mon.name} Stats", icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    message = await ctx.send(embed=embed)

    shiny_count = await queries.get_shiny_count(mon.id, config)

    if shiny_count > 0:
        shiny_total = await queries.get_shiny_total(mon.id, config)
        shiny_odds = int(round((shiny_total / shiny_count), 0))
        text = text + f"{locale['shinies']}: **1:{shiny_odds}** ({shiny_count:_}/{shiny_total:_})\n"
    else:
        text = text + f"{locale['shinies']}: **0**\n"

    embed.description = text.replace("_", locale['decimal_comma']) 
    await message.edit(embed=embed)

    print(f"     [1/3] Shiny Data for {mon.name} Stats")

    scan_numbers = await queries.get_scan_numbers(mon.id, config)
    for scanned, hundos, zeros, nineties in scan_numbers:
        scanned_total = int(scanned)
        if scanned_total > 0:
            hundo_count = int(hundos)
            zero_count = int(zeros)
            ninety_count = int(nineties)
        else:
            hundo_count = 0
            zero_count = 0
            ninety_count = 0

    if hundo_count > 0:
        hundo_odds = int(round((scanned_total / hundo_count), 0))
        text = text + f"{locale['hundos']}: **{hundo_count:_}** (1:{hundo_odds})\n\n"
    else:
        text = text + f"{locale['hundos']}: **0/{scanned_total:_}**\n\n"


    if ninety_count > 0:
        ninety_odds = round((scanned_total / ninety_count), 0)
        text = text + f"{locale['90']}: **{ninety_count:_}** (1:{int(ninety_odds)}) | "
    else:
        text = text + f"{locale['90']}: **0** | "

    if zero_count > 0:
        zero_odds = round((scanned_total / zero_count), 0)
        text = text + f"{locale['0']}: **{zero_count:_}** (1:{int(zero_odds)})\n"
    else:
        text = text + f"{locale['0']}: **0**\n"

    embed.description = text.replace("_", locale['decimal_comma']) 
    await message.edit(embed=embed)

    print(f"     [2/3] Scan Data for {mon.name} Stats")

    big_numbers = await queries.get_big_numbers(mon.id, config)
    for mons, found, boosted in big_numbers:
        mon_total = int(mons)
        if found is not None:
            found_count = int(found)
            boosted_count = int(boosted)
        else:
            found_count = 0
            boosted_count = 0

    if found_count > 0:
        mon_odds = int(round((mon_total / found_count), 0))
        text = text.replace(f"\n{locale['90']}", f"{locale['rarity']}: **1:{mon_odds}**\n\n{locale['90']}")

        boosted_odds = str(round((boosted_count / found_count * 100), 1)).replace(".", ",")
        text = text + f"{locale['weatherboost']}: **{boosted_odds}%**\n"

        scanned_odds = str(round((scanned_total / found_count * 100), 1)).replace(".", ",")
        text = text + f"{locale['scanned']}: **{scanned_odds}%**\n\n"

        text = text + f"{locale['total_found']}: **{found_count:_}**"
    else:
        text = text.replace(f"\n{locale['90']}", f"{locale['rarity']}: **0**\n\n{locale['90']}")
        text = text + f"{locale['weatherboost']}: **0%**\n{locale['scanned']}: **0**\n\n{locale['total_found']}: **0**"

    embed.description = text.replace("_", ".")
    embed.set_footer(text="")
    await message.edit(embed=embed)

    print(f"     [3/3] Total Data for {mon.name} Stats")
    print(f"Done with {mon.name} Stats.")

bot.run(config['bot_token'])
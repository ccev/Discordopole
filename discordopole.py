import discord
import json
from discord.ext import commands
import aiomysql
import asyncio
import os
from itertools import islice
from datetime import datetime

from util.mondetails import details
import util.queries
import util.config

MAX_MOVE_IN_LIST = 291
queries = util.queries
config = util.config.create_config("config/config.ini")
bot = commands.Bot(command_prefix=config['prefix'], case_insensitive=1)

with open(f"data/dts/{config['language']}.json") as localejson:
    locale = json.load(localejson)

with open("config/boards.json", "r") as f:
    boards = json.load(f)

with open(f"data/moves/{config['language']}.json") as f:
    moves = json.load(f)

with open("config/geofence.json") as f:
    geofences = json.load(f)

with open("config/emotes.json") as f:
    custom_emotes = json.load(f)

def get_area_coords(areaname):
    for area in geofences:
        if area['name'].lower() == areaname.lower():
            stringfence = ""
            for coordinates in area['path']:
                stringfence = f"{stringfence}{coordinates[0]} {coordinates[1]},"
            stringfence = f"{stringfence}{area['path'][0][0]} {area['path'][0][1]}"
            return stringfence

async def board_loop():
    while not bot.is_closed():
        for board in boards['raids']:
            channel = await bot.fetch_channel(board["channel_id"])
            message = await channel.fetch_message(board["message_id"])
            area = get_area_coords(board["area"])
            text = ""
            raids = await queries.get_active_raids(config, area, board["levels"])
            if not raids:
                text = locale["empty_board"]
            else:
                for start, end, lat, lon, mon_id, move_1, move_2, name, ex, level in islice(raids, 23):
                    end = datetime.fromtimestamp(end).strftime(locale['time_format_hm'])
                    ex_emote = ""
                    if ex == 1:
                        ex_emote = f"{custom_emotes['ex_eligible']} "
                    if not mon_id is None and mon_id > 0:
                        mon_name = details.id(mon_id, config['language'])
                        if move_1 > MAX_MOVE_IN_LIST:
                            move_1 = "?"
                        else:
                            move_1 = moves[str(move_1)]["name"]
                        if move_2 > MAX_MOVE_IN_LIST:
                            move_2 = "?"
                        else:
                            move_2 = moves[str(move_2)]["name"]
                        text = text + f"{ex_emote}**{name}**: {locale['until']} {end}\n**{mon_name}** - *{move_1} / {move_2}*\n\n"
                
            embed = discord.Embed(title=locale['raids'], description=text, timestamp=datetime.utcnow())

            await message.edit(embed=embed)
            await asyncio.sleep(1)
        for board in boards['eggs']:
            channel = await bot.fetch_channel(board["channel_id"])
            message = await channel.fetch_message(board["message_id"])
            area = get_area_coords(board["area"])
            text = ""
            raids = await queries.get_active_raids(config, area, board["levels"])
            if not raids:
                text = locale["empty_board"]
            else:
                for start, end, lat, lon, mon_id, move_1, move_2, name, ex, level in islice(raids, 23):
                    start = datetime.fromtimestamp(start).strftime(locale['time_format_hm'])
                    end = datetime.fromtimestamp(end).strftime(locale['time_format_hm'])
                    ex_emote = ""
                    if ex == 1:
                        ex_emote = f"{custom_emotes['ex_eligible']} "
                    if mon_id is None or mon_id ==0:
                        egg_emote = custom_emotes[f"raid_egg_level_{level}"]
                        text = text + f"{egg_emote} {ex_emote}**{name}**: {start}  –  {end}\n"
                
            embed = discord.Embed(title=locale['eggs'], description=text, timestamp=datetime.utcnow())

            await message.edit(embed=embed)
            await asyncio.sleep(1)
        await asyncio.sleep(20)

@bot.group(pass_context=True)
async def board(ctx):
    if not ctx.message.author.id in config['admins']:
        return
    if ctx.invoked_subcommand is None:
        await ctx.send("`create/delete`")

@board.group(pass_context=True)
async def create(ctx):
    if not ctx.message.author.id in config['admins']:
        return
    if ctx.invoked_subcommand is None:
        print("Creating an empty Board")
        await ctx.message.delete()
        embed = discord.Embed(title="Empty board", description="")
        message = await ctx.send(embed=embed)
        embed.description = f"Channel ID: `{message.channel.id}`\nMessage ID: `{message.id}`\n"
        await message.edit(embed=embed)
        print("Done creating an empty Board")

@create.command(pass_context=True)
async def raid(ctx, area, levels):
    if not ctx.message.author.id in config['admins']:
        return
    print("Creating Raid Board")
    await ctx.message.delete()

    embed = discord.Embed(title="Raid Board", description="")
    message = await ctx.send(embed=embed)

    with open("config/boards.json", "r") as f:
        boards = json.load(f)
    
    level_list = list(levels.split(','))
    level_list = list(map(int, level_list))
    boards['raids'].append({"channel_id": message.channel.id, "message_id": message.id, "area": area, "levels": level_list})

    with open("config/boards.json", "w") as f:
        f.write(json.dumps(boards, indent=4))

    embed.title = "Succesfully created this Raid Board"
    embed.description = f"Now restart Discordopole to see this message being filled\n\n```Area: {area}\nLevels: {levels}\nChannel ID: {message.channel.id}\nMessage ID: {message.id}```"
    await message.edit(embed=embed)
    print("Wrote Raid Board to config/boards.json")

@create.command(pass_context=True)
async def egg(ctx, area, levels):
    if not ctx.message.author.id in config['admins']:
        return
    print("Creating Egg Board")
    await ctx.message.delete()

    embed = discord.Embed(title="Egg Board", description="")
    message = await ctx.send(embed=embed)

    with open("config/boards.json", "r") as f:
        boards = json.load(f)
    
    level_list = list(levels.split(','))
    level_list = list(map(int, level_list))
    boards['eggs'].append({"channel_id": message.channel.id, "message_id": message.id, "area": area, "levels": level_list})

    with open("config/boards.json", "w") as f:
        f.write(json.dumps(boards, indent=4))

    embed.title = "Succesfully created this Egg Board"
    embed.description = f"Now restart Discordopole to see this message being filled\n\n```Area: {area}\nLevels: {levels}\nChannel ID: {message.channel.id}\nMessage ID: {message.id}```"
    await message.edit(embed=embed)
    print("Wrote Raid Board to config/boards.json")

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

@bot.event
async def on_ready():
    print("Connected to Discord. Ready to take commands.")
    bot.loop.create_task(board_loop())

bot.run(config['bot_token'])

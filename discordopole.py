import discord
import json
import aiomysql
import aiohttp
import asyncio
import os
import dateparser
import matplotlib.pyplot as plt

from dateutil.relativedelta import relativedelta
from itertools import islice
from datetime import datetime
from datetime import date
from discord.ext import commands

from util.mondetails import details
import util.queries
import util.config

MAX_MOVE_IN_LIST = 291
queries = util.queries
config = util.config.create_config("config/config.ini")
bot = commands.Bot(command_prefix=config['prefix'], case_insensitive=1)

if not os.path.exists("data/raid_cache.json"):
    f = open("data/raid_cache.json", 'w+')
    f.write("{}")
    f.close()

with open(f"data/dts/{config['language']}.json") as localejson:
    locale = json.load(localejson)

with open("config/boards.json", "r") as f:
    bot.boards = json.load(f)

with open(f"data/moves/{config['language']}.json") as f:
    moves = json.load(f)

with open("config/geofence.json") as f:
    geofences = json.load(f)

with open("config/emotes.json") as f:
    bot.custom_emotes = json.load(f)

def get_area(areaname):
    stringfence = "-100 -100, -100 100, 100 100, 100 -100, -100 -100"
    namefence = locale['all']
    for area in geofences:
        if area['name'].lower() == areaname.lower():
            namefence = area['name'].capitalize()
            stringfence = ""
            for coordinates in area['path']:
                stringfence = f"{stringfence}{coordinates[0]} {coordinates[1]},"
            stringfence = f"{stringfence}{area['path'][0][0]} {area['path'][0][1]}"
    area_list = [stringfence, namefence]
    return area_list

async def board_loop():
    while not bot.is_closed():
        for board in bot.boards['raids']:
            try:
                channel = await bot.fetch_channel(board["channel_id"])
                message = await channel.fetch_message(board["message_id"])
                area = get_area(board["area"])
                text = ""
                raids = await queries.get_active_raids(config, area[0], board["levels"], board["timezone"])
                if not raids:
                    text = locale["empty_board"]
                else:
                    length = 0
                    for gym_id, start, end, lat, lon, mon_id, move_1, move_2, name, ex, level, gym_img in raids:
                        end = datetime.fromtimestamp(end).strftime(locale['time_format_hm'])
                        if len(name) >= 30:
                            name = name[0:27] + "..."
                        ex_emote = ""
                        if ex == 1:
                            ex_emote = f"{bot.custom_emotes['ex_pass']} "
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

                            entry = f"{ex_emote}**{name}**: {locale['until']} {end}\n**{mon_name}** - *{move_1} / {move_2}*\n\n"
                            if length + len(entry) >= 2048:
                                break
                            else:
                                text = text + entry
                                length = length + len(entry)
                        
                embed = discord.Embed(title=locale['raids'], description=text, timestamp=datetime.utcnow())
                embed.set_footer(text=area[1])

                await message.edit(embed=embed)
                await asyncio.sleep(board["wait"])
            except Exception as err:              
                print(err)
                print("Error while updating Raid Board. Skipping it.")
                await asyncio.sleep(5)
            
        for board in bot.boards['eggs']:
            try:
                channel = await bot.fetch_channel(board["channel_id"])
                message = await channel.fetch_message(board["message_id"])
                area = get_area(board["area"])
                text = ""
                raids = await queries.get_active_raids(config, area[0], board["levels"], board["timezone"])
                if not raids:
                    text = locale["empty_board"]
                else:
                    length = 0
                    for gym_id, start, end, lat, lon, mon_id, move_1, move_2, name, ex, level, gym_img in raids:
                        start = datetime.fromtimestamp(start).strftime(locale['time_format_hm'])
                        end = datetime.fromtimestamp(end).strftime(locale['time_format_hm'])
                        if len(name) >= 30:
                            name = name[0:27] + "..."
                        ex_emote = ""
                        if ex == 1:
                            ex_emote = f"{bot.custom_emotes['ex_pass']} "
                        if mon_id is None or mon_id == 0:
                            egg_emote = bot.custom_emotes[f"raid_egg_{level}"]
                            entry = f"{egg_emote} {ex_emote}**{name}**: {start}  –  {end}\n"
                            if length + len(entry) >= 2048:
                                break
                            else:
                                text = text + entry
                                length = length + len(entry)
                    
                embed = discord.Embed(title=locale['eggs'], description=text, timestamp=datetime.utcnow())
                embed.set_footer(text=area[1])

                await message.edit(embed=embed)
                await asyncio.sleep(board["wait"])
            except Exception as err:
                print(err)
                print("Error while updating Egg Board. Skipping it.")
                await asyncio.sleep(5)
        
        for board in bot.boards['stats']:
            try:
                channel = await bot.fetch_channel(board["channel_id"])
                message = await channel.fetch_message(board["message_id"])
                area = get_area(board["area"])
                text = ""

                if "mon_active" in board['type']:
                    mon_active = await queries.statboard_mon_active(config, area[0])
                    if not "mon_today" in board['type']:
                        text = f"{text}{bot.custom_emotes['pokeball']} **{mon_active[0][0]:,}** {locale['active_pokemon']}\n\n"

                if "mon_today" in board['type']:
                    mon_today = await queries.statboard_mon_today(config, area[0])
                    if "mon_active" in board['type']:
                        text = f"{text}{bot.custom_emotes['pokeball']} **{mon_active[0][0]:,}** {locale['active_pokemon']} | **{mon_today[0][0]:,}** {locale['today']}\n\n"
                    else:
                        text = f"{text}{bot.custom_emotes['pokeball']} **{mon_today[0][0]:,}** {locale['pokemon_seen_today']}\n\n"
                
                if "gym_amount" in board['type']:
                    gym_amount = await queries.statboard_gym_amount(config, area[0])
                    text = f"{text}{bot.custom_emotes['gym_white']} **{gym_amount[0][0]:,}** {locale['total_gyms']}\n"

                if "raid_active" in board['type']:
                    raid_active = await queries.statboard_raid_active(config, area[0])
                    if not "egg_active" in board['type']:
                        text = f"{text}{bot.custom_emotes['raid']} **{raid_active[0][0]:,}** {locale['active_raids']}\n"

                if "egg_active" in board['type']:
                    egg_active = await queries.statboard_egg_active(config, area[0])
                    if "raid_active" in board['type']:
                        text = f"{text}{bot.custom_emotes['raid']} **{raid_active[0][0]:,}** {locale['active_raids']} | **{egg_active[0][0]:,}** {locale['eggs']}\n"
                    else:
                        text = f"{text}{bot.custom_emotes['raid_egg_1']} **{egg_active[0][0]:,}** {locale['active_eggs']}\n"
                
                if "gym_teams" in board['type']:
                    gym_teams = await queries.statboard_gym_teams(config, area[0])
                    text = f"{text}{bot.custom_emotes['gym_blue']}**{gym_teams[0][1]}**{bot.custom_emotes['blank']}{bot.custom_emotes['gym_red']}**{gym_teams[0][2]}**{bot.custom_emotes['blank']}{bot.custom_emotes['gym_yellow']}**{gym_teams[0][3]}**\n"

                if "stop_amount" in board['type']:
                    stop_amount = await queries.statboard_stop_amount(config, area[0])
                    text = f"{text}\n{bot.custom_emotes['pokestop']} **{stop_amount[0][0]:,}** {locale['total_stops']}\n"

                if "quest_active" in board['type']:
                    quest_active = await queries.statboard_quest_active(config, area[0])
                    text = f"{text}🔎 **{quest_active[0][0]:,}** {locale['quests']}\n"

                if "grunt_active" in board['type']:
                    grunt_active = await queries.statboard_grunt_active(config, area[0])
                    if not "leader_active" in board['type']:
                        text = f"{text}{bot.custom_emotes['grunt_female']} **{grunt_active[0][0]:,}** {locale['active_grunts']}"

                if "leader_active" in board['type']:
                    leader_active = await queries.statboard_leader_active(config, area[0])
                    if "grunt_active" in board['type']:
                        text = f"{text}{bot.custom_emotes['grunt_female']} **{grunt_active[0][0]:,}** {locale['grunts']} | {bot.custom_emotes['cliff']} **{leader_active[0][0]:,}** {locale['leaders']}"
                    else:
                        text = f"{text}{bot.custom_emotes['cliff']} **{leader_active[0][0]:,}** {locale['leaders']}"

                    
                embed = discord.Embed(title=locale['stats'], description=text.replace(",", locale['decimal_comma']), timestamp=datetime.utcnow())
                embed.set_footer(text=area[1])

                await message.edit(embed=embed)
                await asyncio.sleep(board["wait"])
            except Exception as err:
                print(err)
                print("Error while updating Stat Board. Skipping it.")
                await asyncio.sleep(5)
        
        await asyncio.sleep(1)

def get_raid_embed(mon_id, start, end, move_1, move_2, lat, lon, gym_name, gym_img, level):
    #mon_name = details.id(mon_id, config['language'])
    start = datetime.fromtimestamp(start).strftime(locale['time_format_hm'])
    end = datetime.fromtimestamp(end).strftime(locale['time_format_hm'])

    if len(gym_name) >= 30:
        gym_name = gym_name[0:27] + "..."

    if not mon_id is None and mon_id > 0:
        if move_1 > MAX_MOVE_IN_LIST:
            move_1 = "?"
        else:
            move_1 = moves[str(move_1)]["name"]
        if move_2 > MAX_MOVE_IN_LIST:
            move_2 = "?"
        else:
            move_2 = moves[str(move_2)]["name"]

        embed = discord.Embed(description=f"{locale['until']} **{end}**\n{locale['moves']}: **{move_1}** | **{move_2}**\n\n[Google Maps](https://www.google.com/maps/search/?api=1&query={lat},{lon}) | [Apple Maps](https://maps.apple.com/maps?daddr={lat},{lon})")
        embed.set_thumbnail(url=f"{config['mon_icon_repo']}pokemon_icon_{str(mon_id).zfill(3)}_00.png")
        embed.set_author(name=gym_name, icon_url=gym_img)
    else:
        embed = discord.Embed(description=f"{locale['hatches_at']} **{start}**\n{locale['lasts_until']} **{end}**\n\n[Google Maps](https://www.google.com/maps/search/?api=1&query={lat},{lon}) | [Apple Maps](https://maps.apple.com/maps?daddr={lat},{lon})")
        embed.set_thumbnail(url=f"{config['emote_repo']}raid_egg_{level}.png")
        embed.set_author(name=gym_name, icon_url=gym_img)

    return embed


async def raid_channels():
    while not bot.is_closed():
        try:
            for board in bot.boards['raid_channels']:
                channel = await bot.fetch_channel(board["channel_id"])
                channel_id = str(board['channel_id'])
                area = get_area(board["area"])
                raids = await queries.get_active_raids(config, area[0], board["levels"], board["timezone"])
                raid_gyms = []
                with open("data/raid_cache.json", "r") as f:
                    cache = json.load(f)
                
                if not str(board['channel_id']) in cache:
                    cache[channel_id] = {}

                for gym_id, start, end, lat, lon, mon_id, move_1, move_2, name, ex, level, gym_img in raids:
                    raid_gyms.append(gym_id)

                    # Check if the Raid has hatched & edit (or send) accordingly
                    if not mon_id is None and mon_id > 0:
                        if str(gym_id) in cache[channel_id]:
                            if cache[channel_id][gym_id][1] == "egg":
                                cache[channel_id][gym_id][1] = "raid"
                                embed = get_raid_embed(mon_id, start, end, move_1, move_2, lat, lon, name, gym_img, level)
                                message = await channel.fetch_message(cache[channel_id][gym_id][0])
                                await message.edit(embed=embed, content="")
                                await asyncio.sleep(1)
                        else:
                            embed = get_raid_embed(mon_id, start, end, move_1, move_2, lat, lon, name, gym_img)
                            message = await channel.send(embed=embed,content="")
                            cache[channel_id][str(gym_id)] =  [message.id, "raid"]
                            await asyncio.sleep(1)
                        
                    # Send messages for new eggs
                    else:
                        if not str(gym_id) in cache[channel_id]:
                            embed = get_raid_embed(mon_id, start, end, move_1, move_2, lat, lon, name, gym_img, level)
                            message = await channel.send(embed=embed, content="")
                            cache[channel_id][str(gym_id)] =  [message.id, "egg"]
                            await asyncio.sleep(1)

                # Delete despawned Raids
                for cached_raid, entry in list(cache[channel_id].items()):
                    if not cached_raid in raid_gyms:
                        message = await channel.fetch_message(entry[0])
                        await message.delete()
                        cache[channel_id].pop(cached_raid)
                        await asyncio.sleep(1)
                        
                with open("data/raid_cache.json", "w") as f:
                    f.write(json.dumps(cache, indent=4))    

                await asyncio.sleep(board['wait'])
            await asyncio.sleep(2)
        except Exception as err:              
            print(err)
            print("Error while updating Raid Channel. Skipping it.")
            await asyncio.sleep(5)

@bot.group(pass_context=True)
async def board(ctx):
    if not ctx.message.author.id in config['admins']:
        return
    if ctx.invoked_subcommand is None:
        await ctx.send("`create/delete`")

@board.group(pass_context=True)
async def create(ctx):
    if not ctx.message.author.id in config['admins']:
        print(f"@{ctx.author.name} tried to create an empty Board but is no Admin")
        return
    if ctx.invoked_subcommand is None:
        print("Creating an empty Board")
        await ctx.message.delete()
        embed = discord.Embed(title="Empty board", description="")
        message = await ctx.send(embed=embed)
        embed.description = f"Channel ID: `{message.channel.id}`\nMessage ID: `{message.id}`\n"
        await message.edit(embed=embed)
        print("Done creating an empty Board")

@board.command(pass_context=True)
async def delete(ctx, deleted_message_id):
    if not ctx.message.author.id in config['admins']:
        print(f"@{ctx.author.name} tried to create a delete a Board but is no Admin")
        return
    message_found = False
    for board_type in bot.boards:
        for board in bot.boards[board_type]:
            if int(deleted_message_id) == board['message_id']:
                message_found = True
                bot.boards[board_type].remove(board)

                with open("config/boards.json", "w") as f:
                    f.write(json.dumps(bot.boards, indent=4))

                channel = await bot.fetch_channel(board["channel_id"])
                message = await channel.fetch_message(deleted_message_id)
                await message.delete()
                await ctx.send("Successfully deleted Board.")
    
    if not message_found:
        await ctx.send("Couldn't find a board with that Message ID.")
        return

@create.command(pass_context=True)
async def raid(ctx, area, levels):
    if not ctx.message.author.id in config['admins']:
        print(f"@{ctx.author.name} tried to create a Raid Board but is no Admin")
        return
    print("Creating Raid Board")

    embed = discord.Embed(title="Raid Board", description="")
    message = await ctx.send(embed=embed)
    
    level_list = list(levels.split(','))
    level_list = list(map(int, level_list))

    if all(i > 5 or i < 1 for i in level_list):
        embed.description = "Couldn't create Raid Board. Try chosing other levels."
        await message.edit(embed=embed)
        return
    areaexist = False
    for areag in geofences:
        if areag['name'].lower() == area.lower():
            areaexist = True
    if not areaexist:
        embed.description = "Couldn't find that area. Try again."
        await message.edit(embed=embed)
        return
    await ctx.message.delete()
    bot.boards['raids'].append({"channel_id": message.channel.id, "message_id": message.id, "area": area, "timezone": config['timezone'], "wait": 15, "levels": level_list})

    with open("config/boards.json", "w") as f:
        f.write(json.dumps(bot.boards, indent=4))

    embed.title = "Succesfully created this Raid Board"
    embed.description = f"You'll see this message being filled in soon\n\n```Area: {area}\nLevels: {levels}\nChannel ID: {message.channel.id}\nMessage ID: {message.id}```"
    await message.edit(embed=embed)
    print("Wrote Raid Board to config/boards.json")

@create.command(pass_context=True)
async def egg(ctx, area, levels):
    if not ctx.message.author.id in config['admins']:
        print(f"@{ctx.author.name} tried to create a Egg Board but is no Admin")
        return
    print("Creating Egg Board")

    embed = discord.Embed(title="Egg Board", description="")
    message = await ctx.send(embed=embed)
    
    level_list = list(levels.split(','))
    level_list = list(map(int, level_list))

    if all(i > 5 or i < 1 for i in level_list):
        embed.description = "Couldn't create Egg Board. Try chosing other levels."
        await message.edit(embed=embed)
        return
    areaexist = False
    for areag in geofences:
        if areag['name'].lower() == area.lower():
            areaexist = True
    if not areaexist:
        embed.description = "Couldn't find that area. Try again."
        await message.edit(embed=embed)
        return
    await ctx.message.delete()
    bot.boards['eggs'].append({"channel_id": message.channel.id, "message_id": message.id, "area": area, "timezone": config['timezone'], "wait": 15, "levels": level_list})

    with open("config/boards.json", "w") as f:
        f.write(json.dumps(bot.boards, indent=4))

    embed.title = "Succesfully created this Egg Board"
    embed.description = f"You'll see this message being filled in soon\n\n```Area: {area}\nLevels: {levels}\nChannel ID: {message.channel.id}\nMessage ID: {message.id}```"
    await message.edit(embed=embed)
    print("Wrote Raid Board to config/boards.json")

@create.command(pass_context=True)
async def stats(ctx, area, *, types):
    if not ctx.message.author.id in config['admins']:
        print(f"@{ctx.author.name} tried to create a Stat Board but is no Admin")
        return
    print("Creating Stat Board")

    embed = discord.Embed(title="Stat Board", description="")
    message = await ctx.send(embed=embed)
    
    stat_list = list(types.split(','))
    stats = list()
    for stat in stat_list:
        if "mon" in stat:
            if "active" in stat:
                stats.append("mon_active")
            elif "today" in stat:
                stats.append("mon_today")
        elif "gym" in stat:
            if "amount" in stat:
                stats.append("gym_amount")
            elif "team" in stat:
                stats.append("gym_teams")
        elif "raid" in stat:
            #if "active" in stat:
            stats.append("raid_active")
        elif "egg" in stat:
            #if "active" in stat:
            stats.append("egg_active")
        elif "stop" in stat:
            stats.append("stop_amount")
        elif "grunt" in stat:
            #if "active" in stat:
            stats.append("grunt_active")
        elif "leader" in stat:
            stats.append("leader_active")
        elif "quest" in stat:
            stats.append("quest_active")

    areaexist = False
    for areag in geofences:
        if areag['name'].lower() == area.lower():
            areaexist = True
    if not areaexist:
        embed.description = "Couldn't find that area. Try again."
        await message.edit(embed=embed)
        return
    await ctx.message.delete()
    bot.boards['stats'].append({"channel_id": message.channel.id, "message_id": message.id, "area": area, "timezone": config['timezone'], "wait": 15, "type": stats})

    with open("config/boards.json", "w") as f:
        f.write(json.dumps(bot.boards, indent=4))

    embed.title = "Succesfully created this Stat Board"
    embed.description = f"You'll see this message being filled in soon\n\n```Area: {area}\nStats: {stats}\nChannel ID: {message.channel.id}\nMessage ID: {message.id}```"
    await message.edit(embed=embed)
    print("Wrote Stat Board to config/boards.json")

@bot.group(pass_context=True)
async def get(ctx):
    if not ctx.message.author.id in config['admins']:
        return
    if ctx.invoked_subcommand is None:
        await ctx.send("Be more specific")

async def download_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

@get.command(pass_context=True)
async def emotes(ctx):
    if not ctx.message.author.id in config['admins']:
        print(f"@{ctx.author.name} tried to import emotes but is no Admin")
        return

    print(f"@{ctx.author.name} wants to import emotes in Server {ctx.guild.name}. Waiting for confirmation")

    needed_emote_names = ["ex_pass", "raid_egg_1", "raid_egg_2", "raid_egg_3", "raid_egg_4", "raid_egg_5", "gym_blue", "gym_red", "gym_yellow", "gym_white", "blank", "raid", "cliff", "grunt_female", "pokeball", "pokestop"]
    emotejson = json.loads("{}")
    
    embed = discord.Embed(title="Importing emotes will overwrite all custom emotes in this Server!", description="Please make sure you're currently in a server dedicated to host Discordopole emotes.\n\nTo continue, please say the name of this Server.")
    message = await ctx.send(embed=embed)
    def check(m):
        return m.content == ctx.guild.name and m.author == ctx.author and m.channel == ctx.channel
    try:
        confirm = await bot.wait_for('message', check=check, timeout=60)
    except:
        await ctx.send("Aborting Emote import.")
        await message.delete()
        print("No confirmation after 60 seconds. Aborting emote import.")
        return
    print("Server name matched. Deleting all emotes now.")
    await confirm.delete()
    embed = discord.Embed(title="Importing Emotes. Please Wait", description="")
    await message.edit(embed=embed)
    existing_emotes = await ctx.guild.fetch_emojis()
    for emote in existing_emotes:
        await emote.delete()
        embed.description = f"{embed.description}Removed Emote `{emote.name}`\n"
        await message.edit(embed=embed)
    embed.description = ""
    print(f"Done. Now importing all needed emotes from repo {config['emote_repo']}")

    for emote_name in needed_emote_names:
        image = await download_url(f"{config['emote_repo']}{emote_name}.png")
        emote = await ctx.guild.create_custom_emoji(name=emote_name, image=image)
        emote_ref = f"<:{emote.name}:{emote.id}>"
        embed.description = f"{embed.description}{emote_ref} `{emote_ref}`\n"
        await message.edit(embed=embed)

        emotejson.update({emote_name: emote_ref})
    embed.title = "Done importing Emotes"
    await message.edit(embed=embed)
    with open("config/emotes.json", "w") as f:
        f.write(json.dumps(emotejson, indent=4))
    bot.custom_emotes = emotejson

    print("All emotes imported.")

@bot.command(pass_context=True, aliases=config['pokemon_aliases'])
async def pokemon(ctx, stat_name, areaname = "", *, timespan = None):
    mon = details(stat_name, config['mon_icon_repo'], config['language'])

    footer_text = ""
    text = ""
    loading = f"{locale['loading']} {mon.name} Stats"

    area = get_area(areaname)
    if not area[1] == locale['all']:
        footer_text = area[1]
        loading = f"{loading} • "
    if timespan is None:
        timespan = list([datetime(2010, 1, 1, 0, 0), datetime.now()])
    else:
        loading = ""

        if "-" in timespan:
            timespan = list(timespan.split('-'))
            for i in [0, 1]:
                timespan[i] = dateparser.parse(timespan[i])

            footer_text = f"{(locale['between']).capitalize()} {timespan[0].strftime(locale['time_format_dhm'])} {locale['and']} {timespan[1].strftime(locale['time_format_dhm'])}"
        else:
            timespan = list([dateparser.parse(timespan), datetime.now()])

            if area[1] == locale['all']:
                footer_text = f"{(locale['since']).capitalize()} {timespan[0].strftime(locale['time_format_dhm'])}"
            else:
                footer_text = f"{footer_text}, {locale['since']} {timespan[0].strftime(locale['time_format_dhm'])}"

    print(f"@{ctx.author.name} requested {mon.name} stats for area {area[1]}")    

    embed = discord.Embed(title=f"{mon.name}", description=text)
    embed.set_thumbnail(url=mon.icon)
    embed.set_footer(text=f"{loading}{footer_text}", icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    message = await ctx.send(embed=embed)

    shiny_count = await queries.get_shiny_count(mon.id, area[0], timespan[0], timespan[1], config)

    if shiny_count > 0:
        shiny_total = await queries.get_shiny_total(mon.id, area[0], timespan[0], timespan[1], config)
        shiny_odds = int(round((shiny_total / shiny_count), 0))
        text = text + f"{locale['shinies']}: **1:{shiny_odds}** ({shiny_count:_}/{shiny_total:_})\n"
    else:
        text = text + f"{locale['shinies']}: **0**\n"

    embed.description = text.replace("_", locale['decimal_comma']) 
    await message.edit(embed=embed)

    print(f"     [1/3] Shiny Data for {mon.name} Stats")

    scan_numbers = await queries.get_scan_numbers(mon.id, area[0], timespan[0], timespan[1], config)
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

    big_numbers = await queries.get_big_numbers(mon.id, area[0], timespan[0], timespan[1], config)
    for mons, found, boosted, time in big_numbers:
        mon_total = int(mons)
        if found is not None:
            found_count = int(found)
            boosted_count = int(boosted)
        else:
            found_count = 0
            boosted_count = 0

    days = (timespan[1].date() - (big_numbers[0][3]).date()).days
    if days < 1:
        days = 1

    if found_count > 0:
        mon_odds = int(round((mon_total / found_count), 0))
        mon_rate = str(round((found_count / days), 1)).replace(".", locale['decimal_dot'])

        text = text.replace(f"\n{locale['90']}", f"{locale['rarity']}: **1:{mon_odds}**\n{locale['rate']}: **{mon_rate}/{locale['day']}**\n\n{locale['90']}")

        boosted_odds = str(round((boosted_count / found_count * 100), 1)).replace(".", locale['decimal_dot'])
        text = text + f"{locale['weatherboost']}: **{boosted_odds}%**\n"

        scanned_odds = str(round((scanned_total / found_count * 100), 1)).replace(".", locale['decimal_dot'])
        text = text + f"{locale['scanned']}: **{scanned_odds}%**\n\n"

        text = text + f"{locale['total_found']}: **{found_count:_}**"
    else:
        text = text.replace(f"\n{locale['90']}", f"{locale['rarity']}: **0**\n{locale['rate']}: **0/{locale['day']}**\n\n{locale['90']}")
        text = text + f"{locale['weatherboost']}: **0%**\n{locale['scanned']}: **0**\n\n{locale['total_found']}: **0**"

    embed.description = text.replace("_", locale['decimal_comma'])
    embed.set_footer(text=footer_text)
    await message.edit(embed=embed)

    print(f"     [3/3] Total Data for {mon.name} Stats")
    print(f"Done with {mon.name} Stats.")

@bot.command(pass_context=True, aliases=config['gyms_aliases'])
async def gyms(ctx, areaname = ""):
    footer_text = ""
    text = ""
    loading = locale['loading_gym_stats']

    area = get_area(areaname)
    if not area[1] == locale['all']:
        footer_text = area[1]
        loading = f"{loading} • {footer_text}"

    print(f"@{ctx.author.name} requested gym stats for area {area[1]}")

    embed = discord.Embed(title=locale['gym_stats'], description=text)
    embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    message = await ctx.send(embed=embed)

    gym_stats = await queries.get_gym_stats(config, area[0])

    for total, neutral, mystic, valor, instinct, ex, raids in gym_stats:
        total_count = int(total)
        white_count = int(neutral)
        blue_count = int(mystic)
        red_count = int(valor)
        yellow_count = int(instinct)
        ex_count = int(ex)
        raid_count = int(raids)

    if total_count > 0:
        ex_odds = str(int(round((ex_count / total_count * 100), 0))).replace(".", locale['decimal_dot'])

    text = f"{bot.custom_emotes['gym_blue']}**{blue_count}**{bot.custom_emotes['blank']}{bot.custom_emotes['gym_red']}**{red_count}**{bot.custom_emotes['blank']}{bot.custom_emotes['gym_yellow']}**{yellow_count}**\n\n{locale['total']}: **{total_count}**\n{bot.custom_emotes['ex_pass']} {locale['ex_gyms']}: **{ex_count}** ({ex_odds}%)\n\n{bot.custom_emotes['raid']} {locale['active_raids']}: **{raid_count}**"

    embed.description=text
    await message.edit(embed=embed)

    # Pie chart
    sizes = [white_count, blue_count, red_count, yellow_count]
    colors = ['lightgrey', '#42a5f5', '#ef5350', '#fdd835']
    plt.pie(sizes, labels=None, colors=colors, autopct='', startangle=120, wedgeprops={"edgecolor":"black", 'linewidth':5, 'linestyle': 'solid', 'antialiased': True})
    plt.axis('equal')
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    plt.margins(0,0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig('gym_stats.png', transparent=True, bbox_inches = 'tight', pad_inches = 0)

    channel = await bot.fetch_channel(config['host_channel'])
    image_msg = await channel.send(file=discord.File("gym_stats.png"))
    image = image_msg.attachments[0].url

    embed.set_footer(text="")
    embed.description=text
    embed.set_thumbnail(url=image)
    embed.set_footer(text=footer_text)
    await message.edit(embed=embed)
    os.remove("gym_stats.png")
    print("Done with Gym Stats")

@bot.event
async def on_ready():
    print("Connected to Discord. Ready to take commands.")
    bot.loop.create_task(board_loop())
    bot.loop.create_task(raid_channels())

bot.run(config['bot_token'])
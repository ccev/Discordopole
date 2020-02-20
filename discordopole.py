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
from discord.ext import commands

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
                    for start, end, lat, lon, mon_id, move_1, move_2, name, ex, level in islice(raids, 21):
                        end = datetime.fromtimestamp(end).strftime(locale['time_format_hm'])
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
                            text = text + f"{ex_emote}**{name}**: {locale['until']} {end}\n**{mon_name}** - *{move_1} / {move_2}*\n\n"
                    
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
                    for start, end, lat, lon, mon_id, move_1, move_2, name, ex, level in islice(raids, 23):
                        start = datetime.fromtimestamp(start).strftime(locale['time_format_hm'])
                        end = datetime.fromtimestamp(end).strftime(locale['time_format_hm'])
                        ex_emote = ""
                        if ex == 1:
                            ex_emote = f"{bot.custom_emotes['ex_pass']} "
                        if mon_id is None or mon_id == 0:
                            egg_emote = bot.custom_emotes[f"raid_egg_{level}"]
                            text = text + f"{egg_emote} {ex_emote}**{name}**: {start}  –  {end}\n"
                    
                embed = discord.Embed(title=locale['eggs'], description=text, timestamp=datetime.utcnow())
                embed.set_footer(text=area[1])

                await message.edit(embed=embed)
                await asyncio.sleep(board["wait"])
            except Exception as err:
                print(err)
                print("Error while updating Egg Board. Skipping it.")
                await asyncio.sleep(5)
        
        await asyncio.sleep(1)

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

@board.command(pass_context=True)
async def delete(ctx, deleted_message_id):
    if not ctx.message.author.id in config['admins']:
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
        return

    needed_emote_names = ["ex_pass", "raid_egg_1", "raid_egg_2", "raid_egg_3", "raid_egg_4", "raid_egg_5", "gym_blue", "gym_red", "gym_yellow", "blank", "raid"]
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
        return
    await confirm.delete()
    embed = discord.Embed(title="Importing Emotes. Please Wait", description="")
    await message.edit(embed=embed)
    existing_emotes = await ctx.guild.fetch_emojis()
    for emote in existing_emotes:
        await emote.delete()
        embed.description = f"{embed.description}Removed Emote `{emote.name}`\n"
        await message.edit(embed=embed)
    embed.description = ""

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

@bot.command(pass_context=True, aliases=config['pokemon_aliases'])
async def pokemon(ctx, stat_name, areaname = "", *, timespan = None):
    mon = details(stat_name, config['mon_icon_repo'], config['language'])
    print(f"Generating {mon.name} Stats...")

    footer_text = ""
    text = ""
    loading = f"{locale['loading']} {mon.name} Stats"

    area = get_area(areaname)
    if not area[1] == locale['all']:
        footer_text = area[1]
        loading = f"{loading} • "
    if timespan is None:
        timespan = datetime(2010, 1, 1, 0, 0)
    else:
        timespan = dateparser.parse(timespan)
        loading = ""
        if area[1] == locale['all']:
            footer_text = f"{(locale['since']).capitalize()} {timespan.strftime(locale['time_format_dhm'])}"
        else:
            footer_text = f"{footer_text}, {locale['since']} {timespan.strftime(locale['time_format_dhm'])}"
        


    embed = discord.Embed(title=f"{mon.name}", description=text)
    embed.set_thumbnail(url=mon.icon)
    embed.set_footer(text=f"{loading}{footer_text}", icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    message = await ctx.send(embed=embed)

    shiny_count = await queries.get_shiny_count(mon.id, area[0], timespan, config)

    if shiny_count > 0:
        shiny_total = await queries.get_shiny_total(mon.id, area[0], timespan, config)
        shiny_odds = int(round((shiny_total / shiny_count), 0))
        text = text + f"{locale['shinies']}: **1:{shiny_odds}** ({shiny_count:_}/{shiny_total:_})\n"
    else:
        text = text + f"{locale['shinies']}: **0**\n"

    embed.description = text.replace("_", locale['decimal_comma']) 
    await message.edit(embed=embed)

    print(f"     [1/3] Shiny Data for {mon.name} Stats")

    scan_numbers = await queries.get_scan_numbers(mon.id, area[0], timespan, config)
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

    big_numbers = await queries.get_big_numbers(mon.id, area[0], timespan, config)
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

@bot.event
async def on_ready():
    print("Connected to Discord. Ready to take commands.")
    bot.loop.create_task(board_loop())

bot.run(config['bot_token'])
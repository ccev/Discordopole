import discord
import json
import asyncio
import os
import dateparser
from dateparser.search import search_dates

import matplotlib.pyplot as plt
import pyshorteners

from datetime import datetime, date
from discord.ext import commands

from util.mondetails import details
from cogs.admin import Admin
import util.queries as queries
import util.config
import util.maps

extensions = ["cogs.admin", "cogs.boards", "cogs.channels"]
activity = discord.Activity(type=discord.ActivityType.watching, name="Discordopole: Online")
intents = discord.Intents.default()
intents.message_content = True
config = util.config.create_config("config/config.ini")
bot = commands.Bot(command_prefix=config['prefix'], case_insensitive=1, intents=intents, activity=activity, status=discord.Status.online)
bot.max_moves_in_list = 348
bot.config = config
short = pyshorteners.Shortener().tinyurl.short

if bot.config['use_map']:
    bot.map_url = util.maps.map_url(config['map'], config['map_url'])

if not os.path.exists("data/raid_cache.json"):
    f = open("data/raid_cache.json", 'w+')
    f.write("{}")
    f.close()

### LANG FILES

dts_lang = bot.config['language']
if not bot.config['language'] in ["en", "de", "fr", "es", "pl"]:
    dts_lang = "en"

with open(f"data/dts/{dts_lang}.json", encoding="utf-8") as f:
    bot.locale = json.load(f)

move_lang = bot.config['language']
if not bot.config['language'] in ["en", "de", "fr", "es"]:
    move_lang = "en"

with open(f"data/moves/{move_lang}.json", encoding="utf-8") as f:
    bot.moves = json.load(f)

form_lang = bot.config['language']
if not bot.config['language'] in ["en", "de", "fr", "es"]:
    form_lang = "en"

with open(f"data/forms/{form_lang}.json", encoding="utf-8") as f:
    bot.forms = json.load(f)

item_lang = bot.config['language']
if not bot.config['language'] in ["en", "de", "fr", "es"]:
    item_lang = "en"

with open(f"data/items/{item_lang}.json", encoding="utf-8") as f:
    bot.items = json.load(f)

### LANG FILES STOP

with open("config/boards.json", "r", encoding="utf-8") as f:
    bot.boards = json.load(f)

with open("config/geofence.json", encoding="utf-8") as f:
    bot.geofences = json.load(f)

with open("config/emotes.json", encoding="utf-8") as f:
    bot.custom_emotes = json.load(f)

with open(f"data/raidcp.json", encoding="utf-8") as f:
    bot.raidcp = json.load(f)

def get_area(areaname):
    stringfence = "-1 -1, -1 1, 1 1, 1 -1, -1 -1"
    namefence = bot.locale['unknown']
    for area in bot.geofences:
        if area['name'].lower() == areaname.lower():
            namefence = area['name'].title()
            stringfence = ""
            for coordinates in area['path']:
                stringfence = f"{stringfence}{coordinates[0]} {coordinates[1]},"
            stringfence = f"{stringfence}{area['path'][0][0]} {area['path'][0][1]}"
    area_list = [stringfence, namefence]
    return area_list

def isUser(role_ids, channel_id):
    if len(bot.config["cmd_roles"][0]) + len(bot.config["cmd_channels"][0]) == 0:
        return True
    elif str(channel_id) in bot.config["cmd_channels"]:
        return True
    else:
        for role in role_ids:
            if str(role.id) in bot.config["cmd_roles"]:
                return True
        return False

@bot.command(pass_context=True, aliases=bot.config['pokemon_aliases'])
async def pokemon(ctx, stat_name, areaname = "", *, timespan = None, alt_timespan = None):
    if not isUser(ctx.author.roles, ctx.channel.id):
        print(f"@{ctx.author.name} tried to use !pokemon but is no user")
        return
    mon = details(stat_name, bot.config['mon_icon_repo'], bot.config['language'])
    footer_text = ""
    text = ""
    loading = f"{bot.locale['loading']} {mon.name} Stats"

    area = get_area(areaname)

    if not area[1] == bot.locale['all'] and not config['timespan_in_footer']:
        footer_text = area[1]
        loading = f"{loading} • "
    elif config['timespan_in_footer']:
        footer_text = area[1]
        loading = f"{loading}"

    if dateparser.search.search_dates(areaname, languages=[bot.config['language']]) is not None: #check for dates in areaname
        if dateparser.search.search_dates(f"{timespan}", languages=[bot.config['language']]) is not None: #check for dates in everything after areaname
            timespan = f"{areaname} {timespan}"
        else: 
            timespan = areaname
    elif dateparser.search.search_dates(f"{areaname} {timespan}", languages=[bot.config['language']]) is not None and (dateparser.search.search_dates(timespan, languages=[bot.config['language']]) is None):
        timespan = f"{areaname} {timespan}"

    print(f"timespan found in command: {timespan}")
    if config['timespan_in_footer']:
        if config['use_alt_table_for_pokemon']:
            oldest_mon_date = await queries.get_oldest_mon_date(bot.config, use_alt_table=True)
            if oldest_mon_date is None:
                oldest_mon_date = await queries.get_oldest_mon_date(bot.config, use_alt_table=False)
        else:
            oldest_mon_date = await queries.get_oldest_mon_date(bot.config, use_alt_table=False)

        if timespan is None:
            timespan = list([oldest_mon_date, datetime.now()])
        elif "-" in timespan:
            timespan = list(timespan.split('-'))
            for i in [0, 1]:
                timespan[i] = dateparser.parse(timespan[i], languages=[bot.config['language']])
        else:
            timespan = list([dateparser.parse(timespan, languages=[bot.config['language']]), datetime.now()])

        if timespan[0] < oldest_mon_date:
            timespan = list([oldest_mon_date, timespan[1]])

        footer_text = f"{footer_text}, {(bot.locale['between'])} {timespan[0].strftime(bot.locale['time_format_dhm'])} {bot.locale['and']} {timespan[1].strftime(bot.locale['time_format_dhm'])}"
    else:
        if timespan is None:
            timespan = list([datetime(2010, 1, 1, 0, 0), datetime.now()])
        else:
            loading = ""

            if "-" in timespan:
                timespan = list(timespan.split('-'))
                for i in [0, 1]:
                    timespan[i] = dateparser.parse(timespan[i], languages=[bot.config['language']])

                footer_text = f"{(bot.locale['between']).capitalize()} {timespan[0].strftime(bot.locale['time_format_dhm'])} {bot.locale['and']} {timespan[1].strftime(bot.locale['time_format_dhm'])}"

            else:
                timespan = list([dateparser.parse(timespan, languages=[bot.config['language']]), datetime.now()])

                if area[1] == bot.locale['all']:
                    footer_text = f"{(bot.locale['since']).capitalize()} {timespan[0].strftime(bot.locale['time_format_dhm'])}"
                else:
                    footer_text = f"{footer_text}, {bot.locale['since']} {timespan[0].strftime(bot.locale['time_format_dhm'])}"

    print(f"@{ctx.author.name} requested {mon.name} stats for area {area[1]}")    

    embed = discord.Embed(title=f"{mon.name}", description=text)
    embed.set_thumbnail(url=mon.icon)
    if config['timespan_in_footer']:
        embed.set_footer(text=f"{loading}", icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    else:
        embed.set_footer(text=f"{loading}{footer_text}", icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    message = await ctx.send(embed=embed)
   
    alt_shiny_count = 0
    alt_shiny_total = 0
    alt_scan_numbers = ((0, 0, 0, 0),)
    alt_big_numbers = ((0, 0, 0, datetime.now()),)
    if bot.config['use_alt_table_for_pokemon']:
        oldest_mon_date = await queries.get_oldest_mon_date(bot.config)
        if oldest_mon_date > timespan[0]:
            print(f"using alt table, because starttime older than oldest mon. starttime: {timespan[0]}, oldest mon: {oldest_mon_date}\n")
            if oldest_mon_date > timespan[1]:
                alt_timespan = list([timespan[0], timespan[1]])
            else:
                alt_timespan = list([timespan[0], oldest_mon_date])
                timespan = list([oldest_mon_date, timespan[1]])
            alt_shiny_count = await queries.get_shiny_count(mon.id, area[0], alt_timespan[0], alt_timespan[1], bot.config, use_alt_table=True)
            alt_shiny_total = await queries.get_shiny_total(mon.id, area[0], alt_timespan[0], alt_timespan[1], bot.config, use_alt_table=True)
            alt_scan_numbers = await queries.get_scan_numbers(mon.id, area[0], alt_timespan[0], alt_timespan[1], bot.config, use_alt_table=True)
            alt_big_numbers = await queries.get_big_numbers(mon.id, area[0], alt_timespan[0], alt_timespan[1], bot.config, use_alt_table=True)
            if alt_big_numbers[0][3] is None:
                alt_big_numbers = ((alt_big_numbers[0][0], alt_big_numbers[0][1], alt_big_numbers[0][2], oldest_mon_date),)

    shiny_count = await queries.get_shiny_count(mon.id, area[0], timespan[0], timespan[1], bot.config)
    shiny_count = shiny_count + alt_shiny_count

    if shiny_count > 0:
        shiny_total = await queries.get_shiny_total(mon.id, area[0], timespan[0], timespan[1], bot.config)
        shiny_total = shiny_total + alt_shiny_total
        shiny_odds = int(round((shiny_total / shiny_count), 0))
        text = text + f"{bot.locale['shinies']}: **1:{shiny_odds}** ({shiny_count:_}/{shiny_total:_})\n"
    else:
        text = text + f"{bot.locale['shinies']}: **0**\n"

    embed.description = text.replace("_", bot.locale['decimal_comma']) 
    await message.edit(embed=embed)

    print(f"     [1/3] Shiny Data for {mon.name} Stats")

    scan_numbers = await queries.get_scan_numbers(mon.id, area[0], timespan[0], timespan[1], bot.config)
    for scanned, hundos, zeros, nineties in scan_numbers:
        scanned_total = int(scanned) + int(alt_scan_numbers[0][0])
        if scanned_total > 0:
            hundo_count = int(hundos) + int(alt_scan_numbers[0][1])
            zero_count = int(zeros) + int(alt_scan_numbers[0][2])
            ninety_count = int(nineties) + int(alt_scan_numbers[0][3])
        else:
            hundo_count = 0
            zero_count = 0
            ninety_count = 0

    if hundo_count > 0:
        hundo_odds = int(round((scanned_total / hundo_count), 0))
        text = text + f"{bot.locale['hundos']}: **{hundo_count:_}** (1:{hundo_odds})\n\n"
    else:
        text = text + f"{bot.locale['hundos']}: **0/{scanned_total:_}**\n\n"


    if ninety_count > 0:
        ninety_odds = round((scanned_total / ninety_count), 0)
        text = text + f"{bot.locale['90']}: **{ninety_count:_}** (1:{int(ninety_odds)}) | "
    else:
        text = text + f"{bot.locale['90']}: **0** | "

    if zero_count > 0:
        zero_odds = round((scanned_total / zero_count), 0)
        text = text + f"{bot.locale['0']}: **{zero_count:_}** (1:{int(zero_odds)})\n"
    else:
        text = text + f"{bot.locale['0']}: **0**\n"

    embed.description = text.replace("_", bot.locale['decimal_comma']) 
    await message.edit(embed=embed)

    print(f"     [2/3] Scan Data for {mon.name} Stats")

    big_numbers = await queries.get_big_numbers(mon.id, area[0], timespan[0], timespan[1], bot.config)
    for mons, found, boosted, time in big_numbers:
        mon_total = int(mons) + int(alt_big_numbers[0][0])
        found_count = int(found) + int(alt_big_numbers[0][1])
        boosted_count = int(boosted) + int(alt_big_numbers[0][2])
    
    if found_count > 0:
        if big_numbers[0][3] is None:
            days = (alt_timespan[1].date() - (alt_big_numbers[0][3]).date()).days
        elif alt_big_numbers[0][3] < big_numbers[0][3]:
            days = (timespan[1].date() - (alt_big_numbers[0][3]).date()).days
        else:
            days = (timespan[1].date() - (big_numbers[0][3]).date()).days

        if days < 1:
            days = 1

        mon_odds = int(round((mon_total / found_count), 0))
        mon_rate = str(round((found_count / days), 1)).replace(".", bot.locale['decimal_dot'])

        text = text.replace(f"\n{bot.locale['90']}", f"{bot.locale['rarity']}: **1:{mon_odds}**\n{bot.locale['rate']}: **{mon_rate}/{bot.locale['day']}**\n\n{bot.locale['90']}")

        boosted_odds = str(round((boosted_count / found_count * 100), 1)).replace(".", bot.locale['decimal_dot'])
        text = text + f"{bot.locale['weatherboost']}: **{boosted_odds}%**\n"

        scanned_odds = str(round((scanned_total / found_count * 100), 1)).replace(".", bot.locale['decimal_dot'])
        text = text + f"{bot.locale['scanned']}: **{scanned_odds}%**\n\n"

        text = text + f"{bot.locale['total_found']}: **{found_count:_}**"
    else:
        text = text.replace(f"\n{bot.locale['90']}", f"{bot.locale['rarity']}: **0**\n{bot.locale['rate']}: **0/{bot.locale['day']}**\n\n{bot.locale['90']}")
        text = text + f"{bot.locale['weatherboost']}: **0%**\n{bot.locale['scanned']}: **0**\n\n{bot.locale['total_found']}: **0**"

    embed.description = text.replace("_", bot.locale['decimal_comma'])
    embed.set_footer(text=footer_text)
    await message.edit(embed=embed)

    print(f"     [3/3] Total Data for {mon.name} Stats")
    print(f"Done with {mon.name} Stats.")

@bot.command(pass_context=True, aliases=bot.config['gyms_aliases'])
async def gyms(ctx, areaname = ""):
    if not isUser(ctx.author.roles, ctx.channel.id):
        print(f"@{ctx.author.name} tried to use !gyms but is no user")
        return
    footer_text = ""
    text = ""
    loading = bot.locale['loading_gym_stats']

    area = get_area(areaname)
    if not area[1] == bot.locale['all']:
        footer_text = area[1]
        loading = f"{loading} • {footer_text}"

    print(f"@{ctx.author.name} requested gym stats for area {area[1]}")

    embed = discord.Embed(title=bot.locale['gym_stats'], description=text)
    embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    message = await ctx.send(embed=embed)

    gym_stats = await queries.get_gym_stats(bot.config, area[0])

    for total, neutral, mystic, valor, instinct, ex, raids in gym_stats:
        total_count = int(total)
        white_count = int(neutral)
        blue_count = int(mystic)
        red_count = int(valor)
        yellow_count = int(instinct)
        ex_count = int(ex)
        raid_count = int(raids)

    if total_count > 0:
        ex_odds = str(int(round((ex_count / total_count * 100), 0))).replace(".", bot.locale['decimal_dot'])
    else:
	    ex_odds = 0

    text = f"{bot.custom_emotes['gym_blue']}**{blue_count}**{bot.custom_emotes['blank']}{bot.custom_emotes['gym_red']}**{red_count}**{bot.custom_emotes['blank']}{bot.custom_emotes['gym_yellow']}**{yellow_count}**\n\n{bot.locale['total']}: **{total_count}**\n{bot.custom_emotes['ex_pass']} {bot.locale['ex_gyms']}: **{ex_count}** ({ex_odds}%)\n\n{bot.custom_emotes['raid']} {bot.locale['active_raids']}: **{raid_count}**"

    embed.description=text
    await message.edit(embed=embed)

    # Pie chart
    sizes = [white_count, blue_count, red_count, yellow_count]
    colors = ['lightgrey', '#42a5f5', '#ef5350', '#fdd835']
    plt.pie(sizes, labels=None, colors=colors, autopct='', startangle=120, wedgeprops={"edgecolor":"black", 'linewidth':5, 'linestyle': 'solid', 'antialiased': True})
    plt.axis('equal')
    plt.gca().set_axis_off()
    #plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    plt.margins(0.01)
    #plt.gca().xaxis.set_major_locator(plt.NullLocator())
    #plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig('gym_stats.png', transparent=True, bbox_inches = 'tight', pad_inches = 0)

    channel = await bot.fetch_channel(bot.config['host_channel'])
    image_msg = await channel.send(file=discord.File("gym_stats.png"))
    image = image_msg.attachments[0].url

    embed.set_footer(text="")
    embed.description=text
    embed.set_thumbnail(url=image)
    embed.set_footer(text=footer_text)
    await message.edit(embed=embed)
    os.remove("gym_stats.png")
    print("Done with Gym Stats")

@bot.command(pass_context=True, aliases=bot.config['quest_aliases'])
async def quest(ctx, areaname = "", *, reward):
    if not isUser(ctx.author.roles, ctx.channel.id):
        print(f"@{ctx.author.name} tried to use !quest but is no user")
        return
    footer_text = ""
    text = ""
    loading = bot.locale['loading_quests']

    area = get_area(areaname)
    if not area[1] == bot.locale['all']:
        footer_text = area[1]
        loading = f"{loading} • {footer_text}"

    print(f"@{ctx.author.name} requested {reward} quests for area {area[1]}")

    if area[1] == "Unknown Area":
        embed = discord.Embed(title=bot.locale['no_area_found'], description=text)
    elif reward.startswith("Mega") or reward.startswith("mega"):
        embed = discord.Embed(title=bot.locale['mega'], description=text)
        embed.set_image(url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
        embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    elif reward == "Stardust":
        embed = discord.Embed(title=bot.locale['quests'], description=text)
        embed.set_image(url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
        embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    elif reward == "stardust":
        embed = discord.Embed(title=bot.locale['quests'], description=text)
        embed.set_image(url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
        embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    elif reward == "Kecleon":
        embed = discord.Embed(title=bot.locale['eventstop'], description=text)
        embed.set_image(url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
        embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    elif reward == "kecleon":
        embed = discord.Embed(title=bot.locale['eventstop'], description=text)
        embed.set_image(url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
        embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    elif reward == "keckleon":
        embed = discord.Embed(title=bot.locale['eventstop'], description=text)
        embed.set_image(url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
        embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    elif reward == "Keckleon":
        embed = discord.Embed(title=bot.locale['eventstop'], description=text)
        embed.set_image(url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
        embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    elif reward == "Coins":
        embed = discord.Embed(title=bot.locale['eventstop'], description=text)
        embed.set_image(url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
        embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    elif reward == "coins":
        embed = discord.Embed(title=bot.locale['eventstop'], description=text)
        embed.set_image(url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
        embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    else:
        embed = discord.Embed(title=bot.locale['quests'], description=text)
        embed.set_image(url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
        embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    message = await ctx.send(embed=embed)

    items = list()
    mons = list()
    item_found = False
    for item_id in bot.items:
        if area[1] == "Unknown Area":
            footer_text = area[1]
            loading = f"{footer_text}"
            embed.description = bot.locale["no_area_found"]
            item_found = True
        elif bot.items[item_id]["name"].lower() == reward.lower():
            embed.set_thumbnail(url=f"{bot.config['mon_icon_repo']}reward/item/{item_id}.png")
            embed.title = f"{bot.items[item_id]['name']} {bot.locale['quests']} - {area[1]}"
            items.append(int(item_id))
            item_found = True
            quests = await queries.get_dataitem(bot.config, area[0], item_id)
            quests2 = await queries.get_alt_dataitem(bot.config, area[0], item_id)
    if not item_found:
        mon = details(reward, bot.config['mon_icon_repo'], bot.config['language'])
        if reward.startswith("Mega") or reward.startswith("mega"):
            embed.title = f"{mon.name} {bot.locale['mega']} - {area[1]}"
            embed.set_thumbnail(url=f"{bot.config['mon_icon_repo']}reward/mega_resource/{str(mon.id)}.png")
            quests = await queries.get_datamega(bot.config, area[0])
            quests2 = await queries.get_alt_datamega(bot.config, area[0])
        elif mon.name == "Kecleon":
            embed.title = f"{mon.name} {bot.locale['eventstop']} - {area[1]}"
            embed.set_thumbnail(url=f"{bot.config['mon_icon_repo']}pokemon/{str(mon.id)}.png")
            quests = await queries.get_datak(bot.config, area[0])
        elif mon.name == "Coins":
            embed.title = f"{mon.name} {bot.locale['eventstop']} - {area[1]}"
            embed.set_thumbnail(url=f"{bot.config['mon_icon_repo']}misc/event_coin.png")
            quests = await queries.get_datacoin(bot.config, area[0])
        elif mon.name == "Stardust":
            embed.title = f"{mon.name} {bot.locale['quests']} - {area[1]}"
            embed.set_thumbnail(url=f"{bot.config['mon_icon_repo']}reward/stardust/0.png")
            quests = await queries.get_datastar(bot.config, area[0])
            quests2 = await queries.get_alt_datastar(bot.config, area[0])
        else:
            embed.title = f"{mon.name} {bot.locale['quests']} - {area[1]}"
            embed.set_thumbnail(url=f"{bot.config['mon_icon_repo']}pokemon/{str(mon.id)}.png")
            quests = await queries.get_data(bot.config, area[0], mon.id)
            quests2 = await queries.get_alt_data(bot.config, area[0], mon.id)
        mons.append(mon.id)
    
    length = 0
    reward_mons = list()
    reward_items = list()
    lat_list = list()
    lon_list = list()

    embed.description = text
    if not item_found and mon.name == "Kecleon":
        for lat, lon, stop_name, stop_id, expiration in quests:
            end = datetime.fromtimestamp(expiration).strftime(bot.locale['time_format_hm'])
            found_rewards = True
            mon_id = 352
            reward_mons.append([mon_id, lat, lon])
            emote_name = f"m{mon_id}"
            emote_img = f"{bot.config['mon_icon_repo']}pokemon/{str(mon.id)}.png"
    
            if found_rewards:
                if len(stop_name)+len(end) >= 26:
                    stop_name = stop_name[0:25]
                lat_list.append(lat)
                lon_list.append(lon)

                if bot.config['use_map']:
                    map_url = bot.map_url.quest(lat, lon, stop_id)
                else:
                    map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

                entry = f"[{stop_name} **{end}**]({map_url})\n"
                if length + len(entry) >= 2400:
                    theend = f"and more..."
                    text = text + theend
                    break
                else:
                    text = text + entry
                    length = length + len(entry)
    elif not item_found and mon.name == "Coins":
        for lat, lon, stop_name, stop_id, expiration in quests:
            end = datetime.fromtimestamp(expiration).strftime(bot.locale['time_format_hm'])
            found_rewards = True
            mon_id = 99999
            reward_mons.append([mon_id, lat, lon])
            emote_name = f"m{mon_id}"
            emote_img = f"{bot.config['mon_icon_repo']}misc/event_coin.png"
    
            if found_rewards:
                if len(stop_name)+len(end) >= 26:
                    stop_name = stop_name[0:25]
                lat_list.append(lat)
                lon_list.append(lon)

                if bot.config['use_map']:
                    map_url = bot.map_url.quest(lat, lon, stop_id)
                else:
                    map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

                entry = f"[{stop_name} **{end}**]({map_url})\n"
                if length + len(entry) >= 2400:
                    theend = f"and more..."
                    text = text + theend
                    break
                else:
                    text = text + entry
                    length = length + len(entry)
    elif not item_found and mon.name == "Stardust":
        for quest_reward_amount, quest_text, lat, lon, stop_name, stop_id in quests:
            found_rewards = True
            amount = quest_reward_amount
            mon_id = 99998
            reward_mons.append([mon_id, lat, lon])
            emote_name = f"s{amount}"
            emote_img = f"{bot.config['mon_icon_repo']}reward/stardust/0.png"
            if found_rewards:
                if len(stop_name) >= 31:
                    stop_name = stop_name[0:30]
                lat_list.append(lat)
                lon_list.append(lon)

                if bot.config['use_map']:
                    map_url = bot.map_url.quest(lat, lon, stop_id)
                else:
                    map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

                entry = f"[{stop_name} **{amount}**]({map_url})\n"
                if length + len(entry) >= 2400:
                    theend = f"and more..."
                    text = text + theend
                    break
                else:
                    text = text + entry
                    length = length + len(entry)
        for alternative_quest_reward_amount, alternative_quest_text, lat, lon, stop_name, stop_id in quests2:
            found_rewards = True
            amount = alternative_quest_reward_amount
            mon_id = 99998
            reward_mons.append([mon_id, lat, lon])
            emote_name = f"s{amount}"
            emote_img = f"{bot.config['mon_icon_repo']}reward/stardust/0.png"
            if found_rewards:
                if len(stop_name) >= 22:
                    stop_name = stop_name[0:21]
                lat_list.append(lat)
                lon_list.append(lon)

                if bot.config['use_map']:
                    map_url = bot.map_url.quest(lat, lon, stop_id)
                else:
                    map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

                entry = f"[{stop_name} **{amount}-NO AR**]({map_url})\n"
                if length + len(entry) >= 2400:
                    theend = f"lots more..."
                    text = text + theend
                    break
                else:
                    text = text + entry
                    length = length + len(entry)
    else:
        for quest_json, quest_text, lat, lon, stop_name, stop_id in quests:
            quest_json = json.loads(quest_json)
            found_rewards = True
            shiny = False
            mon_id = 0
            item_id = 0
            if 'pokemon_id' in quest_json[0]["info"]:
                    mon_id = quest_json[0]["info"]["pokemon_id"]
            if 'item_id' in quest_json[0]["info"]:
                    item_id = quest_json[0]["info"]["item_id"]
                    amount = quest_json[0]["info"]["amount"]
            if 'shiny' in quest_json[0]["info"]:
                    shiny = quest_json[0]["info"]["shiny"]
            if item_id in items:
                reward_items.append([item_id, lat, lon])
                emote_name = f"i{item_id}"
                emote_img = f"{bot.config['mon_icon_repo']}reward/item/{item_id}.png"
            elif mon_id in mons and reward.startswith("Mega") or mon_id in mons and reward.startswith("mega"):
                reward_items = 99997
                reward_mons.append([mon_id, lat, lon])
                emote_name = f"e{mon_id}"
                emote_img = f"{bot.config['mon_icon_repo']}reward/mega_resource/{str(mon.id)}.png"
            elif mon_id in mons and shiny:
                reward_mons.append([mon_id, lat, lon])
                emote_name = f"m{mon_id}"
                emote_img = f"{bot.config['mon_icon_repo']}pokemon/{str(mon.id)}_s.png"
            elif mon_id in mons:
                reward_mons.append([mon_id, lat, lon])
                emote_name = f"m{mon_id}"
                emote_img = f"{bot.config['mon_icon_repo']}pokemon/{str(mon.id)}.png"
            else:
                found_rewards = False
            if found_rewards:
                if len(stop_name) >= 31:
                    stop_name = stop_name[0:30]
                lat_list.append(lat)
                lon_list.append(lon)

                if bot.config['use_map']:
                    map_url = bot.map_url.quest(lat, lon, stop_id)
                else:
                    map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

                if item_id in items:
                    entry = f"[{stop_name} **{amount}**]({map_url})\n"
                elif shiny:
                    entry = f"[{stop_name} **SHINY**]({map_url})\n"
                    embed.set_thumbnail(url=f"{bot.config['mon_icon_repo']}pokemon/{str(mon.id)}_s.png")
                    embed.title = f"{mon.name} Quests SHINY DETECTED!! - {area[1]}"
                else:
                    entry = f"[{stop_name}]({map_url})\n"
                if length + len(entry) >= 2400:
                    if shiny:
                        text = entry + text
                        length = length + len(entry)
                    else:
                        theend = f" lots more ..."
                        text = text + theend
                        break
                else:
                    if shiny:
                        text = entry + text
                        length = length + len(entry)
                    else:
                        text = text + entry
                        length = length + len(entry)
        for alternative_quest_json, alternative_quest_text, lat, lon, stop_name, stop_id in quests2:
            quest_json = json.loads(alternative_quest_json)
            found_alt_rewards = True
            shiny = False
            mon_id = 0
            item_id = 0
            if 'pokemon_id' in quest_json[0]["info"]:
                    mon_id = quest_json[0]["info"]["pokemon_id"]
            if 'item_id' in quest_json[0]["info"]:
                    item_id = quest_json[0]["info"]["item_id"]
                    amount = quest_json[0]["info"]["amount"]
            if 'shiny' in quest_json[0]["info"]:
                    shiny = quest_json[0]["info"]["shiny"]
            if item_id in items:
                reward_items.append([item_id, lat, lon])
                emote_name = f"i{item_id}"
                emote_img = f"{bot.config['mon_icon_repo']}reward/item/{item_id}.png"
            elif mon_id in mons and reward.startswith("Mega") or mon_id in mons and reward.startswith("mega"):
                reward_items = 99997
                reward_mons.append([mon_id, lat, lon])
                emote_name = f"e{mon_id}"
                emote_img = f"{bot.config['mon_icon_repo']}reward/mega_resource/{str(mon.id)}.png"
            elif mon_id in mons and shiny:
                reward_mons.append([mon_id, lat, lon])
                emote_name = f"m{mon_id}"
                emote_img = f"{bot.config['mon_icon_repo']}pokemon/{str(mon.id)}_s.png"
            elif mon_id in mons:
                reward_mons.append([mon_id, lat, lon])
                emote_name = f"m{mon_id}"
                emote_img = f"{bot.config['mon_icon_repo']}pokemon/{str(mon.id)}.png"
            else:
                found_alt_rewards = False
            if found_alt_rewards:
                if len(stop_name) >= 26:
                    stop_name = stop_name[0:25]
                lat_list.append(lat)
                lon_list.append(lon)

                if bot.config['use_map']:
                    map_url = bot.map_url.quest(lat, lon, stop_id)
                else:
                    map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"

                if item_id in items:
                    entry = f"[{stop_name} **{amount}-NO AR**]({map_url})\n"
                elif shiny:
                    entry = f"[{stop_name} **SHINY-NO AR**]({map_url})\n"
                    embed.set_thumbnail(url=f"{bot.config['mon_icon_repo']}pokemon/{str(mon.id)}_s.png")
                    embed.title = f"{mon.name} Quests SHINY DETECTED!! - {area[1]}"
                else:
                    entry = f"[{stop_name} **NO AR**]({map_url})\n"
                if length + len(entry) >= 2400:
                    if shiny:
                        text = entry + text
                        length = length + len(entry)
                    else:
                        theend = f" lots more ..."
                        text = text + theend
                        break
                else:
                    if shiny:
                        text = entry + text
                        length = length + len(entry)
                    else:
                        text = text + entry
                        length = length + len(entry)
    embed.description = text
    image = "https://raw.githubusercontent.com/ccev/dp_emotes/master/blank.png"
    if length > 0:
        if bot.config['use_static']:
            if bot.config['static_provider'] == "mapbox":
                guild = await bot.fetch_guild(bot.config['host_server'])
                existing_emotes = await guild.fetch_emojis()
                emote_exist = False
                for existing_emote in existing_emotes:
                    if emote_name == existing_emote.name:
                        emote_exist = True
                if not emote_exist:
                    try:
                        image = await Admin.download_url("", emote_img)
                        emote = await guild.create_custom_emoji(name=emote_name, image=image)
                        emote_ref = f"<:{emote.name}:{emote.id}>"

                        if emote_name in bot.custom_emotes:
                            bot.custom_emotes[emote_name] = emote_ref
                        else:
                            bot.custom_emotes.update({emote_name: emote_ref})
                    except Exception as err:
                        print(err)
                        print(f"Error while importing emote {emote_name}")

                image = await bot.static_map.quest(lat_list, lon_list, reward_items, reward_mons, bot.custom_emotes)

                if not emote_exist:
                    await emote.delete()
                    bot.custom_emotes.pop(emote_name)

            elif bot.config['static_provider'] == "tileserver":
                image = await bot.static_map.quest(lat_list, lon_list, reward_items, reward_mons, bot.custom_emotes)
    else:
        embed.description = bot.locale["no_quests_found"]

    embed.set_footer(text=footer_text)
    embed.set_image(url=image)

    await message.edit(embed=embed)
    await asyncio.sleep(2)

@bot.event
async def on_ready():
    for extension in extensions:
        await bot.load_extension(extension)
    if bot.config['use_static']:
        trash_channel = await bot.fetch_channel(bot.config['host_channel'])
        bot.static_map = util.maps.static_map(config['static_provider'], config['static_key'], trash_channel, bot.config['mon_icon_repo'])
    print("Connected to Discord. Ready to take commands.")

if __name__ == '__main__':
    bot.run(bot.config['bot_token'])
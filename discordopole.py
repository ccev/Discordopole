import discord
import json
import asyncio
import os
import dateparser
import matplotlib.pyplot as plt
import pyshorteners
import urllib.request

from datetime import datetime, date
from discord.ext import commands

from util.mondetails import details
import util.queries as queries
import util.config
import util.maps

#extensions = ["cogs.admin", "cogs.boards", "cogs.channels", "cogs.misc", "cogs.stats"]
extensions = ["cogs.admin", "cogs.boards", "cogs.channels"]

config = util.config.create_config("config/config.ini")
bot = commands.Bot(command_prefix=config['prefix'], case_insensitive=1)
bot.max_moves_in_list = 291
bot.config = config
short = pyshorteners.Shortener().tinyurl.short

if bot.config['use_static']:
    bot.static_map = util.maps.static_map(config['static_provider'], config['static_key'])

if bot.config['use_map']:
    bot.map_url = util.maps.map_url(config['map'], config['map_url'])

if not os.path.exists("data/raid_cache.json"):
    f = open("data/raid_cache.json", 'w+')
    f.write("{}")
    f.close()

with open(f"data/dts/{bot.config['language']}.json") as localejson:
    bot.locale = json.load(localejson)

with open("config/boards.json", "r") as f:
    bot.boards = json.load(f)

with open(f"data/moves/{bot.config['language']}.json") as f:
    bot.moves = json.load(f)

with open("config/geofence.json") as f:
    bot.geofences = json.load(f)

with open("config/emotes.json") as f:
    bot.custom_emotes = json.load(f)

with open(f"data/forms/{bot.config['language']}.json") as f:
    bot.forms = json.load(f)

with open(f"data/raidcp.json") as f:
    bot.raidcp = json.load(f)

with open(f"data/items/{bot.config['language']}.json") as f:
    bot.items = json.load(f)

def get_area(areaname):
    stringfence = "-100 -100, -100 100, 100 100, 100 -100, -100 -100"
    namefence = bot.locale['all']
    for area in bot.geofences:
        if area['name'].lower() == areaname.lower():
            namefence = area['name'].capitalize()
            stringfence = ""
            for coordinates in area['path']:
                stringfence = f"{stringfence}{coordinates[0]} {coordinates[1]},"
            stringfence = f"{stringfence}{area['path'][0][0]} {area['path'][0][1]}"
    area_list = [stringfence, namefence]
    return area_list

@bot.command(pass_context=True, aliases=bot.config['pokemon_aliases'])
async def pokemon(ctx, stat_name, areaname = "", *, timespan = None):
    mon = details(stat_name, bot.config['mon_icon_repo'], bot.config['language'])

    footer_text = ""
    text = ""
    loading = f"{bot.locale['loading']} {mon.name} Stats"

    area = get_area(areaname)
    if not area[1] == bot.locale['all']:
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

            footer_text = f"{(bot.locale['between']).capitalize()} {timespan[0].strftime(bot.locale['time_format_dhm'])} {bot.locale['and']} {timespan[1].strftime(bot.locale['time_format_dhm'])}"
        else:
            timespan = list([dateparser.parse(timespan), datetime.now()])

            if area[1] == bot.locale['all']:
                footer_text = f"{(bot.locale['since']).capitalize()} {timespan[0].strftime(bot.locale['time_format_dhm'])}"
            else:
                footer_text = f"{footer_text}, {bot.locale['since']} {timespan[0].strftime(bot.locale['time_format_dhm'])}"

    print(f"@{ctx.author.name} requested {mon.name} stats for area {area[1]}")    

    embed = discord.Embed(title=f"{mon.name}", description=text)
    embed.set_thumbnail(url=mon.icon)
    embed.set_footer(text=f"{loading}{footer_text}", icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    message = await ctx.send(embed=embed)

    shiny_count = await queries.get_shiny_count(mon.id, area[0], timespan[0], timespan[1], bot.config)

    if shiny_count > 0:
        shiny_total = await queries.get_shiny_total(mon.id, area[0], timespan[0], timespan[1], bot.config)
        shiny_odds = int(round((shiny_total / shiny_count), 0))
        text = text + f"{bot.locale['shinies']}: **1:{shiny_odds}** ({shiny_count:_}/{shiny_total:_})\n"
    else:
        text = text + f"{bot.locale['shinies']}: **0**\n"

    embed.description = text.replace("_", bot.locale['decimal_comma']) 
    await message.edit(embed=embed)

    print(f"     [1/3] Shiny Data for {mon.name} Stats")

    scan_numbers = await queries.get_scan_numbers(mon.id, area[0], timespan[0], timespan[1], bot.config)
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
        mon_total = int(mons)
        if found is not None:
            found_count = int(found)
            boosted_count = int(boosted)
        else:
            found_count = 0
            boosted_count = 0

    if found_count > 0:
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

    text = f"{bot.custom_emotes['gym_blue']}**{blue_count}**{bot.custom_emotes['blank']}{bot.custom_emotes['gym_red']}**{red_count}**{bot.custom_emotes['blank']}{bot.custom_emotes['gym_yellow']}**{yellow_count}**\n\n{bot.locale['total']}: **{total_count}**\n{bot.custom_emotes['ex_pass']} {bot.locale['ex_gyms']}: **{ex_count}** ({ex_odds}%)\n\n{bot.custom_emotes['raid']} {bot.locale['active_raids']}: **{raid_count}**"

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
    footer_text = ""
    text = ""
    loading = bot.locale['loading_quests']

    area = get_area(areaname)
    if not area[1] == bot.locale['all']:
        footer_text = area[1]
        loading = f"{loading} • {footer_text}"

    print(f"@{ctx.author.name} requested quests for area {area[1]}")

    embed = discord.Embed(title=bot.locale['quests'], description=text)
    embed.set_footer(text=loading, icon_url="https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif")
    message = await ctx.send(embed=embed)

    items = list()
    mons = list()
    item_found = False
    for item_id in bot.items:
        if bot.items[item_id]["name"].lower() == reward.lower():
            embed.set_thumbnail(url=f"{bot.config['mon_icon_repo']}rewards/reward_{item_id}_1.png")
            embed.title = f"{bot.items[item_id]['name']} {bot.locale['quests']}"
            items.append(int(item_id))
            item_found = True
    if not item_found:
        mon = details(reward, bot.config['mon_icon_repo'], bot.config['language'])
        embed.set_thumbnail(url=f"{bot.config['mon_icon_repo']}pokemon_icon_{str(mon.id).zfill(3)}_00.png")
        embed.title = f"{mon.name} {bot.locale['quests']}"
        mons.append(mon.id)
    
    await message.edit(embed=embed)

    quests = await queries.get_active_quests(bot.config, area[0])

    length = 0
    reward_mons = list()
    reward_items = list()
    lat_list = list()
    lon_list = list()

    for quest_json, quest_text, lat, lon, stop_name, stop_id in quests:
        quest_json = json.loads(quest_json)

        found_rewards = True

        item_id = quest_json[0]["item"]["item"]
        mon_id = quest_json[0]["pokemon_encounter"]["pokemon_id"]
        if item_id in items:
            reward_items.append([item_id, lat, lon])
        elif mon_id in mons:
            reward_mons.append([mon_id, lat, lon])
        else:
            found_rewards = False

        if found_rewards:
            if len(stop_name) >= 30:
                stop_name = stop_name[0:27] + "..."
            lat_list.append(lat)
            lon_list.append(lon)

            if bot.config['use_map']:
                map_url = bot.map_url.quest(lat, lon, stop_id)
            else:
                map_url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon})"
            map_url = short(map_url)

            entry = f"[{stop_name}]({map_url})\n"
            if length + len(entry) >= 2048:
                break
            else:
                text = text + entry
                length = length + len(entry)

    embed.description = text
    image = ""
    if length > 0:
        if bot.config['use_static']:
            await message.edit(embed=embed)
            static_map = bot.static_map.quest(lat_list, lon_list, reward_items, reward_mons, bot.custom_emotes)

            urllib.request.urlretrieve(static_map, "quest_command_static_map_temp.png")
            channel = await bot.fetch_channel(bot.config['host_channel'])
            image_msg = await channel.send(file=discord.File("quest_command_static_map_temp.png"))
            image = image_msg.attachments[0].url
            os.remove("quest_command_static_map_temp.png")
    else:
        embed.description = bot.locale["no_quests_found"]

    embed.set_footer(text=footer_text)
    embed.set_image(url=image)

    await message.edit(embed=embed)
    await asyncio.sleep(2)

@bot.event
async def on_ready():
    #await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name="Discordopole"))
    print("Connected to Discord. Ready to take commands.")

if __name__ == "__main__":
    for extension in extensions:
        bot.load_extension(extension)
    bot.run(bot.config['bot_token'])
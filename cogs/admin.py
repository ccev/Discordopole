import discord
import asyncio
import json
import aiohttp

from discord.ext import commands
from util.mondetails import details

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def download_url(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()

    @commands.group(pass_context=True)
    async def board(self, ctx):
        if not ctx.message.author.id in self.bot.config['admins']:
            return
        if ctx.invoked_subcommand is None:
            await ctx.send("`create/delete`")

    @board.group(pass_context=True)
    async def create(self, ctx):
        if not ctx.message.author.id in self.bot.config['admins']:
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
    async def delete(self, ctx, deleted_message_id):
        if not ctx.message.author.id in self.bot.config['admins']:
            print(f"@{ctx.author.name} tried to create a delete a Board but is no Admin")
            return
        message_found = False
        for board_type in self.bot.boards:
            if board_type == "raid_channels":
                continue
            for board in self.bot.boards[board_type]:
                if int(deleted_message_id) == board['message_id']:
                    message_found = True
                    self.bot.boards[board_type].remove(board)

                    with open("config/boards.json", "w") as f:
                        f.write(json.dumps(self.bot.boards, indent=4))

                    channel = await self.bot.fetch_channel(board["channel_id"])
                    message = await channel.fetch_message(deleted_message_id)
                    await message.delete()
                    await ctx.send("Successfully deleted Board.")
        
        if not message_found:
            await ctx.send("Couldn't find a board with that Message ID.")
            return

    @create.command(pass_context=True)
    async def raid(self, ctx, area, levels):
        if not ctx.message.author.id in self.bot.config['admins']:
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
        for areag in self.bot.geofences:
            if areag['name'].lower() == area.lower():
                areaexist = True
        if not areaexist:
            embed.description = "Couldn't find that area. Try again."
            await message.edit(embed=embed)
            return
        await ctx.message.delete()
        self.bot.boards['raids'].append({"channel_id": message.channel.id, "message_id": message.id, "title": self.bot.locale['raids'], "area": area, "timezone": self.bot.config['timezone'], "wait": 15, "levels": level_list, "ex": False})

        with open("config/boards.json", "w") as f:
            f.write(json.dumps(self.bot.boards, indent=4))

        embed.title = "Succesfully created this Raid Board"
        embed.description = f"You'll see this message being filled in soon\n\n```Area: {area}\nLevels: {levels}\nChannel ID: {message.channel.id}\nMessage ID: {message.id}```"
        await message.edit(embed=embed)
        print("Wrote Raid Board to config/boards.json")

    @create.command(pass_context=True)
    async def egg(self, ctx, area, levels):
        if not ctx.message.author.id in self.bot.config['admins']:
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
        for areag in self.bot.geofences:
            if areag['name'].lower() == area.lower():
                areaexist = True
        if not areaexist:
            embed.description = "Couldn't find that area. Try again."
            await message.edit(embed=embed)
            return
        await ctx.message.delete()
        self.bot.boards['eggs'].append({"channel_id": message.channel.id, "message_id": message.id, "title": self.bot.locale['eggs'], "area": area, "timezone": self.bot.config['timezone'], "wait": 15, "levels": level_list, "ex": False})

        with open("config/boards.json", "w") as f:
            f.write(json.dumps(self.bot.boards, indent=4))

        embed.title = "Succesfully created this Egg Board"
        embed.description = f"You'll see this message being filled in soon\n\n```Area: {area}\nLevels: {levels}\nChannel ID: {message.channel.id}\nMessage ID: {message.id}```"
        await message.edit(embed=embed)
        print("Wrote Egg Board to config/boards.json")

    @create.command(pass_context=True)
    async def stats(self, ctx, area, *, types):
        if not ctx.message.author.id in self.bot.config['admins']:
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
                if "lvl" in stat:
                    if "1" in stat:
                        stats.append("raid_lvl_1_active")
                    elif "2" in stat:
                        stats.append("raid_lvl_2_active")
                    elif "3" in stat:
                        stats.append("raid_lvl_3_active")
                    elif "4" in stat:
                        stats.append("raid_lvl_4_active")
                    elif "5" in stat:
                        stats.append("raid_lvl_5_active")
                    elif "all" in stat:
                        stats.append("raid_lvl_5_active")
                        stats.append("raid_lvl_4_active")
                        stats.append("raid_lvl_3_active")
                        stats.append("raid_lvl_2_active")
                        stats.append("raid_lvl_1_active")
                else:
                    stats.append("raid_active")
            elif "egg" in stat:
                if "lvl" in stat:
                    if "1" in stat:
                        stats.append("egg_lvl_1_active")
                    elif "2" in stat:
                        stats.append("egg_lvl_2_active")
                    elif "3" in stat:
                        stats.append("egg_lvl_3_active")
                    elif "4" in stat:
                        stats.append("egg_lvl_4_active")
                    elif "5" in stat:
                        stats.append("egg_lvl_5_active")
                    elif "all" in stat:
                        stats.append("egg_lvl_5_active")
                        stats.append("egg_lvl_4_active")
                        stats.append("egg_lvl_3_active")
                        stats.append("egg_lvl_2_active")
                        stats.append("egg_lvl_1_active")
                else:
                    stats.append("egg_active")
            elif "stop" in stat:
                stats.append("stop_amount")
            elif "lure" in stat:
                if "amount" in stat:
                    stats.append("lure_amount")
                elif "types" in stat:
                    stats.append("lure_types")
            elif "grunt" in stat:
                #if "active" in stat:
                stats.append("grunt_active")
            elif "leader" in stat:
                stats.append("leader_active")
            elif "quest" in stat:
                stats.append("quest_active")
            elif "hundos" in stat:
                if "active" in stat:
                    stats.append("hundos_active")
                elif "today" in stat:
                    stats.append("hundos_today")
            elif "iv0" in stat:
                if "active" in stat:
                    stats.append("iv0_active")
                elif "today" in stat:
                    stats.append("iv0_today")
            elif "scanned" in stat:
                if "active" in stat:
                    stats.append("scanned_active")
                elif "today" in stat:
                    stats.append("scanned_today")
            elif "average" in stat:
                if "iv" in stat:
                    if "active" in stat:
                        stats.append("average_iv_active")
                    elif "today" in stat:
                        stats.append("average_iv_today")

        areaexist = False
        for areag in self.bot.geofences:
            if areag['name'].lower() == area.lower():
                areaexist = True
        if not areaexist:
            embed.description = "Couldn't find that area. Try again."
            await message.edit(embed=embed)
            return
        await ctx.message.delete()
        self.bot.boards['stats'].append({"channel_id": message.channel.id, "message_id": message.id, "title": self.bot.locale['stats'], "area": area, "timezone": self.bot.config['timezone'], "wait": 15, "type": stats})

        with open("config/boards.json", "w") as f:
            f.write(json.dumps(self.bot.boards, indent=4))

        embed.title = "Succesfully created this Stat Board"
        embed.description = f"You'll see this message being filled in soon\n\n```Area: {area}\nStats: {stats}\nChannel ID: {message.channel.id}\nMessage ID: {message.id}```"
        await message.edit(embed=embed)
        print("Wrote Stat Board to config/boards.json")

    @create.command(pass_context=True)
    async def raidchannel(self, ctx, channel_name, area, levels):
        if not ctx.message.author.id in self.bot.config['admins']:
            print(f"@{ctx.author.name} tried to create a Raid Channel but is no Admin")
            return
        print("Creating Raid Channel")

        guild = ctx.message.guild
        channel = await guild.create_text_channel(channel_name)

        embed = discord.Embed(title="Raid Channel", description="")
        message = await ctx.send(embed=embed)
        
        level_list = list(levels.split(','))
        level_list = list(map(int, level_list))

        if all(i > 5 or i < 1 for i in level_list):
            embed.description = "Couldn't create Raid Channel. Try chosing other levels."
            await message.edit(embed=embed)
            return
        areaexist = False
        for areag in self.bot.geofences:
            if areag['name'].lower() == area.lower():
                areaexist = True
        if not areaexist:
            embed.description = "Couldn't find that area. Try again."
            await message.edit(embed=embed)
            return

        await ctx.message.delete()
        self.bot.boards['raid_channels'].append({"channel_id": channel.id, "area": area, "timezone": self.bot.config['timezone'], "wait": 15, "levels": level_list})

        with open("config/boards.json", "w") as f:
            f.write(json.dumps(self.bot.boards, indent=4))

        embed.title = "Succesfully created this Raid Channel"
        embed.description = f"You'll see the channel being filled in soon.\n<#{channel.id}>\n\n```Area: {area}\nLevels: {levels}\nChannel ID: {channel.id}```"
        await message.edit(embed=embed)
        print("Wrote Raid Channel to config/boards.json")

    @create.command(pass_context=True)
    async def quest(self, ctx, area, *, rewards):
        if not ctx.message.author.id in self.bot.config['admins']:
            print(f"@{ctx.author.name} tried to create a Quest Board but is no Admin")
            return
        print("Creating Quest Board")

        embed = discord.Embed(title="Quest Board", description="")
        message = await ctx.send(embed=embed)
        
        rewards = list(rewards.split(','))
        items = list()
        mons = list()

        areaexist = False
        for areag in self.bot.geofences:
            if areag['name'].lower() == area.lower():
                areaexist = True
        if not areaexist:
            embed.description = "Couldn't find that area. Try again."
            await message.edit(embed=embed)
            return

        for reward in rewards:
            item_found = False
            for item_id in self.bot.items:
                if self.bot.items[item_id]["name"].lower() == reward.lower():
                    items.append(int(item_id))
                    found_item_id = item_id
                    item_found = True
            if not item_found:
                mon = details(reward, self.bot.config['mon_icon_repo'], self.bot.config['language'])
                mons.append(mon.id)

        await ctx.message.delete()
        

        embed.title = "Now downloading Emotes"
        embed_emotes = ""
        embed_rest = f"\n\n```Area: {area}\nMons: {mons}\nItems: {items}\nChannel ID: {message.channel.id}\nMessage ID: {message.id}```"
        embed.description = embed_emotes + embed_rest
        await message.edit(embed=embed)
        print("Wrote Quest Board to config/boards.json - Now downloading Emotes")

        guild = await self.bot.fetch_guild(self.bot.config['host_server'])
        existing_emotes = await guild.fetch_emojis()
        for mon_id in mons:
            emote_exist = False
            for existing_emote in existing_emotes:
                if f"m{mon_id}" == existing_emote.name:
                    emote_exist = True
            if not emote_exist:
                try:
                    image = await self.download_url(f"{self.bot.config['mon_icon_repo']}pokemon_icon_{str(mon_id).zfill(3)}_00.png")
                    emote = await guild.create_custom_emoji(name=f"m{mon_id}", image=image)
                    emote_ref = f"<:{emote.name}:{emote.id}>"
                    embed_emotes = f"{embed_emotes}\n{emote_ref} `{emote_ref}`"
                    embed.description = embed_emotes + embed_rest
                    await message.edit(embed=embed)
                    if f"m{mon_id}" in self.bot.custom_emotes:
                        self.bot.custom_emotes[f"m{mon_id}"] = emote_ref
                    else:
                        self.bot.custom_emotes.update({f"m{mon_id}": emote_ref})
                except Exception as err:
                    print(err)
                    print(f"Error while importing emote m{mon_id}")
            else:
                embed_emotes = f"{embed_emotes}\nmon {mon_id}: already exists"
                embed.description = embed_emotes + embed_rest
                await message.edit(embed=embed)

        for item in items:
            emote_exist = False
            for existing_emote in existing_emotes:
                if f"i{item}" == existing_emote.name:
                    emote_exist = True
            if not emote_exist:
                try:
                    image = await self.download_url(f"{self.bot.config['mon_icon_repo']}rewards/reward_{item}_1.png")
                    emote = await guild.create_custom_emoji(name=f"i{item}", image=image)
                    emote_ref = f"<:{emote.name}:{emote.id}>"
                    embed_emotes = f"{embed_emotes}\n{emote_ref} `{emote_ref}`"
                    embed.description = embed_emotes + embed_rest
                    await message.edit(embed=embed)
                    if f"i{item}" in self.bot.custom_emotes:
                        self.bot.custom_emotes[f"i{item}"] = emote_ref
                    else:
                        self.bot.custom_emotes.update({f"i{item}": emote_ref})
                except Exception as err:
                    print(err)
                    print(f"Error while importing emote i{item}")
            else:
                embed_emotes = f"{embed_emotes}\nitem {item}: already exists"
                embed.description = embed_emotes + embed_rest
                await message.edit(embed=embed)

        embed.title = "Succesfully created this Quest Board"
        embed.description = "You'll see the message being filled in soon.\n" + embed_emotes + embed_rest
        await message.edit(embed=embed)

        print("All done with Quest Board")
        title = self.bot.locale['quests']
        if len(items) + len(mons) == 1:
            title2 = ""
            if len(items) == 1:
                title2 = self.bot.items[found_item_id]["name"]
            if len(mons) == 1:
                title2 = mon.name
            title = f"{title2} {title}"

        self.bot.boards['quests'].append({"channel_id": message.channel.id, "message_id": message.id, "title": title, "area": area, "mons": mons, "items": items})

        with open("config/boards.json", "w") as f:
            f.write(json.dumps(self.bot.boards, indent=4))

        with open("config/emotes.json", "w") as f:
            f.write(json.dumps(self.bot.custom_emotes, indent=4))

    @commands.group(pass_context=True)
    async def get(self, ctx):
        if not ctx.message.author.id in self.bot.config['admins']:
            return
        if ctx.invoked_subcommand is None:
            await ctx.send("Be more specific")

    @get.command(pass_context=True)
    async def emotes(self, ctx, quick_name=""):
        if not ctx.message.author.id in self.bot.config['admins']:
            print(f"@{ctx.author.name} tried to import emotes but is no Admin")
            return

        needed_emote_names = ["ex_pass", "raid_egg_1", "raid_egg_2", "raid_egg_3", "raid_egg_4", "raid_egg_5", "gym_blue", "gym_red", "gym_yellow", "gym_white", "gym_grey", "blank", "raid", "cliff", "grunt_female", "pokeball", "pokestop", "lure", "lure_normal", "lure_glacial", "lure_mossy", "lure_magnetic"]

        if quick_name == ctx.guild.name:
            print(f"@{ctx.author.name} wants to import emotes in Server {ctx.guild.name} and said the name directly")
            embed = discord.Embed(title="Importing Emotes. Please Wait", description="")
            message = await ctx.send(embed=embed)
        else:
            print(f"@{ctx.author.name} wants to import emotes in Server {ctx.guild.name}. Waiting for confirmation")
            embed = discord.Embed(title="Importing emotes might overwrite some custom emotes in this Server!", description="Please make sure you don't care about this Server's emotes.\n\nTo continue, please say the name of this Server.")
            message = await ctx.send(embed=embed)
            def check(m):
                return m.content == ctx.guild.name and m.author == ctx.author and m.channel == ctx.channel
            try:
                confirm = await self.bot.wait_for('message', check=check, timeout=60)
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
            if emote.name in needed_emote_names:
                await emote.delete()
                embed.description = f"{embed.description}Removed Emote `{emote.name}`\n"
                await message.edit(embed=embed)
        embed.description = ""
        print(f"Done. Now importing all needed emotes from repo {self.bot.config['emote_repo']}")

        for emote_name in needed_emote_names:
            try:
                image = await self.download_url(f"{self.bot.config['emote_repo']}{emote_name}.png")
                emote = await ctx.guild.create_custom_emoji(name=emote_name, image=image)
                emote_ref = f"<:{emote.name}:{emote.id}>"
                embed.description = f"{embed.description}{emote_ref} `{emote_ref}`\n"
                await message.edit(embed=embed)
                self.bot.custom_emotes.update({emote_name: emote_ref})
            except Exception as err:
                print(err)
                print(f"Error while importing emote {emote_name}") 
        embed.title = "Done importing Emotes"
        await message.edit(embed=embed)
        with open("config/emotes.json", "w") as f:
            f.write(json.dumps(self.bot.custom_emotes, indent=4))

        print("All emotes imported.")

    @get.command(pass_context=True)
    async def updates(self, ctx):
        if not ctx.message.author.id in self.bot.config['admins']:
            print(f"@{ctx.author.name} tried to import emotes but is no Admin")
            return
        await ctx.send("Seeing if there's new stuff to add to Discordopole...")
        
        print("Looking for updates")
        count = 0
        for board in self.bot.boards['raids']:
            if not "title" in board:            
                self.bot.boards['raids'][count]['title'] = locale['raids']
                print("Updated title for Raid Board")
            if not "ex" in board:
                self.bot.boards['raids'][count]['ex'] = False
                print("Updated ex for Raid Board")
            count += 1
            
        for board in self.bot.boards['raid_channels']:
            continue

        count = 0    
        for board in self.bot.boards['eggs']:
            if not "title" in board:            
                self.bot.boards['eggs'][count]['title'] = locale['eggs']
                print("Updated title for Egg Board")
            if not "ex" in board:
                self.bot.boards['eggs'][count]['ex'] = False
                print("Updated ex for Egg Board")
            count += 1

        count = 0     
        for board in self.bot.boards['stats']:
            if not "title" in board:            
                self.bot.boards['stats'][count]['title'] = locale['stats']
                print("Updated title for Stat Board")
            count += 1

        if not "quests" in self.bot.boards:
            self.bot.boards["quests"] = []
            print("put empty quests board in boards.json")

        with open("config/boards.json", "w") as f:
            f.write(json.dumps(self.bot.boards, indent=4))
        await ctx.send("Done.")

def setup(bot):
    bot.add_cog(Admin(bot))

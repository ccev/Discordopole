import discord
import asyncio
import json

from discord.ext import tasks, commands
from datetime import datetime

from discordopole import get_area
from util.mondetails import details
import util.queries as queries

class Channels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_loop.start()
  
    def get_raid_embed(self, mon_id, start, end, move_1, move_2, lat, lon, gym_name, gym_img, level, form):
        start = datetime.fromtimestamp(start).strftime(self.bot.locale['time_format_hm'])
        end = datetime.fromtimestamp(end).strftime(self.bot.locale['time_format_hm'])

        if len(gym_name) >= 30:
            gym_name = gym_name[0:27] + "..."

        if not mon_id is None and mon_id > 0:
            mon_name = details.id(mon_id, self.bot.config['language'])
            mon_img = f"{self.bot.config['mon_icon_repo']}pokemon_icon_{str(mon_id).zfill(3)}_{str(form).zfill(2)}.png"

            if move_1 > self.bot.max_moves_in_list:
                move_1 = "?"
            else:
                move_1 = self.bot.moves[str(move_1)]["name"]
            if move_2 > self.bot.max_moves_in_list:
                move_2 = "?"
            else:
                move_2 = self.bot.moves[str(move_2)]["name"]

            if str(mon_id) in self.bot.forms:
                if str(form) in self.bot.forms[str(mon_id)]:
                    mon_name = f"{self.bot.forms[str(mon_id)][str(form)]} {mon_name}"

            embed = discord.Embed(title=gym_name, description=f"{self.bot.locale['until']} **{end}**\n100%: **{self.bot.raidcp[str(mon_id)]['max_cp_20']}** | **{self.bot.raidcp[str(mon_id)]['max_cp_25']}**\n{self.bot.locale['moves']}: **{move_1}** | **{move_2}**\n\n[Google Maps](https://www.google.com/maps/search/?api=1&query={lat},{lon}) | [Apple Maps](https://maps.apple.com/maps?daddr={lat},{lon})")
            embed.set_thumbnail(url=gym_img)
            embed.set_author(name=mon_name, icon_url=mon_img)
        else:
            egg_name = f"{self.bot.locale['level']} {level} {self.bot.locale['egg']}"
            egg_img = f"{self.bot.config['emote_repo']}raid_egg_{level}.png"

            embed = discord.Embed(title=gym_name, description=f"{self.bot.locale['hatches_at']} **{start}**\n{self.bot.locale['lasts_until']} **{end}**\n\n[Google Maps](https://www.google.com/maps/search/?api=1&query={lat},{lon}) | [Apple Maps](https://maps.apple.com/maps?daddr={lat},{lon})")
            embed.set_thumbnail(url=gym_img)
            embed.set_author(name=egg_name, icon_url=egg_img)

        return embed

    @tasks.loop(seconds=2.0) 
    async def channel_loop(self):
        try:
            for board in self.bot.boards['raid_channels']:
                channel = await self.bot.fetch_channel(board["channel_id"])
                channel_id = str(board['channel_id'])
                area = get_area(board["area"])
                raids = await queries.get_active_raids(self.bot.config, area[0], board["levels"], board["timezone"])
                raid_gyms = []
                with open("data/raid_cache.json", "r") as f:
                    cache = json.load(f)
                
                if not str(board['channel_id']) in cache:
                    cache[channel_id] = {}

                for gym_id, start, end, lat, lon, mon_id, move_1, move_2, name, ex, level, gym_img, form in raids:
                    raid_gyms.append(gym_id)

                    # Check if the Raid has hatched & edit (or send) accordingly
                    if not mon_id is None and mon_id > 0:
                        if str(gym_id) in cache[channel_id]:
                            if cache[channel_id][gym_id][1] == "egg":
                                cache[channel_id][gym_id][1] = "raid"
                                embed = self.get_raid_embed(mon_id, start, end, move_1, move_2, lat, lon, name, gym_img, level, form)
                                message = await channel.fetch_message(cache[channel_id][gym_id][0])
                                await message.edit(embed=embed, content="")
                                await asyncio.sleep(1)
                        else:
                            embed = self.get_raid_embed(mon_id, start, end, move_1, move_2, lat, lon, name, gym_img, level, form)
                            message = await channel.send(embed=embed,content="")
                            cache[channel_id][str(gym_id)] =  [message.id, "raid"]
                            await asyncio.sleep(1)
                        
                    # Send messages for new eggs
                    else:
                        if not str(gym_id) in cache[channel_id]:
                            embed = self.get_raid_embed(mon_id, start, end, move_1, move_2, lat, lon, name, gym_img, level, form)
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
        except Exception as err:              
            print(err)
            print("Error while updating Raid Channel. Skipping it.")
            await asyncio.sleep(5)  
  
  
    @channel_loop.before_loop
    async def before_channels(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Channels(bot))
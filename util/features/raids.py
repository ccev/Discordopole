"""import discord

from datetime import datetime

import util.queries as queries
from util.util import Stop, Mon



class RaidMessage():
    def __init__(self, bot, settings, is_egg_board):
        self.board = settings
        self.bot = bot
        self.raids = []
        self.egg_board = is_egg_board

    async def get_raids(self):
        raids = await queries.get_active_raids(self.bot.config, area[0], board["levels"], board["timezone"], board['ex'])
        for gym_id, start, end, lat, lon, mon_id, move_1, move_2, name, ex, level, gym_img, form in raids:
            gym = Stop(gym_id, lat, lon, name, gym_img, ex)
            mon = Mon(self.bot, mon_id, move_1=move_1, move_2=move_2, form=form)
            raid = Raid(self.bot, level, start, end, gym, mon)
            raid.emote()
            if self.egg_board and raid.egg:
                self.raids.append(raid)
            elif (not self.egg_board) and (not raid.egg):
                self.raids.append(raid)

    async def raid_board_message(self):
        text = ""
        static_map = ""
        for raid in self.raids:
            entry = self.bot.templates.raid_board(raid)
            if len(text) + len(entry) >= 2048:
                break
            else:
                text += entry

        if len(raids) == 0:
            text = self.bot.locale["empty_board"]
        else:
            if self.board.get("static_map", False):
                static_map = await self.bot.static_map.raid(self.raids)

        embed = discord.Embed(description=text, title=self.board.get(title, self.board.locale["raids"]), timestamp=datetime.utcnow())
        self.embed.set_footer(text=self.area.name)
        self.embed.set_image(url=static_map)"""
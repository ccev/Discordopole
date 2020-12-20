from datetime import datetime

from discordopole import dp
from dp.boards import Board
from dp.pogo import Mon, Gym

class RaidEgg:
    def __init__(self, level):
        self.id = level
        self.name = dp.files.locale["level_egg"].format(level=level)
        self.img = f"{dp.config.emote_repo}raid_egg_{level}.png"
        self.emote = dp.files.custom_emotes.get(f"raid_egg_{level}", "")

class Raid:
    def __init__(self, level, start, end, gym, mon_id, move_1, move_2, form_id):
        self.level = level
        self.start = datetime.fromtimestamp(start)
        self.end = datetime.fromtimestamp(end)
        self.gym = gym

        if mon_id is None:
            self.egg = True
            self.boss = RaidEgg(self.level)
        else:
            self.egg = False
            self.boss = Mon(mon_id, move_1, move_2, form_id)
    
    async def create_emote(self):
        await self.boss.get_emote()

class RaidBoard(Board):
    def __init__(self, board, is_egg_board):
        super().__init__(board)
        self.raids = []
        self.egg_board = is_egg_board

        self.standard_format = {
            "channel_id": "",
            "message_id": "",
            "title": dp.files.locale["raids"],
            "area": "",
            "wait": 2,
            "levels": [
                5
            ],
            "ex": False,
            "static_map": False
        }
        self.standard_dict()

    async def get_objs(self):
        raids = await dp.queries.execute("active_raids", sql_fence=self.area.sql_fence)
        for gym_id, start, end, lat, lon, mon_id, move_1, move_2, name, ex, level, gym_img, form in raids:
            if int(level) not in self.board["levels"]:
                continue
            if self.board["ex"] and (not ex):
                continue
            gym = Gym(gym_id, lat, lon, name, gym_img, ex)
            raid = Raid(level, start, end, gym, mon_id, move_1, move_2, form)
            if self.egg_board and raid.egg:
                self.raids.append(raid)
            elif (not self.egg_board) and (not raid.egg):
                self.raids.append(raid)
                await raid.create_emote()

    async def generate_embed(self):
        template = dp.templates.raid_board()
        if self.board["static_map"]:
            self.static_map = await dp.static_map.raid(self.raids)
        self.generate_text(self.raids, template)

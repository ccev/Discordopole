from datetime import datetime

from dp.dp_objects import dp
from dp.boards.basicboard import Board
from dp.pogo import Mon, Gym

raid_format = {
    "channel_id": "",
    "message_id": "",
    "title": dp.files.locale["raids"],
    "area": "",
    "wait": 2,
    "levels": [
        5
    ],
    "state": [
        "hatched",
        "unhatched"
    ],
    "ex": False,
    "static_map": False
}

class RaidEgg:
    def __init__(self, level):
        self.id = level
        self.name = dp.files.locale["level_egg"].format(level=level)
        self.img = dp.config.asset_repo + f"emotes/egg{level}.png"
        self.emote = dp.emotes.get_standard(f"egg{level}")

class Raid:
    def __init__(self, level, start, end, gym, mon_id, move_1, move_2, form_id, evolution):
        self.level = level
        self.start = datetime.fromtimestamp(start)
        self.end = datetime.fromtimestamp(end)
        self.gym = gym

        if mon_id:
            self.egg = False
            self.boss = Mon(mon_id, move_1, move_2, form_id, evolution=evolution)
        else:
            self.egg = True
            self.boss = RaidEgg(self.level)

class RaidBoard(Board):
    def __init__(self, board):
        super().__init__(board)

        self.standard_format = raid_format
        self.standard_dict()

    async def get_objs(self):
        raids = []
        eggs = []
        db_raids = await dp.queries.execute("active_raids", sql_fence=self.area.sql_fence)
        for gym_id, start, end, lat, lon, mon_id, move_1, move_2, name, ex, level, gym_img, form, team, evolution in db_raids:
            if int(level) not in self.board["levels"]:
                continue
            if self.board["ex"] and (not ex):
                continue
            gym = Gym(gym_id, lat, lon, name, gym_img, ex, team)
            raid = Raid(level, start, end, gym, mon_id, move_1, move_2, form, evolution)
            if raid.egg:
                eggs.append(raid)
            else:
                raids.append(raid)
                await raid.boss.get_emote()
        
        self.raids = raids + eggs
        self.new_ids = ["e" + raid.gym.id for raid in eggs] + ["r" + raid.gym.id for raid in raids]

    async def generate_embed(self):
        template = dp.templates.raid_board()
        if self.board["static_map"]:
            self.static_map = await dp.static_map.raid(self.raids)
        self.generate_text(self.raids, template)

from datetime import datetime

from dp.boards import Board
from dp.pogo import Mon, Gym

class Raid():
    def __init__(self, dp, level, start, end, gym, boss):
        self.level = level
        self.start = datetime.fromtimestamp(start)
        self.end = datetime.fromtimestamp(end)
        self.gym = gym

        if boss.name != "?":
            self.egg = False
            self.boss = boss
        else:
            self.egg = True
            self.boss = Mon(dp)
            self.boss.custom(self.level, dp.files.locale["level_egg"].format(level=self.level), f"{dp.config.emote_repo}raid_egg_{self.level}.png")
            self.boss.emote = dp.files.custom_emotes.get(f"raid_egg_{self.level}", "")
    
    async def create_emote(self):
        await self.boss.get_emote()

class RaidBoard(Board):
    def __init__(self, dp, board, is_egg_board):
        super().__init__(dp, board)
        self.raids = []
        self.egg_board = is_egg_board

        self.standard_format = {
            "channel_id": "",
            "message_id": "",
            "title": self.dp.files.locale["raids"],
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
        raids = await self.dp.queries.execute("active_raids", sql_fence=self.area.sql_fence)
        for gym_id, start, end, lat, lon, mon_id, move_1, move_2, name, ex, level, gym_img, form in raids:
            if int(level) not in self.board["levels"]:
                continue
            if self.board["ex"] and (not ex):
                continue
            gym = Gym(self.dp.files.custom_emotes, gym_id, lat, lon, name, gym_img, ex)
            mon = Mon(self.dp, mon_id, move_1=move_1, move_2=move_2, form=form)
            raid = Raid(self.dp, level, start, end, gym, mon)
            if self.egg_board and raid.egg:
                self.raids.append(raid)
            elif (not self.egg_board) and (not raid.egg):
                self.raids.append(raid)
                await raid.create_emote()

    async def generate_embed(self):
        template = self.dp.templates.raid_board()
        if self.board["static_map"]:
            self.static_map = await self.dp.static_map.raid(self.raids)
        self.generate_text(self.raids, template)

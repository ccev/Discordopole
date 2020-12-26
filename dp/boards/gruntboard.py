from dp.dp_objects import dp
from dp.boards.basicboard import Board
from dp.pogo import Mon, Stop

class Grunt:
    def __init__(self, gid, start, end, stop):
        self.id = gid
        self.start = start
        self.end = end
        self.stop = stop
        self.img = dp.config.asset_repo + f"grunts/g{self.id}.png"

        self.mons = []
        for mid in dp.gamedata.available_grunts.get(gid, []):
            mids = mid.split("_")
            self.mons.append(Mon(mon_id=mids[0], form=mids[1]))

    async def get_emote(self):
        if self.id in dp.gamedata.grunt_to_type.keys():
            emote_name = "t" + str(dp.gamedata.grunt_to_type[self.id])
            emote_path = "types/" + emote_name
        else:
            emote_name = "g" + str(self.id)
            emote_path = "grunts/" + emote_name

        self.emote = await dp.emotes.get(emote_name, dp.config.asset_repo + emote_path + ".png")

class GruntBoard(Board):
    def __init__(self, board):
        super().__init__(board)

        self.standard_format = {
            "channel_id": "",
            "message_id": "",
            "title": dp.files.locale["grunts"],
            "area": "",
            "wait": 2,
            "mons": [],
            "grunts": [],
            "static_map": False
        }
        self.standard_dict()

        for mon in self.board["mons"]:
            for gid, data in dp.gamedata.available_grunts.items():
                if mon in [int(m.split("_")[0]) for m in data]:
                    if gid not in self.board["grunts"]:
                        self.board["grunts"].append(gid)

        self.board["grunts"] = list(map(str, self.board["grunts"]))
        #print("GRUNT INIT")
        #print(self.board)

    async def get_objs(self):
        self.grunts = []
        #print(self.board["grunts"])
        wheregid = ",".join(self.board["grunts"])
        grunts = await dp.queries.execute("active_grunts", sql_fence=self.area.sql_fence, extra=wheregid)
        for pid, name, image, lat, lon, start, end, gid in grunts:
            stop = Stop(pid, lat, lon, name, image)
            grunt = Grunt(gid, start, end, stop)
            for mon in grunt.mons:
                await mon.get_emote()
            await grunt.get_emote()
            self.grunts.append(grunt)

    async def generate_embed(self):
        template = dp.templates.grunt_board()
        if self.board["static_map"]:
            self.static_map = await dp.static_map.grunt(self.grunts)
        self.generate_text(self.grunts, template)
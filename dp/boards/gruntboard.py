from dp.dp_objects import dp
from dp.boards.basicboard import Board
from dp.pogo import Mon, Stop

grunt_format = {
    "channel_id": "",
    "message_id": "",
    "title": dp.files.locale["grunts"],
    "area": "",
    "wait": 2,
    "mons": [],
    "grunts": [],
    "static_map": False
}

class Grunt:
    def __init__(self, gid, start, end, stop):
        self.start = start
        self.end = end
        self.stop = stop

        self.data = dp.pogodata.get_grunt(id=gid)
        self.img = dp.config.asset_repo + f"grunts/g{self.data.id}.png"

        self.mons = []
        for reward in self.data.rewards:
            self.mons.append(Mon(pd_mon=reward))

    async def get_emote(self):
        if self.data.type:
            emote_name = "t" + str(self.data.type.id)
            emote_path = "types/" + emote_name
        else:
            emote_name = "g" + str(self.data.id)
            emote_path = "grunts/" + emote_name

        self.emote = await dp.emotes.get(emote_name, dp.config.asset_repo + emote_path + ".png")

class GruntBoard(Board):
    def __init__(self, board):
        super().__init__(board)

        self.standard_format = grunt_format
        self.standard_dict()

        for mon_id in self.board["mons"]:
            for grunt in dp.pogodata.grunts:
                if int(mon_id) in [m.id for m in grunt.rewards]:
                    self.board["grunts"].append(grunt.id)

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
        self.new_ids = [grunt.stop.id for grunt in self.grunts]

    async def generate_embed(self):
        template = dp.templates.grunt_board()
        if self.board["static_map"]:
            self.static_map = await dp.static_map.grunt(self.grunts)
        self.generate_text(self.grunts, template)
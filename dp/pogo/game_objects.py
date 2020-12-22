from dp.dp_objects import dp
from dp.utils.emotes import DPEmote

class Stop():
    def __init__(self, sid, lat, lon, name, img):
        self.id = sid
        self.lat = lat
        self.lon = lon
        self.name = name
        self.img = img
        self.icon = dp.config.emote_repo + "pokestop.png"

        if len(name) >= 30:
            name = name[0:27]
            while name[-1:] == " ":
                name = name[:-1]
            name += "..."
            self.short_name = name
        else:
            self.short_name = name

class Gym(Stop):
    def __init__(self, gid, lat, lon, name, img, ex=False, team_id=0):
        super().__init__(gid, lat, lon, name, img)
        self.ex = ex
        self.team_id = team_id

        if self.ex:
            self.ex_emote = dp.files.custom_emotes.get("ex_pass", "")
        else:
            self.ex_emote = ""

        team_ids = {
            0: "white",
            1: "blue",
            2: "red",
            3: "yellow"
        }
        self.icon = dp.config.emote_repo + f"gym_{team_ids[self.team_id]}.png"

class GameObject:
    def __init__(self):
        self.emote = ""
        self.dp_emote = ""

    async def standard_get_emote(self, emote_name):
        self.emote = dp.files.custom_emotes.get(emote_name, "")

        if self.emote == "":
            self.dp_emote = DPEmote()
            await self.dp_emote.create(self.img, emote_name)
            self.emote = self.dp_emote.ref

class Mon(GameObject):
    def __init__(self, mon_id=None, move_1=1, move_2=1, form=0):
        self.id = mon_id
        self.name = dp.gamedata.mon_locale.get(self.id, "?")
        self.move_1 = self.Move(move_1)
        self.move_2 = self.Move(move_2)
        self.form = self.Form(self.id, form)
            
        self.img = dp.config.mon_icon_repo + f"pokemon_icon_{str(self.id).zfill(3)}_{str(self.form.id).zfill(2)}.png"

    async def get_emote(self, emote_name=None):
        if emote_name is None:
            emote_name = f"m{self.id}"
        await self.standard_get_emote(emote_name)
        
    class Move:
        def __init__(self, move_id):
            self.name = dp.gamedata.move_locale.get(str(move_id), "?")
            self.id = move_id
    
    class Form:
        def __init__(self, mid, fid):
            if fid is None:
                fid = 0
            self.id = fid
            self.name = dp.files.form_locale.get(str(mid), {}).get(str(fid), "")
            try:
                self.short_name = self.name[0]
            except:
                self.short_name = ""

class Item(GameObject):
    def __init__(self, item_id=None):
        self.id = item_id
        self.name = dp.gamedata.item_locale.get(self.id, "?")
        self.img = dp.config.mon_icon_repo + f"rewards/reward_{self.id}_1.png"
    
    async def get_emote(self, emote_name=None):
        if emote_name is None:
            emote_name = f"i{self.id}"
        await self.standard_get_emote(emote_name)
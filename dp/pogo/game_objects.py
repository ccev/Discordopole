from dp.dp_objects import dp
from dp.utils.emotes import DPEmote

MON_EMOTE_NAMES = {}

class Stop():
    def __init__(self, sid, lat, lon, name, img):
        self.id = sid
        self.lat = lat
        self.lon = lon
        self.name = name
        self.img = img
        self.icon = dp.config.asset_repo + "icons/pokestop.png"

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
            self.ex_emote = dp.emotes.get_standard("ex_pass")
        else:
            self.ex_emote = ""

        self.icon = dp.config.asset_repo + f"icons/gym{self.team_id}.png"

class GameObject:
    def __init__(self):
        self.emote = ""

    async def get_emote(self, emote_name=None):
        if emote_name is None:
            emote_name = self.emote_identifier + str(self.data.id)
        self.emote = await dp.emotes.get(emote_name, self.img)

class Mon(GameObject):
    def __init__(self, mon_id=None, move_1=1, move_2=1, form=0, evolution=0, costume=0, pd_mon=None):
        if pd_mon is not None:
            self.data = pd_mon
        else:
            self.data = dp.pogodata.get_mon(id=mon_id, form=form, temp_evolution_id=evolution, costume=costume)

        self.move_1 = dp.pogodata.get_move(id=move_1)
        self.move_2 = dp.pogodata.get_move(id=move_2)
    
        suffix = ""
        if self.data.costume:
            suffix = "_" + str(self.data.costume)
        elif self.data.temp_evolution_id:
            suffix = "_" + str(self.data.temp_evolution_id)

        formpart = "00"
        if self.data.form:
            formpart = self.data.form

        self.img = dp.config.mon_icon_repo + f"pokemon_icon_{str(self.data.id).zfill(3)}_{formpart}{suffix}.png"

    async def get_emote(self):
        emote_name = MON_EMOTE_NAMES.get(self.data)

        if not emote_name:
            emote_name = "p" + str(self.data.id)
            if self.data.form and not dp.pogodata.get_mon(template=self.data.base_template).asset == self.data.asset:
                emote_name += "f" + str(self.data.form)
            if self.data.costume:
                emote_name += "c" + str(self.data.costume)
            if self.data.temp_evolution_id:
                emote_name += "e" + str(self.data.temp_evolution_id)

        self.emote = await dp.emotes.get(emote_name, self.img)
        
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
        self.data = dp.pogodata.get_item(id=item_id)
        self.emote_identifier = "i"
        self.img = dp.config.mon_icon_repo + f"rewards/reward_{self.data.id}_1.png"

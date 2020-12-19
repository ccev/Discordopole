class Stop():
    def __init__(self, sid, lat, lon, name, img):
        self.id = sid
        self.lat = lat
        self.lon = lon
        self.name = name
        self.img = img

        if len(name) >= 30:
            name = name[0:27]
            while name[-1:] == " ":
                name = name[:-1]
            name += "..."
            self.short_name = name
        else:
            self.short_name = name

class Gym(Stop):
    def __init__(self, custom_emotes, gid, lat, lon, name, img, ex=False, team_id=0):
        super().__init__(gid, lat, lon, name, img)
        self.ex = ex
        self.team_id = team_id

        if self.ex:
            self.ex_emote = custom_emotes.get("ex_pass", "")
        else:
            self.ex_emote = ""

class Mon():
    def __init__(self, dp, mon_id=None, mon_name=None, move_1=1, move_2=1, form=0):
        self.dp = dp
        self.id, self.name, self.match = mon_item_matching(dp, mon_id, mon_name, bot.mon_names)
        self.move_1 = self.Move(dp, move_1)
        self.move_2 = self.Move(dp, move_2)
        self.form = self.Form(dp, self.id, form)
        self.emote = ""
        self.dp_emote = None
            
        self.img = dp.config.mon_icon_repo + f"pokemon_icon_{str(self.id).zfill(3)}_{str(self.form.id).zfill(2)}.png"

    def custom(self, m_id, m_name, m_img):
        self.id = m_id
        self.name = m_name
        self.img = m_img

    async def get_emote(self, emote_name=None):
        if emote_name is None:
            emote_name = f"m{self.id}"
        await mon_item_emote(self, emote_name)
        
    class Move():
        def __init__(self, bot, move_id):
            self.name = bot.moves.get(str(move_id), "?")
            self.id = move_id
    
    class Form():
        def __init__(self, bot, mid, fid):
            if fid is None:
                fid = 0
            self.id = fid
            self.name = bot.forms.get(str(mid), {}).get(str(fid), "")
            try:
                self.short_name = self.name[0]
            except:
                self.short_name = ""

class Item():
    def __init__(self, bot, item_id=None, item_name=None):
        self.id, self.name, self.match = mon_item_matching(bot, item_id, item_name, bot.item_names)
        self.emote = ""
        self.dp_emote = None
        self.img = bot.config.mon_icon_repo + f"rewards/reward_{self.id}_1.png"
    
    async def get_emote(self, emote_name=None):
        if emote_name is None:
            emote_name = f"i{self.id}"
        await mon_item_emote(self, emote_name)
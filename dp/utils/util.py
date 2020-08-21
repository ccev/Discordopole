import discord
import aiohttp
import json
import difflib
import requests
import json

def get_json_file(filename, mode="r"):
    with open(filename, mode=mode, encoding="utf-8") as f:
        return json.load(f)

async def get_message(bot, message_id, channel_id):
    channel = await bot.fetch_channel(channel_id)
    message = await channel.fetch_message(message_id)
    return message

def isUser(bot, role_ids, channel_id):
    if len(bot.config.cmd_roles[0]) + len(bot.config.cmd_channels[0]) == 0:
        return True
    elif str(channel_id) in bot.config.cmd_channels:
        return True
    else:
        for role in role_ids:
            if str(role.id) in bot.config.cmd_roles:
                return True
        return False

def get_loading_footer(bot, loading_text, area_name=None):
    if area_name is not None:
        if not area_name == bot.locale['all']:
            loading_text = f"{loading_text} • {area_name}"
    
    return loading_text, "https://mir-s3-cdn-cf.behance.net/project_modules/disp/c3c4d331234507.564a1d23db8f9.gif"

class DPEmote():
    def __init__(self, bot, emote=None):
        self.bot = bot
        self.ref = ""
        if emote is None:
            self.emote = None
        else:
            self.emote = emote

    def set_ref(self):
        if self.emote is not None:
            self.ref = f"<:{self.emote.name}:{self.emote.id}>"

    async def create(self, url, emote_name):
        async def download_url(url):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.read()
        
        guild = await self.bot.fetch_guild(self.bot.config.host_server)
        image = await download_url(url)
        self.emote = await guild.create_custom_emoji(name=emote_name, image=image)

        self.set_ref()
        self.bot.custom_emotes[emote_name] = self.ref
        with open("config/emotes.json", "w") as emote_file:
            emote_file.write(json.dumps(self.bot.custom_emotes, indent=4))

    async def delete(self):
        self.set_ref()
        await self.emote.delete()
        self.bot.custom_emotes.pop(self.emote.name)
        with open("config/emotes.json", "w") as emote_file:
            emote_file.write(json.dumps(self.bot.custom_emotes, indent=4))

class Area():
    def __init__(self, bot, areaname):
        stringfence = "-100 -100, -100 100, 100 100, 100 -100, -100 -100"
        namefence = bot.locale['all']
        for area in bot.geofences:
            if area['name'].lower() == areaname.lower():
                namefence = area['name'].capitalize()
                stringfence = ""
                for coordinates in area['path']:
                    stringfence = f"{stringfence}{coordinates[0]} {coordinates[1]},"
                stringfence = f"{stringfence}{area['path'][0][0]} {area['path'][0][1]}"
                break
        self.sql_fence = stringfence
        self.name = namefence

class Stop():
    """
    All information for Pokestops
    """
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
    def __init__(self, gid, lat, lon, name, img, bot, ex=False, team_id=0):
        super().__init__(gid, lat, lon, name, img)
        self.ex = ex
        self.team_id = team_id

        if self.ex:
            self.ex_emote = bot.custom_emotes.get("ex_pass", "")
        else:
            self.ex_emote = ""

def match(to_be_matched, origin_dict):
    diffs = []
    for item in origin_dict.items():
        diff = difflib.SequenceMatcher(None, to_be_matched.lower(), item[1].lower()).ratio()
        if diff > 0.5:
            diffs.append([diff, item[0], item[1]])
    if len(diffs) == 0:
        diffs.append([0, "0", "?"])
    return (list(reversed(sorted(diffs, key=lambda x: x[0]))))

def mon_item_matching(bot, i_id, i_name, names):
    if i_name is not None:
        i_final = match(i_name, names)[0]
        final_id = int(i_final[1])
        final_name = i_final[2]
        _match = i_final[0]
    elif (i_id is not None) and (i_id != 0):
        final_id = int(i_id)
        final_name = names[str(i_id)]
        _match = 1
    else:
        final_id = 1
        final_name = "?"
        _match = 0
    return final_id, final_name, _match

async def mon_item_emote(item, emote_name):
    item.emote = item.bot.custom_emotes.get(emote_name, "")

    if item.emote == "":
        item.dp_emote = DPEmote(item.bot)
        await item.dp_emote.create(item.img, emote_name)
        item.emote = item.dp_emote.ref

class Mon():
    def __init__(self, bot, mon_id=None, mon_name=None, move_1=1, move_2=1, form=0):
        self.bot = bot
        self.id, self.name, self.match = mon_item_matching(bot, mon_id, mon_name, bot.mon_names)
        self.move_1 = self.Move(bot, move_1)
        self.move_2 = self.Move(bot, move_2)
        self.form = self.Form(bot, self.id, form)
        self.emote = ""
        self.dp_emote = None
            
        self.img = bot.config.mon_icon_repo + f"pokemon_icon_{str(self.id).zfill(3)}_{str(self.form.id).zfill(2)}.png"

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
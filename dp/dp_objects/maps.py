import discord
import requests

from io import BytesIO
from tileserver import Tileserver

class StaticMap:
    def __init__(self, tileserver_url):
        if not tileserver_url:
            self.use = False
        else:
            self.use = True
            self.tileserver = Tileserver(tileserver_url)
        self.trash_channel = None

    async def multiples(self, objs):
        if len(objs) == 0:
            return ""
        if not self.use:
            return ""

        staticmap = self.tileserver.staticmap(
            style="osm-bright",
            width=1000,
            height=600,
            scale=1
        )
        for obj in objs:
            staticmap.add_marker(url=obj.img, lat=obj.lat, lon=obj.lon, width=32, height=32, x_offset=0, y_offset=0)

        staticmap.auto_position()
        result = requests.post(staticmap.tileserver.base_url+"staticmap", json=staticmap.get_dict())
        stream = BytesIO(result.content)
        image_msg = await self.trash_channel.send(file=discord.File(stream, filename="staticmap.png"))
        static_map = image_msg.attachments[0].url
        stream.close()

        return static_map
    
    class StaticMapObject():
        def __init__(self, lat, lon, img):
            self.lat = lat
            self.lon = lon
            self.img = img

    async def quest(self, quests):
        objs = []
        for quest in quests:
            objs.append(self.StaticMapObject(quest.stop.lat, quest.stop.lon, quest.reward.img))
        return await self.multiples(objs)

    async def raid(self, raids):
        objs = []
        for raid in raids:
            objs.append(self.StaticMapObject(raid.gym.lat, raid.gym.lon, raid.boss.img))
        return await self.multiples(objs)

    """async def grunt(self, raids):
        if len(raids) == 0:
            return ""
        objs = []
        for grunt in grunts:
            objs.append(self.StaticMapObject(grunt.stop.lat, grunt.stop.lon, grunt.emote, raid.boss.img))
        return await self.multiples(objs)"""

class MapUrl:
    def __init__(self, frontend, url):
        self.frontend = frontend
        self.url = url

    def generic(self, obj, what):
        if self.frontend == "pmsf":
            url = f"{self.url}?lat={obj.lat}&lon={obj.lon}&zoom=18&{what}Id={obj.id}"
        elif self.frontend == "rdm":
            url = f"{self.url}@{what}/{obj.id}"
        else:
            url = f"{self.url}?lat={obj.lat}&lon={obj.lon}&zoom=18"

        return url

    def stop(self, stop):
        if self.frontend == "pmsf":
            what = "stop"
        else:
            what = "pokestop"

        return self.generic(stop, what)

    def gym(self, gym):
        return self.generic(gym, "gym")
import math
import discord
import os
import urllib.request
import requests
import json

from io import BytesIO

class StaticMap:
    def __init__(self, bot, trash_channel):
        self.provider = bot.config.static_provider
        self.key = bot.config.static_key
        self.trash_channel = trash_channel
        self.icons = bot.config.mon_icon_repo
        self.bot = bot

    def get_zoom(self, ne, sw, width, height, tile_size):
        ne = [c * 1.06 for c in ne]
        sw = [c * 1.06 for c in sw]

        if ne == sw:
            return 17.5

        def latRad(lat):
            sin = math.sin(lat * math.pi / 180)
            rad = math.log((1 + sin) / (1 - sin)) / 2
            return max(min(rad, math.pi), -math.pi) / 2

        def zoom(px, tile, fraction):
            return round(math.log((px / tile / fraction), 2), 2)

        lat_fraction = (latRad(ne[0]) - latRad(sw[0])) / math.pi

        angle = ne[1] - sw[1] 
        if angle < 0:
            angle += 360
        lon_fraction = angle / 360

        lat_zoom = zoom(height, tile_size, lat_fraction)
        lon_zoom = zoom(width, tile_size, lon_fraction)

        return min(lat_zoom, lon_zoom)

    async def multiples(self, objs):
        if not self.bot.config.use_static:
            return ""

        width = 1000
        height = 600
        min_lat = min([obj.lat for obj in objs])
        max_lat = max([obj.lat for obj in objs])
        min_lon = min([obj.lon for obj in objs])
        max_lon = max([obj.lon for obj in objs])
        ne = [max_lat, max_lon]
        sw = [min_lat, min_lon]      
        center_lat = min_lat + ((max_lat - min_lat) / 2)
        center_lon = min_lon + ((max_lon - min_lon) / 2)

        if self.provider == "mapbox":
            zoom = self.get_zoom(ne, sw, width, height, 512)

            static_map = "https://api.mapbox.com/styles/v1/mapbox/outdoors-v11/static/"

            for obj in objs:
                img = f"https%3A%2F%2Fcdn.discordapp.com%2Femojis%2F{obj.emote}.png%3Fsize=32"
                static_map += f"url-{img}({obj.lon},{obj.lat}),"

            static_map = static_map[:-1]
            static_map = f"{static_map}/{center_lon},{center_lat},{zoom}/{width}x{height}?access_token={self.key}"

            urllib.request.urlretrieve(static_map, "quest_static_map_temp.png")
            image_msg = await self.trash_channel.send(file=discord.File("quest_static_map_temp.png"))
            static_map = image_msg.attachments[0].url
            os.remove("quest_static_map_temp.png")

        elif self.provider == "tileserver":
            zoom = self.get_zoom(ne, sw, width, height, 256)

            data = {
                "style": "osm-bright",
                "latitude": center_lat,
                "longitude": center_lon,
                "zoom": zoom,
                "width": width,
                "height": height,
                "scale": 1,
                "markers": [

                ]
            }
            for obj in objs:
                data["markers"].append(
                    {
                        "url": obj.img,
                        "height": 32,
                        "width": 32,
                        "x_offset": 0,
                        "y_offset": 0,
                        "latitude": obj.lat,
                        "longitude": obj.lon
                    }
                )

            result = requests.post(f"{self.key}staticmap", json=data)
            stream = BytesIO(result.content)
            image_msg = await self.trash_channel.send(file=discord.File(stream, filename="map.png"))
            static_map = image_msg.attachments[0].url
            stream.close()

        return static_map
    
    class StaticMapObject():
        def __init__(self, lat, lon, emote, img):
            self.lat = lat
            self.lon = lon
            self.emote = emote[:-1].split(':')[2]
            self.img = img

    async def quest(self, rewards):
        if len(rewards) == 0:
            return ""
        objs = []
        for reward in rewards:
            objs.append(self.StaticMapObject(reward.stop.lat, reward.stop.lon, reward.item.emote, reward.item.img))
        return await self.multiples(objs)

    async def raid(self, raids):
        if len(raids) == 0:
            return ""
        objs = []
        for raid in raids:
            objs.append(self.StaticMapObject(raid.gym.lat, raid.gym.lon, raid.boss.emote, raid.boss.img))
        return await self.multiples(objs)

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
            what = pokestop

        return self.generic(stop, what)

    def gym(self, gym):
        return self.generic(gym, "gym")
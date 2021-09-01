import math
import discord
import os
import urllib.request
import requests
import json

from io import BytesIO

class static_map:
    def __init__(self, provider, key, trash_channel, icons):
        self.provider = provider
        self.key = key
        self.trash_channel = trash_channel
        self.icons = icons

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

    async def quest(self, lat, lon, items, mons, custom_emotes):
        width = 1000
        height = 600
        ne = [max(lat), max(lon)]
        sw = [min(lat), min(lon)]       
        center_lat = min(lat) + ((max(lat) - min(lat)) / 2)
        center_lon = min(lon) + ((max(lon) - min(lon)) / 2)
        if self.provider == "mapbox":
            zoom = self.get_zoom(ne, sw, width, height, 512)

            static_map = "https://api.mapbox.com/styles/v1/mapbox/outdoors-v11/static/"
            for mon_id, mon_lat, mon_lon in mons:
                mon_img = custom_emotes[f"m{mon_id}"]
                mon_img = mon_img[:-1].split(":")
                mon_img = f"https%3A%2F%2Fcdn.discordapp.com%2Femojis%2F{mon_img[2]}.png%3Fsize=32"
                static_map = f"{static_map}url-{mon_img}({mon_lon},{mon_lat}),"
            for item_id, item_lat, item_lon in items:
                item_img = custom_emotes[f"i{item_id}"]
                item_img = item_img[:-1].split(":")
                item_img = f"https%3A%2F%2Fcdn.discordapp.com%2Femojis%2F{item_img[2]}.png%3Fsize=32"
                static_map = f"{static_map}url-{item_img}({item_lon},{item_lat}),"

            static_map = static_map[:-1]
            static_map = f"{static_map}/{center_lon},{center_lat},{zoom}/{width}x{height}?access_token={self.key}"

            urllib.request.urlretrieve(static_map, "quest_static_map_temp.png")
            image_msg = await self.trash_channel.send(file=discord.File("quest_static_map_temp.png"))
            static_map = image_msg.attachments[0].url
            os.remove("quest_static_map_temp.png")

        elif self.provider == "tileserver":
            zoom = self.get_zoom(ne, sw, width, height, 256)

            data = {"style": "osm-bright","latitude": center_lat,"longitude": center_lon,"zoom": zoom,"width": width,"height": height,"scale": 1,"markers": []}
            for mon_id, mon_lat, mon_lon in mons:
                data["markers"].append({"url": f"{self.icons}pokemon_icon_{str(mon_id).zfill(3)}_00.png","height": 32,"width": 32,"x_offset": 0,"y_offset": 0,"latitude": mon_lat,"longitude": mon_lon})
            for item_id, item_lat, item_lon in items:
                data["markers"].append({"url": f"{self.icons}rewards/reward_{item_id}_1.png","height": 32,"width": 32,"x_offset": 0,"y_offset": 0,"latitude": item_lat,"longitude": item_lon})

            result = requests.post(f"{self.key}staticmap", json=data, headers={"content-type": "application/json;charset=utf-8"})
            stream = BytesIO(result.content)
            image_msg = await self.trash_channel.send(file=discord.File(stream, filename="map.png"))
            static_map = image_msg.attachments[0].url
            stream.close()

        return static_map

class map_url:
    def __init__(self, frontend, url):
        self.frontend = frontend
        self.url = url

    def quest(self, lat, lon, stop_id):
        if self.frontend == "pmsf":
            quest_url = f"{self.url}?lat={lat}&lon={lon}&zoom=18&stopId={stop_id}"
        elif self.frontend == "rdm":
            quest_url = f"{self.url}@pokestop/{stop_id}"
        else:
            quest_url = f"{self.url}?lat={lat}&lon={lon}&zoom=18"

        return quest_url
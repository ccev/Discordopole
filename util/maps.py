import math

class static_map:
    def __init__(self, provider, key):
        self.provider = provider
        self.key = key

    def get_zoom(self, west, east, width):
        if west == east:
            zoom = 17.5
            return zoom
        east = east * 1.06
        west = west * 1.06
        tile_width = 512
        angle = east - west
        if angle < 0:
            angle += 360

        zoom = round(math.log((width * 360 / angle / tile_width), 2), 2)
        return zoom

    def quest(self, lat, lon, items, mons, custom_emotes):
        width = 1000
        height = 600
        static_map = ""
        if self.provider == "mapbox":
            zoom = self.get_zoom(min(lon), max(lon), width)
            center_lat = min(lat) + ((max(lat) - min(lat)) / 2)
            center_lon = min(lon) + ((max(lon) - min(lon)) / 2)

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

        return static_map

class map_url:
    def __init__(self, frontend, url):
        self.frontend = frontend
        self.url = url

    def quest(self, lat, lon, stop_id):
        if self.frontend == "pmsf":
            quest_url = f"{self.url}?lat={lat}&lon={lon}&zoom=18&stopId={stop_id}"
        elif self.frontend == "rdm":
            quest_url = f"{self.url}@pokestop/:{stop_id}"
        else:
            quest_url = f"{self.url}?lat={lat}&lon={lon}&zoom=18"

        return quest_url

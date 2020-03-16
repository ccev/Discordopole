class static_map:
    def __init__(self, provider, url):
        self.provider = provider
        self.url = url

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
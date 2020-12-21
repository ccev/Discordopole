from dp.dp_objects import dp

class Area():
    def __init__(self, areaname):
        stringfence = "-100 -100, -100 100, 100 100, 100 -100, -100 -100"
        namefence = dp.files.locale['all']
        for area in dp.files.geofences:
            if area['name'].lower() == areaname.lower():
                namefence = area['name'].capitalize()
                stringfence = ""
                for coordinates in area['path']:
                    stringfence = f"{stringfence}{coordinates[0]} {coordinates[1]},"
                stringfence = f"{stringfence}{area['path'][0][0]} {area['path'][0][1]}"
                break
        self.sql_fence = stringfence
        self.name = namefence
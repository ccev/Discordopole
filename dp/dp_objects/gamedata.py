import math
import re
import requests

class GameData:
    def __init__(self, config_locale):
        self.protos = requests.get("https://raw.githubusercontent.com/Furtif/POGOProtos/master/base/base.proto").text
        self.item_ids = self.get_proto("Item")
        self.mon_ids = self.get_proto("HoloPokemonId")
        self.move_ids = self.get_proto("HoloPokemonMove")
        self.form_ids = self.get_proto("Form")
        self.costume_ids = self.get_proto("Costume")

        self.mon_forms = {}
        for proto_id, mon_id in self.mon_ids.items():
            if "NIDORAN" in proto_id:
                proto_id = proto_id.replace("_FEMALE", "").replace("_MALE", "")
            forms = [{
                "proto": proto_id,
                "id": "00"
            }]
            for form_proto, form_id in self.form_ids.items():
                if proto_id in form_proto:
                    forms.append({
                        "proto": form_proto,
                        "id": int(form_id)
                    })
            self.mon_forms[int(mon_id)] = {
                "forms": forms
            }

        languages = {
            "de": "german",
            "es": "spanish",
            "fr": "french"
        }
        lang = languages.get(config_locale, "english")

        raw_locale = requests.get(f"https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/JSON/i18n_{lang}.json").json()["data"]
        locale = {}
        for i in range(0, len(raw_locale), 2):
            locale[raw_locale[i]] = raw_locale[i+1]
        
        self.item_locale = {}
        for proto_id, _id in self.item_ids.items():
            self.item_locale[_id] = locale.get(proto_id.lower() + "_name", "?")
        
        self.mon_locale = {}
        for _id in self.mon_ids.values():
            self.mon_locale[int(_id)] = locale.get("pokemon_name_" + str(_id).zfill(4), "?")
        
        self.move_locale = {}
        for _id in self.move_ids.values():
            self.move_locale[_id] = locale.get("move_name_" + str(_id).zfill(4), "?")


        raw_gamemaster = requests.get("https://raw.githubusercontent.com/PokeMiners/game_masters/master/latest/latest.json").json()
        self.gm_base_stats = {}
        for template in raw_gamemaster:
            templateid = template["templateId"]
            if re.search(r"^V\d{4}_POKEMON_.*", templateid):
                try:
                    self.gm_base_stats[re.sub(r"^V\d{4}_POKEMON_", "", templateid)] = template["data"]["pokemonSettings"]["stats"]
                except:
                    pass
        
        self.raidcp = {}
        for mon_id, data in self.mon_forms.items():
            for form in data["forms"]:
                try:
                    cps = []
                    for cp in [20, 25]:
                        cps.append(self.calculate_cp(cp, self.gm_base_stats[form["proto"]], (15, 15, 15)))
                    self.raidcp[str(mon_id) + "_" + str(form["id"])] = cps
                except:
                    pass

        self.available_grunts = {}
        for gid, data in requests.get("https://raw.githubusercontent.com/ccev/pogoinfo/info/grunts.json").json().items():
            encounters = data.get("encounters", {}).get("first", [])
            if data.get("second_reward", False):
                encounters += data.get("encounters", {}).get("second", [])
            #encounters = [int(e.split("_")[0]) for e in encounters]
            self.available_grunts[int(gid)] = encounters

        type_to_gid = {
            1: [30, 31],
            2: [16, 17],
            3: [20, 21],
            4: [32, 33],
            5: [24, 25],
            6: [36, 37],
            7: [6, 7],
            8: [47, 48],
            9: [28, 29],
            10: [18, 19],
            11: [38, 39],
            12: [22, 23],
            13: [49, 50],
            14: [34, 35],
            15: [26, 27],
            16: [12, 13],
            17: [30, 31],
            18: [14, 15]
        }
        self.grunt_to_type = {}
        for tid, gids in type_to_gid.items():
            for gid in gids:
                self.grunt_to_type[gid] = tid

    def get_proto(self, enum):
        proto = re.findall(f"enum {enum} "+r"{[^}]*}", self.protos)[0]
        proto = proto.replace("\t", "")

        final = {}
        proto = proto.split("{\n")[1].split("\n}")[0]
        for entry in proto.split("\n"):
            k = entry.split(" =")[0]
            v = entry.split("= ")[1].split(";")[0]
            final[k] = v
        return final

    def calculate_cp(self, level, basestats, iv):
        multipliers = {
            10: 0.422500014305115,
            15: 0.517393946647644,
            20: 0.597400009632111,
            25: 0.667934000492096
        }

        multiplier = multipliers.get(level)
        attack = basestats["baseAttack"] + iv[0]
        defense = basestats["baseDefense"] + iv[1]
        stamina = basestats["baseStamina"] + iv[2]
        return math.floor((attack * defense**0.5 * stamina**0.5 * multiplier**2) / 10)

if __name__ == "__main__":
    gamedata = GameData("de")
    print(gamedata.mon_ids)
import ast
import difflib

class details(object):
    def __init__(self, mon_name, lang):
        if not lang == "de":
            lang = "en"
        data = ast.literal_eval(open(f"data/mon_names/{lang}.txt", "r").read())

        org_name = str(mon_name)

        diffs = []
        for pname in data.keys():
            diff = difflib.SequenceMatcher(None, pname.lower(), mon_name.lower()).ratio()

            data_tuple = (pname.lower(), diff)
            diffs.append(data_tuple)

        sorted_list = list(reversed(sorted(diffs, key=lambda x: x[1])))
        result = sorted_list[0]

        if result[1] < 0.76:

            for pname in data.keys():
                if pname.lower().startswith(name.lower()):
                    result = [pname, difflib.SequenceMatcher(None, pname.lower(), name.lower()).ratio()]
                    break

        result_id = data[result[0]]
        org_result_id = data[result[0]]

        result_name = "?"
        for aname, aid in data.items():
            if str(aid) == str(org_result_id):
                result_name = aname.title()

        self.name = result_name
        self.id = int(result_id)
        self.icon = f"https://raw.githubusercontent.com/whitewillem/PogoAssets/resized/no_border/pokemon_icon_{str(result_id).zfill(3)}_00.png"

    def id(mon_id, lang):
        if not lang == "de":
            lang = "en"
        data = ast.literal_eval(open(f"data/mon_names/{lang}.txt", "r").read())
        for aname, aid in data.items():
            if str(aid) == str(mon_id):
                mon_name = aname.title()
        return mon_name
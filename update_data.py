import requests
import json

latest_verion = "0.179.2"

# supported languages: de, en, es, fr, pl

languages = {
    "de": "german",
    "en": "english",
    "es": "spanish",
    "fr": "french"
}
supported = ["de", "en", "es", "fr"]

locales = []

print("Getting language files from Pokeminers and Protos")
for l in supported:
#for l in ["de"]:
    r = requests.get(f"https://raw.githubusercontent.com/PokeMiners/pogo_assets/master/Texts/Latest%20APK/i18n_{languages[l]}.json")
    locales.append(r.json()["data"])

#r = requests.get(f"https://raw.githubusercontent.com/Furtif/POGOProtos/master/base/v{latest_verion}.proto")
r = requests.get("https://raw.githubusercontent.com/Furtif/POGOProtos/master/src/POGOProtos/Inventory/Item/ItemId.proto")
item_protos = r.text

# proto forms: https://github.com/Furtif/POGOProtos/blob/master/src/POGOProtos/Enums/Form.proto

print("Done. Going through them now")

item_names = {}
# ATTENTION: THIS MAY NOT WORK WHEN OBFUSCATION HITS THIS FILE
items_p = item_protos.split("{")[1].split("}")[0].split(";\n")[:-1]
for item in items_p:
    parts = item.split(" = ")
    item_id = parts[1]
    item_name = parts[0].split("ITEM_")[1].lower()
    item_names[item_name] = item_id


mon_names = {}
moves = {}
items = {}

for i in range(4):
    locale = locales[i]
    for index in range(0, len(locale), 2):
        if "pokemon_name_" in locale[index]:
            mon_id = int(locale[index].split("pokemon_name_")[1])
            mon_names[mon_id] = locale[index+1]
        elif "move_name_" in locale[index]:
            move_id = int(locale[index].split("move_name_")[1])
            moves[move_id] = locale[index+1]
        elif locale[index] in [f"item_{item_name}_name" for item_name in item_names.keys()]:
            item_name = locale[index].split("item_")[1].split("_name")[0]
            item_id = item_names[item_name]
            items[item_id] = locale[index+1]

    with open(f"data/mon_names/{supported[i]}.json", "w+") as f:
        f.write(json.dumps(mon_names, indent=4))
    with open(f"data/moves/{supported[i]}.json", "w+") as f:
        f.write(json.dumps(moves, indent=4))
    with open(f"data/items/{supported[i]}.json", "w+") as f:
        f.write(json.dumps(items, indent=4))
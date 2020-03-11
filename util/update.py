import json

def update(boards, locale):
    print("Looking for updates")

    count = 0
    for board in boards['raids']:
        if not "title" in board:            
            boards['raids'][count]['title'] = locale['raids']
            print("Updated title for Raid Board")
        if not "ex" in board:
            boards['raids'][count]['ex'] = False
            print("Updated ex for Raid Board")
        count += 1
        
    for board in boards['raid_channels']:
        continue

    count = 0    
    for board in boards['eggs']:
        if not "title" in board:            
            boards['eggs'][count]['title'] = locale['eggs']
            print("Updated title for Egg Board")
        if not "ex" in board:
            boards['eggs'][count]['ex'] = False
            print("Updated ex for Egg Board")
        count += 1

    count = 0     
    for board in boards['stats']:
        if not "title" in board:            
            boards['stats'][count]['title'] = locale['stats']
            print("Updated title for Stat Board")
        count += 1


    with open("config/boards.json", "w") as f:
        f.write(json.dumps(boards, indent=4))

    return boards

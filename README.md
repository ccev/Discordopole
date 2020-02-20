# Discordopole

This project is still under heavy development. So clone with confidence and join https://discord.gg/cnT8Dmz to get updates and help with developing. Thank you

python3.6 will work. not tested with other version. definitely not compatible with older versions

## Setup

- `cp -r config_example config` to copy the config_example folder to a folder named config
- Install requirements.txt
- Fill in config.ini in that config folder
- Trash channel = A channel in which only images will be sent to (to upload them to Discord and then use them in embeds)
- Set up geofences in geofence.json. It's the exact same format Poracle uses so you can just copy the file from there
- Run the bot with `python3 discordopole.py`
- Invite it to your server and give it Admin perms (which perms exactly will follow here)

## Boards
Boards are message that update automatically. Right now, you can have egg and raid boards which show the current eggs/raids in your area.

- Create boards with `!board create [raid/egg] [area name] [levels seperated with , (e.g. 1,3,4)]`
- You can also just `!board create` to get an empty board and put in everything manually in config/boards.json
- All boards are stored in config/boards.json. You can edit, remove and create your configs there.
- `!board delete [message id]` to delete a board with that Message ID. Removed it from config/boards.json and deletes the message

Due to Disocrd limits, Boards are limited to 23 (or so) entries. That should be enough for an area with ~130 gyms.

## Stats

- `!pokemon [pokemon name] [area name] [time]` to get pokemon stats.
- `!gyms [area name] [time]` to get gym stats.

area name and time are optional parameters. Area name has to be exact name from config/geofence.json. Time is really smart and can be anything. e.g. "3 days", "1. 1. 2019" or "2/2"

## Emotes
Some messages need custom emotes. To properly configure them:

- Create an extra server and invite your bot to it. Or just use a throwaway server you already have. Just make sure there are no emotes on it you care about
- `!get emotes` and follow what it says.
- Discord Bots basically have free nitro. So the bot will be able to use those emotes everywhere

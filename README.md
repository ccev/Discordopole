![](https://media.discordapp.net/attachments/523253670700122144/694301358018396202/dp_maybee.png)

Discordopole takes what [Worldopole](https://github.com/brusselopole/Worldopole) left behind and puts it into Discord. The goal is to allow your users to get easy access to useful data.

- Supports **MAD** and **RDM**
- Written with language support in mind. Supports **English**, **German**, **French**, **Spanish** and **Polish**

### Links
- [**Wiki**](https://github.com/ccev/Discordopole/wiki) - Getting started, detailed feature overview and more.
- [**Discord**](https://discord.gg/cnT8Dmz) - Support, announcements and planned features.

### Features
There are two types of frontend features:
- Boards: messages that always stay updated with latest information
- Commands: allow users to get useful information they want

Screenshots and more information: [Board Wiki Page](https://github.com/ccev/Discordopole/wiki/Boards) and [Command Wiki Page](https://github.com/ccev/Discordopole/wiki/Commands)

### Added Features in this branch
you will need to change emote repo in config/config.ini to `emote_repo = https://raw.githubusercontent.com/idna-ved/dp_emotes/master/` and use `!get emote` again in your trash server to get those new emotes

Stat Boards:
- lure_amount: total amount of active lures
- lure_types: amount of different lure types

![](http://puu.sh/FKtb3/a2c953f2a8.png)

- raid_lvl_1_active: amount of active lvl 1 raids
- raid_lvl_2_active: amount of active lvl 2 raids
- raid_lvl_3_active: amount of active lvl 3 raids
- raid_lvl_4_active: amount of active lvl 4 raids
- raid_lvl_5_active: amount of active lvl 5 raids

you can use `!board create stats area raid lvl all` instead of `!boards create stats all raid lvl 1, raid lvl 2, raid lvl 3, raid lvl 4, raid lvl 5` to show lvl 1-5 raids

- egg_lvl_1_active: amount of active lvl 1 eggs
- egg_lvl_2_active: amount of active lvl 2 eggs
- egg_lvl_3_active: amount of active lvl 3 eggs
- egg_lvl_4_active: amount of active lvl 4 eggs
- egg_lvl_5_active: amount of active lvl 5 eggs

you can use `!board create stats area egg lvl all` instead of `!boards create stats all egg lvl 1, egg lvl 2, egg lvl 3, egg lvl 4, egg lvl 5` to show lvl 1-5 eggs

![](http://puu.sh/FKteB/14f6d3ffdd.png)

- hundos_active: amount of active hundos
- hundos_today: total amount of hundos today
- scanned_active: amount of active scanned mons
- scanned_today: total amount of scanned mons today

![](http://puu.sh/FKvvn/a37a768f4b.png)

other:
- neutral gyms for gym_teams ![](http://puu.sh/FKtrr/d7ff1ccf4c.png)
- select timeframe without area for command !pokemon

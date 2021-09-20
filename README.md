## This repo is no longer maintained

Due to a lack of motivation and time, I've decided to archive most of my repos. At the time of writing this, it's still fully functional.

I hate what Discordopole has become. I love the idea but the work has been super messy. Here's a short hisotry:
- I liked Worldopole but it was super outdated and no one would've used it anyway since all my users prefer using Discord over dedicated websites
- So I started to convert some of Worldopole features to Discord (master branch)
- At the time I sucked at coding (still do, but it's even worse back then) so the project quickly became hard to mainatin and I lost motivation on it
- Andy picked it up, hacked in a lot of features than I didn't really like (develop branch)
- I started rewriting it on develop-develop. That rewrite provides a great base imo and I actually have it running. But it's mainly missing Stats stuff (that I don't care about) and documenation. Else it's pretty good
- I stopped working on develop-develop because I first wanted to finish pogodata (now called pogodatapy), so I have a proper base to work with. When that project was nearly finished, I prioritized other stuff. Then pogodatapy got super messy and I started redo-ing that. Quickly lost mootivation on that and now I'm just quitting everything.
- yeah.

- develop-develop has Quest Boards, Raid Boards and Grunt Boards. + Template support, ok-ish commands to manage everything and an Emoji manager that likes to break
- Maybe Discordopole could benefit from a system like I have in my conceptional discordmap repo.
- Stat stuff should be implemented
- Whatever else you can think of. Maybe a Hundo Board. Maybe an Event Boards based on pogoinfo.
- If you like to continue work on this, please DM me on Discord. Would like to talk about it more.

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
you will need to change emote repo in config/config.ini to `emote_repo = https://raw.githubusercontent.com/alexmartz710/dp_emotes/master/` and use `!get emote` again in your trash server to get those new emotes

Stat Boards:
- lure_amount: total amount of active lures
- lure_types: amount of different lure types

![](https://i.imgur.com/sJESVBr.png)

- raid_lvl_1_active: amount of active lvl 1 raids
- raid_lvl_2_active: amount of active lvl 2 raids
- raid_lvl_3_active: amount of active lvl 3 raids
- raid_lvl_4_active: amount of active lvl 4 raids
- raid_lvl_5_active: amount of active lvl 5 raids
- raid_lvl_6_active: amount of active lvl 6 raids

you can use `!board create stats area raid lvl all` instead of `!board create stats area raid lvl 1, raid lvl 2, raid lvl 3, raid lvl 4, raid lvl 5, raid lvl 6` to show lvl 1-6 raids

- egg_lvl_1_active: amount of active lvl 1 eggs
- egg_lvl_2_active: amount of active lvl 2 eggs
- egg_lvl_3_active: amount of active lvl 3 eggs
- egg_lvl_4_active: amount of active lvl 4 eggs
- egg_lvl_5_active: amount of active lvl 5 eggs
- egg_lvl_6_active: amount of active lvl 6 eggs

you can use `!board create stats area egg lvl all` instead of `!board create stats area egg lvl 1, egg lvl 2, egg lvl 3, egg lvl 4, egg lvl 5, egg lvl 6` to show lvl 1-6 eggs

![](https://i.imgur.com/KN0bpiB.png)

- scanned_active: amount of active scanned mons
- scanned_today: total amount of scanned mons today
- average_iv_active: average iv of alle scanned active mons
- average_iv_today: average iv of alle scanned mons of the day
- hundos_active: amount of active hundos
- hundos_today: total amount of hundos today
- iv0_active: amount of active mon with 0% iv
- iv0_today: total amount of mon with 0% iv

![](https://i.imgur.com/TiplrNK.png)

other:
- neutral gyms for gym_teams ![](http://puu.sh/FKtrr/d7ff1ccf4c.png)
- select timeframe without area for command !pokemon
- you can use an alternative pokemon table for pokemon command. you will have to expand your `config.ini`. see `config_example/config.ini`. pokemon command will use alternative table, if timespan start is older than oldest pokemon in main table. 
- new config option `show_used_timespan_in_footer`. if True, footer will show everytime used timespan and area for pokemon command

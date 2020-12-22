from datetime import datetime

class Templates():
    def __init__(self, dp, templates):
        self.dp = dp
        self.templates = templates
        self.locale = dp.files.locale
        self.map_url = dp.map_url

        self.quest_entry = self.get_entry("quest")
        self.raid_board_entry = self.get_entry("raid")
        self.egg_board_entry = self.get_entry("egg")
        self.hundo_board_entry = self.get_entry("hundo")
        self.grunt_board_entry = self.get_entry("grunt")
    
    def get_entry(self, name):
        return self.templates.get("board_entries", {}).get(name, "")

    def quest(self):
        return QuestBoardEntry(self.dp, self.templates)

    def raid_board(self):
        return RaidBoardEntry(self.dp, self.templates)

    def hundo_board(self):
        return HundoBoardEntry(self.dp, self.templates)

    def grunt_board(self):
        return GruntBoardEntry(self.dp, self.templates)

class QuestBoardEntry(Templates):
    def get(self, quest):
        entry = self.quest_entry.format(
            emote=quest.reward.emote,

            stop_name=quest.stop.name,
            short_stop_name=quest.stop.short_name,
            stop_id=quest.stop.id,

            lat=quest.stop.lat,
            lon=quest.stop.lon,
            map_link=self.map_url.stop(quest.stop),

            reward_name=quest.reward.name,
            reward_id=quest.reward.id
        )
        entry += "\n"
        return entry

class RaidBoardEntry(Templates):
    def get(self, raid):
        if raid.egg:
            wanted_entry = self.egg_board_entry

            entry = wanted_entry.format(
                ex_emote=raid.gym.ex_emote,
                boss_emote=raid.boss.emote,

                level=raid.level,
                start=raid.start.strftime(self.dp.files.locale['time_format_hm']),
                end=raid.end.strftime(self.dp.files.locale['time_format_hm']),

                gym_name=raid.gym.name,
                short_gym_name=raid.gym.short_name,
                gym_id=raid.gym.id,

                lat=raid.gym.lat,
                lon=raid.gym.lon,
                map_link=self.map_url.gym(raid.gym),

                boss_name=raid.boss.name,
                boss_id=raid.boss.id
            )
        else:
            wanted_entry = self.raid_board_entry

            entry = wanted_entry.format(
                ex_emote=raid.gym.ex_emote,
                boss_emote=raid.boss.emote,

                level=raid.level,
                start=raid.start.strftime(self.dp.files.locale['time_format_hm']),
                end=raid.end.strftime(self.dp.files.locale['time_format_hm']),

                gym_name=raid.gym.name,
                short_gym_name=raid.gym.short_name,
                gym_id=raid.gym.id,

                lat=raid.gym.lat,
                lon=raid.gym.lon,
                map_link=self.map_url.gym(raid.gym),

                boss_name=raid.boss.name,
                move_1=raid.boss.move_1.name,
                move_2=raid.boss.move_2.name,
                boss_id=raid.boss.id
            )
        entry += "\n"
        return entry

class HundoBoardEntry(Templates):
    def get(self, mon):
        entry = self.hundo_board_entry.format(
            mon_name=mon.name
        )
        return entry

class GruntBoardEntry(Templates):
    def get(self, grunt):
        entry = self.grunt_board_entry.format(
            
        )
        entry += "\n"
        return entry
import json

from dp.dp_objects import dp
from dp.boards.basicboard import Board
from dp.pogo import Mon, Item, Stop

class Quest():
    def __init__(self, reward, stop, amount, task=""):    
        self.reward = reward
        self.stop = stop
        self.amount = amount
        self.task = task

class QuestBoard(Board):
    def __init__(self, board):
        super().__init__(board)
        self.standard_format = {
            "channel_id": "",
            "message_id": "",
            "title": dp.files.locale["quests"],
            "area": "",
            "wait": 2,
            "mons": [],
            "items": [],
            "energy": [],
            "static_map": True
        }
        self.standard_dict()

        self.board["items"] = {iid: Item(iid) for iid in self.board["items"]}
        self.board["mons"] = {mid: Mon(mid) for mid in self.board["mons"]}

    async def get_objs(self):
        self.quests = []
        quests = await dp.queries.execute("active_quests", sql_fence=self.area.sql_fence)

        for quest_json, quest_text, lat, lon, stop_name, stop_id in quests:
            quest_json = json.loads(quest_json)

            if dp.config.db_scan_schema == "rdm":
                mon_id = quest_json[0]["info"].get("pokemon_id", 0)
                item_id = quest_json[0]["info"].get("item_id", 0)
            elif dp.config.db_scan_schema == "mad":
                item_id = quest_json[0]["item"]["item"]
                mon_id = quest_json[0]["pokemon_encounter"]["pokemon_id"]

            reward = self.board["items"].get(item_id)
            if not reward:
                reward = self.board["mons"].get(mon_id)

            if reward:
                quest = Quest(reward, Stop(stop_id, lat, lon, stop_name, img=None), 1, quest_text)
                await quest.reward.get_emote()
                self.quests.append(quest)

        self.new_ids = [quest.stop.id for quest in self.quests]

    async def generate_embed(self):
        template = dp.templates.quest()
        self.static_map = await dp.static_map.quest(self.quests)
        self.generate_text(self.quests, template)
    
    def _get_embed_one_reward(self):
        rewards = self.board["mons"] + self.board["items"]
        if len(rewards) == 1:
            self.embed.set_thumbnail(url=rewards[0].img)
            if self.board.get("title", dp.files.locale["quests"]) == dp.files.locale["quests"]:
                self.board["title"] = rewards[0].name + " " + dp.files.locale["quests"]

    async def generate_empty_embed(self):
        self._get_embed_one_reward()
        loading, load_gif = get_loading_footer(dp.bot, dp.files.locale['loading_quests'], self.area.name)
        self.embed.description = ""
        self.embed.title = self.board["title"]
        self.embed.set_footer(text=loading, icon_url=load_gif)

    async def delete_emotes(self):
        deleted = []
        for quest in self.quests:
            if quest.reward.dp_emote and quest.reward.id not in deleted:
                await quest.reward.dp_emote.delete()
                deleted.append(quest.reward.id)
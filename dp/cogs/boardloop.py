import json
import asyncio

from discord.ext import tasks, commands

from dp.utils.logging import log
from dp.utils.util import get_message
import dp.boards as boards
from dp.dp_objects import dp

SECONDS = 2.0

class Boards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.raidboard_loop.start()
        self.eggboard_loop.start()
        self.questboard_loop.start()

        self.raidboards = self.prepare_board(boards.RaidBoard, "raids", args={"is_egg_board": False})
        self.eggboards = self.prepare_board(boards.RaidBoard, "eggs", args={"is_egg_board": True})
        self.questboards = self.prepare_board(boards.QuestBoard, "quests")

    def prepare_board(self, boardobj, boardtype, args={}):
        result = []
        for board in dp.files.boards.get(boardtype, []):
            obj = boardobj(board, **args)
            result.append(obj)
        return result
        
    async def generic_board(self, board):
        embed = await board.get()
        if not board.is_new:
            return
        message = await get_message(dp.bot, board.board["message_id"], board.board["channel_id"])
        await message.edit(embed=embed)
        await asyncio.sleep(board.board["wait"])

    @tasks.loop(seconds=SECONDS)   
    async def raidboard_loop(self):
        for board in self.raidboards:
            try:
                await self.generic_board(board)
            except Exception as e:
                log.critical(f"Error while updating Raid Board for message {board.board['message_id']}")
                log.exception(e)
    
    @tasks.loop(seconds=SECONDS)   
    async def eggboard_loop(self):
        for board in self.eggboards:
            try:
                await self.generic_board(board)
            except Exception as e:
                log.critical(f"Error while updating Egg Board for message {board.board['message_id']}")
                log.exception(e)
    
    @tasks.loop(hours=1)   
    async def questboard_loop(self):
        for board in self.questboards:
            try:
                await self.generic_board(board)
            except Exception as e:
                log.critical(f"Error while updating Quest Board for message {board.board['message_id']}")
                log.exception(e)
    
    @tasks.loop(seconds=SECONDS)   
    async def statboard_loop(self):
        for board in self.bot.boards.get("stats", []):
            try:
                statboard = boardobj.StatBoard(self.bot, board)
                await statboard.get_stats()

                message = await get_message(self.bot, board["message_id"], board["channel_id"])
                await message.edit(embed=statboard.embed)
                await asyncio.sleep(board["wait"])
            except Exception as e:
                log.critical(f"Error while updating Stat Board for message {board['message_id']}")
                log.exception(e)

    @raidboard_loop.before_loop
    async def before_raid(self):
        await self.bot.wait_until_ready()

    @eggboard_loop.before_loop
    async def before_egg(self):
        await self.bot.wait_until_ready()
    
    @questboard_loop.before_loop
    async def before_quest(self):
        await self.bot.wait_until_ready()

    @statboard_loop.before_loop
    async def before_stats(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(Boards(bot))
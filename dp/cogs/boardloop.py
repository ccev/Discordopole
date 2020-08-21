import discord
import asyncio
import json
import pyshorteners

from discord.ext import tasks, commands
from datetime import datetime, date, timedelta

from dp.utils.logging import log
from dp.utils.util import get_message
import dp.utils.boards as boardobj

SECONDS = 2.0

class Boards(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.raidboard_loop.start()
        self.eggboard_loop.start()
    
    async def generic_board(self, board, obj):
        await obj.get()
        message = await get_message(self.bot, board["message_id"], board["channel_id"])
        await message.edit(embed=obj.embed)
        await asyncio.sleep(board["wait"])

    @tasks.loop(seconds=SECONDS)   
    async def raidboard_loop(self):
        for board in self.bot.boards.get("raids", []):
            try:
                await self.generic_board(board, boardobj.RaidBoard(self.bot, board, is_egg_board=False))
            except Exception as e:
                log.critical(f"Error while updating Raid Board for message {board['message_id']}")
                log.exception(e)
    
    @tasks.loop(seconds=SECONDS)   
    async def eggboard_loop(self):
        for board in self.bot.boards.get("eggs", []):
            try:
                await self.generic_board(board, boardobj.RaidBoard(self.bot, board, is_egg_board=True))
            except Exception as e:
                log.critical(f"Error while updating Egg Board for message {board['message_id']}")
                log.exception(e)
    
    @tasks.loop(hours=1)   
    async def questboard_loop(self):
        for board in self.bot.boards.get("quests", []):
            try:
                await self.generic_board(board, boardobj.QuestBoard(self.bot, board))
            except Exception as e:
                log.critical(f"Error while updating Quest Board for message {board['message_id']}")
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
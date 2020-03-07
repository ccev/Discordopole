import discord
import json
import asyncio



async def raid_channels(bot, queries):
    while not bot.is_closed():
        for board in bot.boards['raid_channels']:
            #area = discordopole.get_area(board["area"])
            raids = await queries.get_active_raids(config, area[0], board["levels"], board["timezone"])
            print(raids)

            await asyncio.sleep(board['wait'])
        await asyncio.sleep(2)
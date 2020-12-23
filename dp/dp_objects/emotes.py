import discord
import requests
import aiohttp

from dp.utils.logging import log

class Emotes:
    def __init__(self, dp):
        self.dp = dp
        self.guild_name = "Discordopole Emotes"
        self.guilds = []
        self.exisiting_emotes = []
        self.standard_emote_names = [name["name"].replace(".png", "") for name in requests.get("https://api.github.com/repos/ccev/dp_emotes/contents").json() if name["name"].endswith(".png")]

    async def initialize(self):
        for guild in self.dp.bot.guilds:
            if guild.name == self.guild_name:
                self.guilds.append(guild)
                for emote in guild.emojis:
                    self.exisiting_emotes.append(emote)
        
        if len(self.guilds) == 0:
            log.info("No Emote Server found, creating one")
            guild = await self.dp.bot.create_guild(self.guild_name)
            self.guilds.append(guild)
        
        for standard_emote_name in self.standard_emote_names:
            if standard_emote_name not in [emote.name for emote in self.exisiting_emotes]:
                self.create_emote(
                    standard_emote_name,
                    f"https://raw.githubusercontent.com/ccev/dp_emotes/master/{standard_emote_name}.png"
                )

    async def cleanup(self, all_guilds=False):
        if all_guilds:
            guilds = self.guilds
        else:
            guilds = self.guilds[-1:]

        for guild in guilds:
            for emote in guild.emojis:
                if emote.name not in self.standard_emote_names:
                    await emote.delete()

    async def create_emote(self, name, image_url):
        guild = [guild for guild in self.guilds if len(guild.emojis) < guild.emoji_limit]
        if len(guild) == 0:
            log.info("No more available emote slots. Removing some from your servers")
            await self.cleanup()
            guild = self.guilds[-1]
        else:
            guild = guild[0]
        image = await self.download_url(image_url)
        emote = await guild.create_custom_emoji(name=name, image=image)
        self.exisiting_emotes.append(emote)
        return emote

    async def get_emote(self, name, image, wanted_type="ref"):
        emote = [e for e in self.exisiting_emotes if e.name == name]
        if len(emote) == 0:
            log.info(f"Creating emote :{emote.name}:")
            wanted_emote = await self.create_emote(name, image)
        else:
            wanted_emote = emote[0]
        
        if wanted_type == "ref":
            return f"<:{wanted_emote.name}:{wanted_emote.id}>"
        else:
            return wanted_emote

    async def download_url(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()

import discord
import requests
import aiohttp

from dp.utils.logging import log

class Emotes:
    def __init__(self, bot, config):
        self.bot = bot
        self.config = config
        self.guild_name = "Discordopole Emotes"
        self.guilds = []
        self.exisiting_emotes = []
        self.standard_emote_names = [name["name"].replace(".png", "") for name in requests.get("https://api.github.com/repos/ccev/dp-assets/contents/emotes").json() if name["name"].endswith(".png")]

    async def initialize(self):
        for guild in self.bot.guilds:
            if guild.name == self.guild_name:
                self.guilds.append(guild)
                for emote in guild.emojis:
                    self.exisiting_emotes.append(emote)
        
        if len(self.guilds) == 0:
            log.info("No Emote Server found, creating one")
            await self.create_guild()
        
        for standard_emote_name in self.standard_emote_names:
            if standard_emote_name not in [emote.name for emote in self.exisiting_emotes]:
                await self.create_emote(
                    standard_emote_name,
                    self.config.asset_repo + "emotes/" + standard_emote_name + ".png"
                )

    async def create_guild(self):
        guild = await self.bot.create_guild(self.guild_name)
        self.guilds.append(guild)

    async def get_channel(self, index=0):
        guild = self.guilds[index]
        if len(guild.text_channels) == 0:
            channel = await guild.create_text_channel("general")
        else:
            channel = guild.text_channels[0]
        return channel

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

    def _get_existing_emote(self, name):
        return [e for e in self.exisiting_emotes if e.name == name]

    def _get_ref(self, emote):
        return f"<:{emote.name}:{emote.id}>"

    def get_standard(self, name):
        return self._get_ref(self._get_existing_emote(name)[0])

    async def get(self, name, image="", wanted_type="ref"):
        emote = self._get_existing_emote(name)
        if len(emote) == 0:
            log.info(f"Creating emote :{name}:")
            wanted_emote = await self.create_emote(name, image)
        else:
            wanted_emote = emote[0]
        
        if wanted_type == "ref":
            return self._get_ref(wanted_emote)
        else:
            return wanted_emote

    async def download_url(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.read()

import json
import aiohttp

from dp.dp_objects import dp


class DPEmote():
    def __init__(self, emote=None):
        self.ref = ""
        if emote is None:
            self.emote = None
        else:
            self.emote = emote

    def set_ref(self):
        if self.emote is not None:
            self.ref = f"<:{self.emote.name}:{self.emote.id}>"

    async def create(self, url, emote_name):
        async def download_url(url):
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    return await response.read()
        
        guild = await dp.bot.fetch_guild(dp.config.host_server)
        image = await download_url(url)
        self.emote = await guild.create_custom_emoji(name=emote_name, image=image)

        self.set_ref()
        dp.files.custom_emotes[emote_name] = self.ref
        with open("config/emotes.json", "w") as emote_file:
            emote_file.write(json.dumps(dp.files.custom_emotes, indent=4))

    async def delete(self):
        self.set_ref()
        await self.emote.delete()
        dp.files.custom_emotes.pop(self.emote.name)
        with open("config/emotes.json", "w") as emote_file:
            emote_file.write(json.dumps(dp.files.custom_emotes, indent=4))
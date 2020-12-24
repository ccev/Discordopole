import discord

from discord.ext import commands

from dp.dp_objects import dp
from dp.utils.logging import log

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.id in dp.config.admins

    async def cog_command_error(self, ctx, error):
        log.error(f"An error occured while trying to execute an Admin Command: {error}")
        log.exception(error)

    async def cog_before_invoke(self, ctx):
        if ctx.invoked_subcommand:
            return
        log.info(f"User @{ctx.author.name}:{ctx.author.discriminator} executed command {ctx.command.name}: {ctx.message.content}")

    async def base_group(self, ctx):
        if ctx.invoked_subcommand is None:
            missing = [c.name for c in ctx.command.walk_commands()]
            await ctx.send(embed=discord.Embed(description=f"Missing/wrong subcommand. Must be one of these: `{', '.join(missing)}`"))

    @commands.group(pass_context=True)
    async def emotes(self, ctx):
        await self.base_group(ctx)

    @emotes.command()
    async def invites(self, ctx):
        text = ""
        for guild in dp.emotes.guilds:
            invites = await guild.invites()
            if len(invites) == 0:
                if len(guild.text_channels) == 0:
                    channel = await guild.create_text_channel("general")
                else:
                    channel = guild.text_channels[0]
                invite = await channel.create_invite()
            else:
                invite = invites[0]
            text += invite.url + "\n"
        await ctx.send(text)

    @emotes.command()
    async def create(self, ctx, amount=1):
        count = 0
        for _ in range(amount):
            try:
                await dp.emotes.create_guild()
                count += 1
            except Exception as e:
                log.error(f"Error while trying to create a new emote server: {e}")
        await ctx.send(embed=discord.Embed(description=f"Created {count} new Emote Servers"))

    @emotes.command()
    async def clean(self, ctx):
        await dp.emotes.cleanup(True)
        await ctx.send(embed=discord.Embed(description="Removed all emotes from your Emote Servers"))

    @commands.command()
    async def empty(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(title="Empty Board", description="")
        message = await ctx.send(embed=embed)
        embed.description = f"```Channel ID: {message.channel.id}\nMessage ID: {message.id}```\n"
        await message.edit(embed=embed)

    @commands.group(pass_context=True)
    async def reload(self, ctx):
        await self.base_group(ctx)

    @reload.command()
    async def boards(self, ctx):
        dp.files.load_boards()
        dp.bot.unload_extension("dp.cogs.boardloop")
        dp.bot.load_extension("dp.cogs.boardloop")
        await ctx.message.add_reaction("✅")

    @reload.command()
    async def gamedata(self, ctx):
        dp.load_gamedata()
        await ctx.message.add_reaction("✅")

def setup(bot):
    bot.add_cog(AdminCommands(bot))
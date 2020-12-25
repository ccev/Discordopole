import json
import discord

from discord.ext import commands

from dp.dp_objects import dp
from dp.utils.logging import log

def list_to_string(conv_list):
    return ",".join(map(str, conv_list))

def get_boards():
    for cog in dp.bot.cogs:
        if cog == "BoardLoop":
            return dp.bot.get_cog(cog)
    return None

def reset_boards():
    dp.files.load_boards()
    dp.bot.unload_extension("dp.cogs.boardloop")
    dp.bot.load_extension("dp.cogs.boardloop")

def match_board(message_id):
    boards = get_boards()
    boards = boards.raidboards + boards.questboards
    return [b for b in boards if b.board["message_id"] == message_id][0]

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
        reset_boards()
        await ctx.message.add_reaction("✅")

    @reload.command()
    async def gamedata(self, ctx):
        dp.load_gamedata()
        await ctx.message.add_reaction("✅")

    @commands.group(pass_context=True)
    async def board(self, ctx):
        await self.base_group(ctx)

    @board.command()
    async def list(self, ctx):
        def standard_string(board):
            return f"[Message({board.message.jump_url})] in {board.channel.mention}"
        
        boards = get_boards()

        raidboards = ""
        for raid in boards.raidboards:
            levels = list_to_string(raid.board["levels"])
            raidboards += f"{standard_string(raid)}\nLevels: `{levels}`\n\n"

        questboards = ""
        for quest in boards.questboards:
            items = list_to_string(quest.board["items"])
            mons = list_to_string(quest.board["mons"])
            energies = list_to_string(quest.board["energy"])
            questboards += f"{standard_string(quest)}\nMons: `{mons}`\nItems: `{items}`\nEnergy: `{energies}`\n\n"
        
        embed = discord.Embed(title="Active Boards")
        embed.add_field(name="Raid Boards", value=raidboards)
        embed.add_field(name="Quest Boards", value=questboards)
        await ctx.send(embed=embed)

    @board.command()
    async def edit(self, ctx, message_id, *args):
        board = match_board(message_id)
        board_dict = board.original_board

        for arg in list(args):
            key, value = arg.split(":")

            if key in board.standard_format.keys():
                standard_type = type(board.standard_format[key])
                if standard_type == bool:
                    if value.lower() == "true":
                        value = True
                    else:
                        value = False

                if standard_type == list:
                    value = value.split(",")
                    try:
                        value = list(map(int, value))
                    except:
                        pass

                if standard_type == int:
                    value = int(value)

                board_dict[key.lower()] = value

        with open("config/boards.json", "r") as board_file:
            old_json = json.load(board_file)
        
        for board_key, board_jsons in old_json.items():
            for i, board_json in enumerate(board_jsons):
                if board_json["message_id"] == message_id:
                    old_json[board_key][i] = board_dict
                    break

        with open("config/boards.json", "w") as board_file:
            board_file.write(json.dumps(old_json, indent=4))

        reset_boards()
        embed = discord.Embed(title="Board edited", description=f"```json\n{json.dumps(board_dict, indent=4)}```")
        await ctx.send(embed=embed)

    @board.command()
    async def show(self, ctx, message_id):
        board = match_board(message_id)
        embed = discord.Embed(title="Board Settings", description=f"```json\n{json.dumps(board.original_board, indent=4)}```")
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(AdminCommands(bot))
import discord

from discord.ext import commands

from dp.utils.commands.generic import NoInput, do_dialog
from dp.utils.commands.board_creation import raid_board, egg_board, stat_board, quest_board

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True)
    async def board(self, ctx):
        return

    @board.command(pass_context=True)
    async def create(self, ctx, board_kind=None):
        embed = discord.Embed(
            title="Let's create a Board"
        )
        message = await ctx.send(embed=embed)

        kinds_of_boards = {
            "raid": raid_board(ctx, message),
            "egg": egg_board(ctx, message),
            "quest": quest_board(ctx, message),
            "stat": stat_board(ctx, message)
        }

        try:
            board_kind = await do_dialog(
                ctx, message,
                "First, tell me what kind of board you want to create.\n\n**Choose from the following:**\n- " + "\n- ".join(kinds_of_boards.keys()),
                kinds_of_boards.keys(),
                "Sorry, `{var}` is not recognized. Please choose from the following:\n- " + "\n- ".join(kinds_of_boards.keys()),
                og_var=board_kind
            )
        except NoInput:
            return
        
        try:
            await kinds_of_boards[board_kind]
        except NoInput:
            await message.delete()
            return

def setup(bot):
    bot.add_cog(AdminCommands(bot))
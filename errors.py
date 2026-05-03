import discord

from discord.ext import commands
from discord import app_commands

# Currently doesn't work, but good idea

class Errors(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        #bot.tree.error(coro = self.__dispatch_to_app_command_handler)

        self.default_error_message = "There is an error."

    @commands.Cog.listener("on_app_command_error")
    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        print("found error!")
        if error == discord.app_commands.CheckFailure:
            interaction.response.send_message(content = f"You don't have permission to use that!\n{error}", ephemeral = True)
        else:
            raise error

async def setup(bot):
    print("error handler loading")
    await bot.add_cog(Errors(bot))
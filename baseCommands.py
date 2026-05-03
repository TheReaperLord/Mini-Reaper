import discord
from discord import app_commands
from discord.ext import commands
import checks

class BaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def extend(self, interaction: discord.Interaction):
        await interaction.response.send_message("Extension")

    @commands.command()
    async def test(self, ctx):
        await ctx.send("Test Recieved")

    @commands.hybrid_command()
    async def hybrid(self, ctx):
        await ctx.send("Hybrid")

    '''@commands.Cog.listener()
    async def on_message(self, message):
        print("Message Detected in Base Commands")'''

    @app_commands.command()
    @checks.is_me()
    async def reload(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        await self.bot.reloadCogs(interaction)
        await interaction.followup.send(content = "success", ephemeral = True)

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def admin_only(self, interaction: discord.Interaction):
        await interaction.response.send_message(content= "hello admin!", ephemeral= True)

async def setup(bot):
    print("baseCommands loading")
    await bot.add_cog(BaseCommands(bot))
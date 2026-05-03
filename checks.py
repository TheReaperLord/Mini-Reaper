import discord
from discord import app_commands

def is_me():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == self.me
    return app_commands.check(predicate)
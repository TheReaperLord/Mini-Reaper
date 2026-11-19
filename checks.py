import discord
from discord import app_commands

import os

def is_me():
    async def predicate(interaction: discord.Interaction):
        return interaction.user.id == os.getenv('ME')
    return app_commands.check(predicate)
import discord
from discord import app_commands

import os

def is_me():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id != os.getenv('ME'):
            print(interaction.user.id)
            print(os.getenv('ME'))

        return interaction.user.id == os.getenv('ME')
    return app_commands.check(predicate)
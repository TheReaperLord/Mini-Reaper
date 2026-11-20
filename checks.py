import discord
from discord import app_commands

import os

def is_me():
    async def predicate(interaction: discord.Interaction):
        if int(interaction.user.id) != int(os.getenv('ME')):
            print(interaction.user.id)
            print(os.getenv('ME'))

        return int(interaction.user.id) == int(os.getenv('ME'))
    return app_commands.check(predicate)
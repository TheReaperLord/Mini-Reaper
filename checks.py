import discord
from discord import app_commands

import os

def is_me():
    def predicate(interaction: discord.Interaction) -> bool:
        return interaction.user.id == os.getenv('ME')
    return app_commands.check(predicate)
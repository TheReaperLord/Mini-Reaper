# -*- coding: utf-8 -*-

# Connects directly to the minecraft server

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions
import asyncio
import server
import os

from mcsmp.client import Client
from mcsmp.schemas import UntypedGameRule


class Minecraft(commands.GroupCog, group_name='minecraft'):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        #Check if user has admin perms
        return ctx.author.guild_permissions.administrator

    @app_commands.command()
    #@app_commands.checks.has_permissions(administrator=True)
    async def activePlayers(self, interaction: discord.Interaction):
        async with Client(os.getenv("MC_HOST"), 25585, os.getenv("MC_SECRET")) as client:
            # Get the currently online players
            players = await client.players.get()
            await interaction.response.send_message(players)
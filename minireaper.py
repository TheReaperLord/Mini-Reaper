# -*- coding: utf-8 -*-

'''
TO DO:
FIX THE VERIFY USERS IN SECRET SANTA. SAVE THE CHANNEL THE ORIGINAL SANTA MESSAGE IS IN
Use new message format
Make santa recognise admins only (maybe?)
create response to SSBegin

Command to show leaderboard of starred users (quick sort)
Prevent checks on servers without starboards

make VM auto update with git?
seperate base commands into own cog, now that they work consistently
better reload command. default to test server, toggle for global
remove reload from start up
auto load cogs from folder
better expected error handling

add minecraft cog
'''

import discord
from discord import app_commands
from discord.ext import commands

import asyncio
import server
import SQLQuery
import os

from dotenv import load_dotenv

load_dotenv()

'''import baseCommands
import starboard
import secretSanta'''


TOKEN = os.getenv('DISCORD_TOKEN')

TEST_SERVER = discord.Object(id = os.getenv('TEST_SERVER'))

cogs = ["errors", "baseCommands", "secretSanta", "starboard"]

class MyClient(commands.Bot):
    user: discord.ClientUser # Supresses an error

    def __init__(self, *, intents, **options):
        super().__init__(command_prefix="!", intents=intents, **options)
        intents.members = True
        intents.message_content = True
        self.tree.on_error = self.on_tree_error
        self.me = os.getenv('ME')

    async def reloadCogs(self, interaction):
        channel = interaction.channel
        async with channel.typing():
            await channel.send(content="Reloading")
            for cog in cogs:
                try:
                    await self.reload_extension(cog)
                except Exception as error:
                    await channel.send(content=f"Failed to load {cog}/n, {error}")
                else:
                    await channel.send(content=f"Successfully loaded {cog}")
            #self.tree.copy_global_to(guild=TEST_SERVER)
            await self.tree.sync(guild=TEST_SERVER)
            await self.tree.sync()
            await channel.send("Loading Complete!")

    async def setup_hook(self):
        print('loading cogs')
        for cog in cogs:
            await self.load_extension(cog)
        #self.tree.copy_global_to(guild=TEST_SERVER)
        await self.tree.sync(guild=TEST_SERVER)
        await self.tree.sync()

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author == client.user:
            return
        
        await self.process_commands(message)
    
    async def on_ready(self):
        await self.setup_hook()
        await client.change_presence(activity = discord.CustomActivity(name = "MK II"))
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        #starboard.client = client
        #secretSanta.client = client
        print('------')

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, discord.app_commands.errors.CheckFailure):
            await interaction.response.send_message(content = f"You don't have permission to use that!\n{error}", ephemeral = True)
        else:
            raise error


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.tree.command()
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(content=f'Hi, {interaction.user.mention}')

client.run(TOKEN)

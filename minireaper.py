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

    async def reloadCogs(self, interaction):
        channel = interaction.channel
        async with channel.typing():
            await channel.send(content="Reloading")
            for cog in cogs:
                try:
                    await self.reload_extension(cog)
                except:
                    await channel.send(content=f"\nFailed to load {cog}", )
                else:
                    await channel.send(content=f"\nSuccessfully loaded {cog}")
            self.tree.copy_global_to(guild=TEST_SERVER)
            await self.tree.sync(guild=TEST_SERVER)
            await self.tree.sync()
            await channel.send("Loading Complete!")

    async def setup_hook(self):
        print('loading cogs')
        for cog in cogs:
            await self.load_extension(cog)
        self.tree.copy_global_to(guild=TEST_SERVER)
        await self.tree.sync(guild=TEST_SERVER)
        await self.tree.sync()

    async def on_message(self, message):
        # we do not want the bot to reply to itself
        if message.author == client.user:
            return

        '''prefix = SQLQuery.getData("SELECT prefix FROM serverConfig WHERE id = {}".format(message.guild.id))
        prefix = str(prefix[0][0]).strip()
        if message.content.startswith(prefix):
            for x in range(len(message.content)):
                if x == " " or "":
                    break
            command = message.content[1:x+1]
            await secretSanta.commands(message, command)'''
        
        await self.process_commands(message)
        
    '''# Registers when an emote is added to a post
    async def on_raw_reaction_add(self, payload):
        if payload.member.id == client.user.id:
            return
    
        # Get message details
        emoji = str(payload.emoji)
        server = payload.guild_id
        channel = await client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        serverInfo = servers[server]
    
        await starboard.starAdd(payload)

        #await secretSanta.addSanta(payload)

    # Updates when reactions are removed
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == client.user.id:
            return
    
        await starboard.starRemove(payload)

        #await secretSanta.removeSanta(payload)'''
    
    async def on_ready(self):
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

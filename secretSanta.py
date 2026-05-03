# -*- coding: utf-8 -*-

from ast import Try
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions
from datetime import datetime
import asyncio
import random
import SQLQuery
import pyodbc

santa = "🎅"

'''async def addSanta(payload):
    emoji = str(payload.emoji)

    santaMessage = SQLQuery.getData("SELECT secretSantaMessage FROM serverConfig WHERE id = {}".format(payload.guild_id))
    santaMessage = santaMessage[0][0]
    
    if payload.message_id == santaMessage and emoji == santa:
        SQLQuery.sendData("INSERT INTO secretSantaParticipants (id, server) VALUES ({0}, {1})".format(payload.member.id, payload.guild_id))'''

'''async def removeSanta(payload):
    emoji = str(payload.emoji)

    santaMessage = SQLQuery.getData("SELECT secretSantaMessage FROM serverConfig WHERE id = {}".format(payload.guild_id))
    santaMessage = santaMessage[0][0]

    if payload.message_id == santaMessage and emoji == santa:
        SQLQuery.sendData("DELETE FROM secretSantaParticipants WHERE id = {0} AND server = {1}".format(payload.user_id, payload.guild_id))'''

async def textcommands(message, command):
    originalMessage = message
    
        
    if command.startswith("sst"):
        secretSantaMembers = SQLQuery.getData("SELECT id FROM secretSantaParticipants WHERE server = {}".format(message.guild.id))
        random.shuffle(secretSantaMembers)
        for i in range(len(secretSantaMembers)):
            secretSanta = await client.fetch_user(secretSantaMembers[i][0])
            if i < len(secretSantaMembers) - 1:
                receiver = secretSantaMembers[i+1][0]
            else:
                receiver = secretSantaMembers[0][0]
            receiver = await client.fetch_user(receiver)
            msg = "{0}'s secret santa is {1}".format(secretSanta.name, receiver.name)
            await message.channel.send(msg)

@app_commands.guild_only()
class secretSanta(commands.GroupCog, group_name='secret-santa'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="begin-secret-santa")
    @app_commands.checks.has_permissions(administrator=True)
    async def createSantaMessage(self, interaction: discord.Interaction, close_date: str):
        santaMessage = await interaction.channel.send(content=""":snowflake: @everyone **SECRET SANTA {0} IS HERE!!!** :snowflake:
    Press here sign up for secret santa.
    Sign ups close on the {1}, followed shortly by your secret santa assignment""".format(datetime.now().year, close_date))
        await santaMessage.add_reaction(santa)
        SQLQuery.sendData("UPDATE serverConfig SET secretSantaMessage = ? WHERE id = ?", santaMessage.id, interaction.guild_id)

    @app_commands.command()
    async def rules(self, interaction: discord.Interaction):
        msg = """# __How *Secret Santa* works:__

1. By __<t:1764466200:D>__, use the command /secret-santa join
2. Everyone’s names are put in a digital hat from which I will draw names for each participant.
3. Whoever gets your name shall be your Secret Santa.
4. Secret Santas can give you any gift including, but not limited to, personal playlists, poems, positive messages, graphic arts, doodles, emotes, recorded musical numbers, recorded messages, memes, and everything in between. Get creative!
5. Put your heart into your gift.
6. On __<t:1766280600:D>__, we will hold the Secret Santa reveals and marvel over all the wonderful gifts!

**NOTE:** __Gifts are strictly non-monetary__, as in gifts should be personally made, not bought.
We have a new feature this year! Use the command /secret-santa set-message to set a personalised message that only your secret santa will see!"""
        await interaction.channel.send(msg)

    async def getReactions(self, interaction):
        SQLQuery.sendData("DELETE FROM secretSantaParticipants WHERE server = ?", interaction.guild_id)
        users = []
        santaMessage = SQLQuery.getData("SELECT secretSantaMessage FROM serverConfig WHERE id = ?", interaction.guild_id)[0][0]
        for reactions in (await self.bot.fetch_message(santaMessage)).reactions:
            if reactions.emoji == "🎅":
                async for user in reactions.users():
                    if not user.bot:
                        users.append(user)
                        SQLQuery.sendData("INSERT INTO secretSantaParticipants (id, server) VALUES (?, ?)", user.id, interaction.guild_id)
        return users

    @app_commands.command(name="debug-reactions", description="debug to check secret santa list")
    @app_commands.checks.has_permissions(administrator=True)
    async def debugReactions(self, interaction: discord.Interaction):
        await interaction.response.send_message(await self.getReactions(interaction))

    @app_commands.command(name="send-dms", description="must be run in same channel as react message")
    @app_commands.checks.has_permissions(administrator=True)
    async def sendDMs(self, interaction: discord.Interaction, real: bool):

        #secretSantaMembers = await self.getReactions(interaction)
        #print(secretSantaMembers)

        await interaction.response.defer(ephemeral=True)

        server = interaction.guild_id
        secretSantaMembers = SQLQuery.getData("SELECT id, message FROM secretSantaParticipants WHERE server = {}".format(server))
        random.shuffle(secretSantaMembers)
        for i in range(len(secretSantaMembers)):
            secretSantaInfo = secretSantaMembers[i]
            secretSanta = secretSantaInfo[0]
            secretSanta = await self.bot.fetch_user(secretSanta)
            if i < len(secretSantaMembers) - 1:
                receiver = secretSantaMembers[i+1]
            else:
                receiver = secretSantaMembers[0]
            receiver_msg = receiver[1]
            receiver = await self.bot.fetch_user(receiver[0])
            msg = "{0}'s secret santa is {1}".format(secretSanta.name, receiver.name)
            SQLQuery.sendData("UPDATE secretSantaParticipants SET gifted = ? WHERE id = ? AND server = ?", secretSanta.id, receiver.id, server)
            await secretSanta.create_dm()
            if real == True:
                print("sending DM")
                await secretSanta.dm_channel.send(msg)
                if receiver_msg != None:
                    await secretSanta.dm_channel.send("They included a message to help you: {}".format(receiver_msg))
            else:
                await interaction.channel.send(msg)
                if receiver_msg != None:
                    await interaction.channel.send("They included a message to help you: {}".format(receiver_msg))
                else:
                    await interaction.channel.send("No Message")
        await interaction.channel.send("Merry Christmas")
        await interaction.followup.send("DMs Sent", ephemeral=True)

    @app_commands.command(name="join", description="Join this year's secret santa!")
    async def join(self, interaction: discord.Interaction):
        # Add them to the database (There should already be a unique constraint so they can't be added twice)
        try:
            SQLQuery.sendData("""
        INSERT INTO secretSantaParticipants (id, server)
        VALUES (?, ?)
        """, interaction.user.id, interaction.guild_id)
        except pyodbc.IntegrityError:
            await interaction.response.send_message("You've already joined secret santa!", ephemeral=True)
        else:
            await interaction.response.send_message("You've joined secret santa!", ephemeral=True)

    @app_commands.command(name="leave", description="Join this year's secret santa!")
    async def leave(self, interaction: discord.Interaction):
        # Remove any entries of this user particpaiting in this server.
        SQLQuery.sendData("DELETE FROM secretSantaParticipants WHERE id = ? AND server = ?", interaction.user.id, interaction.guild_id)
        await interaction.response.send_message("You've left secret santa", ephemeral=True)

    @app_commands.command(name="set-message", description="Set a message for Mini Reaper to send to your secret santa!")
    async def setMessage(self, interaction: discord.Interaction, message: str):
        # If the message wont fit, cut it off so the preview can be accurate)
        if len(message) > 255:
            message = message[0:255]
        # If they're particpating in secret santa, append their message
        SQLQuery.sendData("""
        UPDATE secretSantaParticipants
        SET message = ?
        WHERE id = ? AND server = ?
        """, message, interaction.user.id, interaction.guild_id)
        await interaction.response.send_message("Message set to: {}".format(message), ephemeral=True)

async def setup(bot):
    print("secretSanta loading")
    await bot.add_cog(secretSanta(bot))

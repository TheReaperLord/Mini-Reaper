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

@app_commands.guild_only()
class secretSanta(commands.GroupCog, group_name='secret-santa'):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def setup(self, interaction: discord.Interaction, start_date: int, end_date: int):
        SQLQuery.sendData("DELETE FROM secretSantaParticipants WHERE server = ?", interaction.guild_id)
        msg = """:snowflake: @everyone **SECRET SANTA IS HERE!!!** :snowflake:
# __How *Secret Santa* works:__

1. __<t:{0}:R>__ anyone signed up using the command `/secret-santa join` will be entered. (Please enter again even if you participated last year, I've reset the database)
2. Everyone’s names are put in a digital hat from which I will draw names for each participant.
3. Whoever gets your name shall be your Secret Santa.
4. Secret Santas can give you any gift including, but not limited to, personal playlists, poems, positive messages, graphic arts, doodles, emotes, recorded musical numbers, recorded messages, memes, and everything in between. Get creative!
5. Put your heart into your gift <3
6. __<t:{1}:R>__, we will hold the Secret Santa reveals and marvel over all the wonderful gifts!

**NOTE:** __Gifts are strictly non-monetary__, as in gifts should be personally made, not bought.
Please use the command /secret-santa set-message to set a personalised message that only your secret santa will see!
After last year I upped the character limit massively, so you can enter up to 1000 characters! Use them well""".format(start_date, end_date)
        await interaction.channel.send(msg)
        await interaction.response.send("Message successfully", ephemeral=True)

    @app_commands.command(name="send-dms", description="must be run in same channel as react message")
    @app_commands.checks.has_permissions(administrator=True)
    async def sendDMs(self, interaction: discord.Interaction, real: bool):
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
        # If they're particpating in secret santa, append their message
        SQLQuery.sendData("""
        UPDATE secretSantaParticipants
        SET message = ?
        WHERE id = ? AND server = ?
        """, message, interaction.user.id, interaction.guild_id)
        await interaction.response.send_message("Message set to: {}".format(message), ephemeral=True)

    @app_commands.command(name="check-message", description="Check your secret santa message")
    async def checkMessage(self, interaction: discord.Interaction):
        message = SQLQuery.getData("SELECT message FROM secretSantaParticipants WHERE server = {0} AND id = {1}".format(interaction.guild_id, interaction.user.id))
        await interaction.response.send_message("Message set to: {}".format(message[0][0]), ephemeral=True)

async def setup(bot):
    print("secretSanta loading")
    await bot.add_cog(secretSanta(bot))

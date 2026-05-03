# -*- coding: utf-8 -*-

# Record posts to one table
# Record users to another

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import has_permissions
import asyncio
import server
import SQLQuery
from datetime import datetime


class Starboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Generates the text to go with the embed
    # Stars change as the star count goes up
    async def starboardMessage(self, starCount, channel):
        if starCount > 10:
            starLevel = "🌟"
        elif starCount > 20:
            starLevel = "💫"
        else:
            starLevel = "⭐"

        return "{} {} | <#{}>".format(starLevel, starCount, channel.id)

    # Finds a starboard post based on the id of the original post
    async def get_post_from_db(self, id):
        try:
            message = SQLQuery.getDataDic("SELECT * FROM starboardPosts WHERE sourceID = ?", id)[0]
            return message
        except IndexError:
            return None

    # Get the update the text only of a starboard post. Doesn't effect the embed
    async def update_starboard_post(self, postID, starCount, guildID, postChannel):
        starboardChannel = SQLQuery.getData("SELECT starboard FROM serverConfig WHERE id = ?", guildID)[0][0]
        starChannel = await self.bot.fetch_channel(starboardChannel)
        currentPost = await starChannel.fetch_message(postID)
        newContent = await self.starboardMessage(starCount, postChannel)
        await currentPost.edit(content = newContent)
        # If for some reason the starboard post has been deleted, this will error

    # Creates a new starboard post
    async def new_star_post(self, payload, server, channel, message, serverInfo, starCount):
        author = message.author

        # Generates the text to go with the embed
        msg = await self.starboardMessage(starCount, channel)

        # Generates embed with author details and message content, and link to the message
        embed=discord.Embed(description = message.content, color = 0xffd700)
        embed.set_author(name = author.name, icon_url = author.display_avatar)
        embed.add_field(name = "Original", value = "[Jump!]({})".format(message.jump_url))

        # If message has attachments, add them to the embed
        if len(message.attachments) > 0:
            if "SPOILER" not in message.attachments[0].url:
                embed.set_image(url = message.attachments[0].url)
            else:
                embed.set_image(url = "https://i.redd.it/yvq5a4xboh931.png")

        # Find the star channel in this server and post the message
        starChannel = await self.bot.fetch_channel(serverInfo["starboard"])
        return await starChannel.send(msg, embed=embed)

    async def get_star_count(self, message, emoji):
        reactions = message.reactions
        for reacts in reactions:
            if reacts.emoji == emoji:
                users = [user.id async for user in reacts.users()]
                if message.author.id in users:
                    return reacts.count - 1
                return reacts.count
        return 0
    
    async def update_starred_user(self, author, guildID, extra, adj):
        SQLQuery.sendData('''
        BEGIN TRAN
        UPDATE starboardUsers SET starredPostCount = starredPostCount + ?, stars = stars + ?
        WHERE userID = ? AND guildID = ?
        
        IF @@rowcount = 0
        BEGIN
        INSERT INTO starboardUsers VALUES (?, ?, ?, ?)
        END
        COMMIT TRAN
        ''', extra, adj, author, guildID, author, guildID, extra, adj)
    
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # Get message details
        emoji = str(payload.emoji)
        server = payload.guild_id
        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        try:
            serverInfo = SQLQuery.getDataDic("SELECT star, starThreshold, starboard FROM serverConfig WHERE id = ?", payload.guild_id)[0]
        except IndexError:
            return None
    
        # Check if emoji added was the server's star and that the message author didn't star
        if emoji == serverInfo["star"] and (payload.member != message.author or payload.guild_id == 494055661429063680):
            reaction = message.reactions

            starpost = await self.get_post_from_db(message.id)

            # Gets the total number of star reactions on a message
            stars = await self.get_star_count(message, emoji)

            # Check if message in the database of starred posts, and if not add it with value 1
            if starpost != None:
                print("Updating Database Entry")
                SQLQuery.sendData("UPDATE starboardPosts SET stars = ? WHERE sourceID = ?", stars, message.id)
            else: # If first star ever
                # Create new entry on starboardPosts database, with a single star entry
                #print(f"INSERT INTO starboardPosts VALUES (NULL, {message.id}, {message.author.id}, {payload.guild_id}, {stars}, {message.created_at.strftime('%Y-%m-%d %H:%M:%S')}, {datetime.today().strftime('%Y-%m-%d %H:%M:%S')})")
                print("No Database Entry")
                SQLQuery.sendData("INSERT INTO starboardPosts VALUES (NULL, ?, ?, ?, ?, ?, NULL)", message.id, message.author.id, payload.guild_id, stars, message.created_at)

            extra = 0 # Helper var to track if a new post reached the starboard
            # If the starred post has enough stars to reach starboard, either make a post, or edit the existing one
            if stars >= serverInfo["starThreshold"] or payload.guild_id == 494055661429063680:
                # If not already there, call the helper function to make a new embed post
                if starpost == None or starpost["postID"] == None:
                    newPost = await self.new_star_post(payload, server, channel, message, serverInfo, stars)
                    SQLQuery.sendData("UPDATE starboardPosts SET postID = ?, starTime = ? WHERE sourceID = ?", newPost.id, datetime.today(), message.id)
                    extra = 1
                # Otherwise find the existing message and update the text (REPLACE WITH SQL)
                else:
                    await self.update_starboard_post(starpost["postID"], stars, server, message.channel)

            await self.update_starred_user(message.author.id, server, extra, 1)
    
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        # Check if the removed react is the server's star
        serverInfo = SQLQuery.getDataDic("SELECT star, starThreshold, starboard FROM serverConfig WHERE id = ?", payload.guild_id)[0]
        emoji = str(payload.emoji)
        server = payload.guild_id
        channel = await self.bot.fetch_channel(payload.channel_id) 
        message = await channel.fetch_message(payload.message_id)

        if emoji == serverInfo["star"] and (payload.member != message.author or payload.guild_id == 494055661429063680):
            # Get post info
            starpost = await self.get_post_from_db(payload.message_id)

            extra = 0
            # Only run if the message losing a react is a star post
            if starpost != None:
                
                # Remove 1 star from the record
                stars = await self.get_star_count(message, emoji)
                SQLQuery.sendData("UPDATE starboardPosts SET stars = ? WHERE sourceID = ?", stars, message.id)

                # If 0 stars on post, remove the post from the dictionary (REPLACE WITH SQL)
                if stars <= 0:
                    SQLQuery.sendData("DELETE FROM starboardPosts WHERE sourceID = ?", message.id)
                else:
                    SQLQuery.sendData("UPDATE starboardPosts SET stars = ? WHERE sourceID = ?", stars, message.id)

                # If the post was on the real starboard
                if starpost["postID"] != None:
                    # Get the starboard channel
                    starChannel = await self.bot.fetch_channel(serverInfo["starboard"])
                    # If it no longer deserves to be on starboard, remove it
                    if stars < serverInfo["starThreshold"]:
                        post = await starChannel.fetch_message(starpost["postID"])
                        await post.delete()
                        extra = -1
                    # Otherwise update the starboard post
                    else:
                        await self.update_starboard_post(starpost["postID"], stars, server, message.channel)
        
            await self.update_starred_user(message.author.id, server, extra, -1)

    @app_commands.command(name="starboard-config")
    @app_commands.checks.has_permissions(administrator=True)
    async def starboardConfig(self, interaction: discord.Interaction, starboard_channel: discord.TextChannel, starboard_emoji: str, threshold: int):
        # future expansion, ensure channel works, etc
        SQLQuery.sendData('''
        BEGIN TRAN
        UPDATE serverConfig SET star = ?, starboard = ?, starThreshold = ?
        WHERE id = ?
        
        IF @@rowcount = 0
        BEGIN
        INSERT INTO serverConfig(id, star, starThreshold, starboard) VALUES (?, ?, ?, ?)
        END
        COMMIT TRAN
        ''', starboard_emoji, starboard_channel.id, threshold, interaction.guild_id, interaction.guild_id, starboard_emoji, threshold, starboard_channel.id)
        await interaction.response.send_message(content = "success", ephemeral=True)


async def setup(bot):
    print("starboard loading")
    await bot.add_cog(Starboard(bot))

# SDV Winter 2023 Discord bot
# Written by aquova, 2023

import discord
import db, teams
from client import client
from config import DISCORD_KEY, SNOWMAN_EMOJI, SNOWBALL_EMOJI

@client.event
async def on_ready():
    if client.user:
        print(client.user.name)
        print(client.user.id)
    db.initialize()

@client.event
async def on_guild_available(guild: discord.Guild):
    await client.set_data(guild)
    await client.sync_guild(guild)

@client.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.Member):
    if isinstance(reaction.message.author, discord.User):
        return
    if str(reaction) == SNOWBALL_EMOJI:
        result = teams.throw_snowball(user, reaction.message.author)
        if result[0] != "":
            await client.log.send(result[0])
    elif str(reaction) == SNOWMAN_EMOJI:
        result = teams.build_snowman(user, reaction.message.author)
        if result[0] != "":
            await client.log.send(result[0])

client.run(DISCORD_KEY)

# SDV Winter 2023 Discord bot
# Written by aquova, 2023

import discord
import db
from client import client
from config import DISCORD_KEY

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

client.run(DISCORD_KEY)

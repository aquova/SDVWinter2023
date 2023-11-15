from typing import cast

import discord
from discord.ext import commands

import db, teams
from config import SNOWBALL_LOG
from signup import SignupWidget

class DiscordClient(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="?", intents=intents)

    async def set_data(self, _: discord.Guild):
        self.log = cast(discord.TextChannel, self.get_channel(SNOWBALL_LOG))
        # await self.add_cog(teams.LeaderboardCog(self.log))
        self.add_view(SignupWidget())

    async def sync_guild(self, guild: discord.Guild):
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

client = DiscordClient()

# This should be limited to desired roles in Discord's UI
@client.tree.context_menu(name="Approve")
async def approve_task_context(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_modal(teams.ApproveModal(message))

@client.tree.context_menu(name="Reject")
async def reject_task_context(interaction: discord.Interaction, message: discord.Message):
    # TODO: Send the user a DM that their item was rejected
    await message.add_reaction("x")
    await interaction.response.send_message("Item rejected.", ephemeral=True)

@client.tree.context_menu(name="Award points")
async def award_points_context(interaction: discord.Interaction, user: discord.Member):
    modal = teams.AwardPointsModal(user)
    if modal.is_valid():
        await interaction.response.send_modal(modal)
    else:
        await interaction.response.send_message("That user is not on a team", ephemeral=True)

@client.tree.context_menu(name="Snowball count")
async def snowball_count_context(interaction: discord.Interaction, user: discord.Member):
    if db.get_team(user.id) is not None:
        cnt = db.get_snowballs(user.id)
        await interaction.response.send_message(f"They have {cnt} snowballs remaining", ephemeral=True)
    else:
        await interaction.response.send_message("They are not on a team", ephemeral=True)

@client.tree.context_menu(name="Post signup message")
async def post_signup_context(interaction: discord.Interaction, message: discord.Message):
    await message.channel.send("Choose a team to join!", view=SignupWidget())
    await interaction.response.send_message("Signup message posted!", ephemeral=True)

@client.tree.context_menu(name="Throw snowball")
async def throw_snowball_msg_context(interaction: discord.Interaction, message: discord.Message):
    if isinstance(interaction.user, discord.User) or isinstance(message.author, discord.User):
        return
    output = teams.throw_snowball(interaction.user, message.author)
    if output[0] != "":
        await client.log.send(output[0])
    await interaction.response.send_message(output[1], ephemeral=True)

@client.tree.context_menu(name="Throw snowball")
async def throw_snowball_user_context(interaction: discord.Interaction, user: discord.Member):
    if isinstance(interaction.user, discord.User):
        return
    output = teams.throw_snowball(interaction.user, user)
    if output[0] != "":
        await client.log.send(output[0])
    await interaction.response.send_message(output[1], ephemeral=True)

@client.tree.context_menu(name="Build snowman")
async def build_snowman_msg_context(interaction: discord.Interaction, message: discord.Message):
    if isinstance(interaction.user, discord.User) or isinstance(message.author, discord.User):
        return
    output = teams.build_snowman(interaction.user, message.author)
    if output[0] != "":
        await client.log.send(output[0])
    await interaction.response.send_message(output[1], ephemeral=True)

@client.tree.context_menu(name="Build snowman")
async def build_snowman_user_context(interaction: discord.Interaction, user: discord.Member):
    if isinstance(interaction.user, discord.User):
        return
    output = teams.build_snowman(interaction.user, user)
    if output[0] != "":
        await client.log.send(output[0])
    await interaction.response.send_message(output[1], ephemeral=True)

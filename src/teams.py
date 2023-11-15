from random import choice, randint

import discord
from discord.ext import commands, tasks

import db

YOUR_SNOWMAN_PTS = 5
THEIR_SNOWMAN_PTS = 3

NORMAL_SNOWBALL = -3
CRIT_SNOWBALL = -6
SNOWBALL_FAIL = -1

FAIL_FLAVOR = [
    "their mom was watching",
    "they tripped and fell",
    "it was yellow snow",
    "their shoe was untied",
]

CRIT_FLAVOR = [
    "SMAAAASH",
    "it landed perfectly",
    "they rolled a 20",
    "don't mess around",
]

class ApproveModal(discord.ui.Modal):
    def __init__(self, message: discord.Message):
        super().__init__(title="Approve submission")
        self.message = message
        self.team = db.get_team_name(message.author.id)
        self.input = discord.ui.TextInput(
            label=f"Number of points to award to {self.team}",
            placeholder="0",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.input)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            pts = int(self.input.value)
            submitted = db.add_submission(self.message.author.id, self.message.channel.id)
            if submitted:
                db.add_points_user(self.message.author.id, pts)
                await interaction.response.send_message(f"Approved! {pts} points awarded to {self.team}", ephemeral=True)
                await self.message.add_reaction("ballot_box_with_check")
            else:
                await interaction.response.send_message(f"{str(self.message.author)} has maxed out the number of submissions for this task")
        except ValueError:
            await interaction.response.send_message(f"{self.input.value} is not a number.")

class AwardPointsModal(discord.ui.Modal):
    def __init__(self, user: discord.Member):
        super().__init__(title="Award points")

        self.recipiant = user
        self.team = db.get_team_name(user.id)
        self.input = discord.ui.TextInput(
            label=f"Number of points to add to {self.team}",
            placeholder="0",
            style=discord.TextStyle.short,
            required=True
        )
        self.add_item(self.input)

    def is_valid(self) -> bool:
        return self.team is not None

    async def on_submit(self, interaction: discord.Interaction):
        try:
            pts = int(self.input.value)
            db.add_points_user(self.recipiant.id, pts)
            await interaction.response.send_message(f"{pts} points added to {self.team}", ephemeral=True)
        except ValueError:
            await interaction.response.send_message(f"{self.input.value} is not a number.")

class LeaderboardCog(commands.Cog):
    def __init__(self, log: discord.TextChannel):
        self.post_lb.start()
        self.log = log

    def cog_unload(self) -> None:
        self.post_lb.cancel()

    @tasks.loop(hours=1)
    async def post_lb(self):
        embed = discord.Embed(title="Team Leaderboard", type="rich")
        lb = db.get_leaderboard()
        for team in lb:
            embed.add_field(name=team[1], value=team[2], inline=False)
        await self.log.send(embed=embed)

# Returns two strings, the first is the message to post in the log
# The second is a message to only show to the user. This needs to always exist
def throw_snowball(src_user: discord.Member, target_user: discord.Member) -> tuple[str, str]:
    src_team = db.get_team(src_user.id)
    target_team = db.get_team(target_user.id)
    if src_team is None:
        # We should limit this command to team members only via Discord UI, and never see this
        return ("", "You are not on a team!")
    elif target_team is None:
        return ("", "They are not on a team!")
    elif src_team == target_team:
        return("", "You can't throw a snowball at them! They're on your team!")
    snowballs_remaining = db.get_snowballs(src_user.id)
    if snowballs_remaining == 0:
        return ("", "You don't have any snowballs left!")
    db.use_snowball(src_user.id)
    odds = randint(1, 100)
    output = f"{str(src_user)} threw a snowball at {str(target_user)}"
    if odds < 6: # Fail
        db.add_points(src_team, SNOWBALL_FAIL)
        db.add_points(target_team, SNOWBALL_FAIL)
        output = f"{output}... but {choice(FAIL_FLAVOR)}! Critical failure! {SNOWBALL_FAIL} points to both their teams!"
    elif odds > 95: # Crit
        db.add_points(target_team, CRIT_SNOWBALL)
        output = f"{output}... and {choice(CRIT_FLAVOR)}! Critical hit! {CRIT_SNOWBALL} points to {str(target_user)}'s team!"
    else:
        db.add_points(target_team, NORMAL_SNOWBALL)
        output = f"{output}. {NORMAL_SNOWBALL} points to {str(target_user)}'s team."
    return (output, f"You threw a snowball at {str(target_user)}!")

def build_snowman(src_user: discord.Member, target_user: discord.Member) -> tuple[str, str]:
    src_team = db.get_team(src_user.id)
    target_team = db.get_team(target_user.id)
    if src_team is None:
        return ("", "You are not on a team!")
    elif target_team is None:
        return ("", "They are not on a team!")
    elif src_team == target_team:
        return ("", "You can't build a snowman with them, they're on your team")
    snowballs_remaining = db.get_snowballs(src_user.id)
    if snowballs_remaining == 0:
        return ("", "You don't have any snowballs left!")
    db.use_snowball(src_user.id)
    db.add_points(src_team, YOUR_SNOWMAN_PTS)
    db.add_points(target_team, THEIR_SNOWMAN_PTS)
    return (f"{str(src_user)} and {str(target_user)} made a snowman together. How nice~!", f"You built a snowman with {str(target_user)}!")

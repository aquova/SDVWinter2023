import discord
from config import EVENT_ROLE, PERMANENT_ROLE, TEAMS
import db

class SignupWidgetButton(discord.ui.Button):
    def __init__(self, text: str):
        custom_id = f"team_id:{text}"
        super().__init__(style=discord.ButtonStyle.primary, label=text, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        # This is here mainly to shut up the linter
        if isinstance(interaction.user, discord.User):
            return

        try:
            team_check = db.get_team(interaction.user.id)
            if team_check is not None:
                await interaction.response.send_message("You are already on a team!", ephemeral=True)
                return
            team_info = [t for t in TEAMS if t["name"] == self.label][0]
            db.add_member(interaction.user.id, team_info["id"])
            role_id = team_info["id"]
            team_role = discord.utils.get(interaction.user.guild.roles, id=role_id)
            event_role = discord.utils.get(interaction.user.guild.roles, id=EVENT_ROLE)
            permanent_role = discord.utils.get(interaction.user.guild.roles, id=PERMANENT_ROLE)
            if team_role is None or event_role is None or permanent_role is None:
                return
            await interaction.user.add_roles(team_role, event_role, permanent_role)
            await interaction.response.send_message(f"You have joined the {self.label} team!", ephemeral=True)
        except IndexError:
            print("Unknown sign up button clicked")

class SignupWidget(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        for team in TEAMS:
            self.add_item(SignupWidgetButton(team["name"]))

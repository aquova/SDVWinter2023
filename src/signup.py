import discord
from config import EVENT_ROLE, GAMES_ROLE, PERMANENT_ROLE, TEAMS
import db

BUTTONS_PER_ROW = 2

class SignupWidgetButton(discord.ui.Button):
    def __init__(self, text: str, row: int, disabled: bool):
        custom_id = f"team_id:{text}"
        super().__init__(style=discord.ButtonStyle.primary, label=text, custom_id=custom_id, row=row, disabled=disabled)

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
            if not team_info["accepting"]:
                await interaction.response.send_message(f"Sorry, {self.label} isn't accepting new members at the moment", ephemeral=True)
                return
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

class EventGamesButton(discord.ui.Button):
    def __init__(self, text: str, row: int):
        custom_id = "games"
        super().__init__(style=discord.ButtonStyle.green, label=text, custom_id=custom_id, row=row)

    async def callback(self, interaction: discord.Interaction):
        if isinstance(interaction.user, discord.User):
            return

        games_role = discord.utils.get(interaction.user.guild.roles, id=GAMES_ROLE)
        if games_role is None:
            return

        if interaction.user.get_role(GAMES_ROLE) is None:
            await interaction.user.add_roles(games_role)
            await interaction.response.send_message("You have signed up to be pinged for mini-events!", ephemeral=True)
        else:
            await interaction.user.remove_roles(games_role)
            await interaction.response.send_message("You will no longer be pinged for mini-events", ephemeral=True)


class SignupWidget(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        idx = 0
        for team in TEAMS:
            row = int(idx / BUTTONS_PER_ROW)
            self.add_item(SignupWidgetButton(team["name"], row, not team["accepting"]))
            idx += 1
        self.add_item(EventGamesButton("Ping Me for Games!", int(idx / BUTTONS_PER_ROW)))

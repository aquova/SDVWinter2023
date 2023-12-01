import json

STARTING_SNOWBALLS = 15
SNOWBALL_EMOJI = "white_circle"
SNOWMAN_EMOJI = "snowman"

DATABASE_PATH = "private/database.db"
CONFIG_PATH = "private/config.json"
with open(CONFIG_PATH) as config_file:
    cfg = json.load(config_file)

DISCORD_KEY = cfg["discord"]
TEAMS = cfg["teams"]
EVENT_ROLE = cfg["roles"]["event"]
PERMANENT_ROLE = cfg["roles"]["permanent"]
GAMES_ROLE = cfg["roles"]["games"]
SNOWBALL_LOG = cfg["channels"]["log"]
SUBMISSIONS = cfg["channels"]["submissions"]

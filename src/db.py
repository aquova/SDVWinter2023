import sqlite3
from config import DATABASE_PATH, STARTING_SNOWBALLS, SUBMISSION_MAX, TEAMS

def initialize():
    sqlconn = sqlite3.connect(DATABASE_PATH)
    sqlconn.execute("CREATE TABLE IF NOT EXISTS teams (team_id INT PRIMARY KEY, team_name TEXT, points INT, UNIQUE(team_id));")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS members (user_id INT PRIMARY KEY, team INT, snowballs INT, FOREIGN KEY(team) REFERENCES teams(team_id));")
    sqlconn.execute("CREATE TABLE IF NOT EXISTS submissions (user_id INT, channel_id INT, FOREIGN KEY (user_id) REFERENCES members(user_id));")

    for team in TEAMS:
        sqlconn.execute("INSERT OR IGNORE INTO teams (team_id, team_name, points) VALUES (?, ?, ?)", [team["id"], team["name"], 0])

    sqlconn.commit()
    sqlconn.close()

def _db_read(query):
    sqlconn = sqlite3.connect(DATABASE_PATH)
    results = sqlconn.execute(*query).fetchall()
    sqlconn.close()
    return results

def _db_write(query):
    sqlconn = sqlite3.connect(DATABASE_PATH)
    sqlconn.execute(*query)
    sqlconn.commit()
    sqlconn.close()

def get_leaderboard() -> list:
    query = ("SELECT * FROM teams ORDER BY points DESC",)
    lb = _db_read(query)
    return lb

def add_member(userid: int, teamid: int):
    query = ("INSERT INTO members (user_id, team, snowballs) VALUES (?, ?, ?)", [userid, teamid, STARTING_SNOWBALLS])
    _db_write(query)

def get_team(userid: int) -> int | None:
    query = ("SELECT team FROM members WHERE user_id=?", [userid])
    results = _db_read(query)
    try:
        return results[0][0]
    except IndexError:
        return None

def get_team_name(userid: int) -> int | None:
    query = ("SELECT team_name FROM teams INNER JOIN members ON teams.team_id = members.team WHERE user_id=?", [userid])
    results = _db_read(query)
    try:
        return results[0][0]
    except IndexError:
        return None

def add_points_user(userid: int, pts: int):
    teamid = get_team(userid)
    if teamid is not None:
        add_points(teamid, pts)

def add_points(teamid: int, pts: int):
    old_pts_query = ("SELECT * FROM teams WHERE team_id=?", [teamid])
    old_pts = _db_read(old_pts_query)[0]
    new_pts = old_pts[2] + pts
    update_query = ("REPLACE INTO teams (team_id, team_name, points) VALUES (?, ?, ?)", [teamid, old_pts[1], new_pts])
    _db_write(update_query)

# Returns whether submission was accepted or not
def add_submission(userid: int, channelid: int) -> bool:
    if get_submission_count(userid, channelid) >= SUBMISSION_MAX:
        return False

    query = ("INSERT INTO submissions (user_id, channel_id) VALUES (?, ?)", [userid, channelid])
    _db_write(query)
    return True

def get_submission_count(userid: int, channelid: int) -> int:
    query = ("SELECT COUNT(*) FROM submissions WHERE user_id=? AND channel_id=?", [userid, channelid])
    cnt = _db_read(query)[0]
    return cnt[0]

def get_points(teamid: int) -> int:
    query = ("SELECT points FROM teams WHERE team_id=?", [teamid])
    pts = _db_read(query)
    try:
        return pts[0][0]
    except IndexError:
        return 0

def get_snowballs(userid: int) -> int:
    query = ("SELECT snowballs FROM members WHERE user_id=?", [userid])
    results = _db_read(query)
    try:
        return results[0][0]
    except IndexError:
        return 0

def use_snowball(userid: int):
    cnt = get_snowballs(userid)
    if cnt > 0:
        query = ("UPDATE members SET snowballs=? WHERE user_id=?", [cnt - 1, userid])
        _db_write(query)

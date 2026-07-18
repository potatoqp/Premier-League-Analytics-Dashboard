import requests
import pandas as pd
from sqlalchemy import create_engine
import time

from config import load_api_key


# CONFIG

API_KEY = load_api_key()
if not API_KEY:
    raise RuntimeError("Missing FOOTBALL_DATA_API_KEY in .env")
SEASON = 2025

# batch control
START = 0
END = 10

headers = {
    "X-Auth-Token": API_KEY
}

engine = create_engine(
    "mysql+pymysql://root:root@localhost/football_analytics"
)


# LOAD TEAMS
teams = pd.read_sql("""
    SELECT team_id
    FROM dim_team
    ORDER BY team_id
""", engine)

teams_subset = teams.iloc[START:END]

""""
#the players from those teams couldn't be added due to rate limiting, so i hardcoded them
teams_subset = teams[
    teams["team_id"].isin([402, 1044, 563, 340, 338])
]
"""



# FETCH SQUADS

players = []
bridge_rows = []

for team_id in teams_subset["team_id"]:

    url = f"https://api.football-data.org/v4/teams/{team_id}"

    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        continue

    squad = r.json()["squad"]

    for p in squad:

        players.append({
            "player_id": p["id"],
            "player_name": p["name"],
            "nationality": p["nationality"],
            "position": p["position"]
        })

        bridge_rows.append({
            "season": SEASON,
            "team_id": team_id,
            "player_id": p["id"]
        })

    time.sleep(1)




df_players = pd.DataFrame(players).drop_duplicates()

df_bridge = pd.DataFrame(bridge_rows)


# INSERT PLAYERS

for _, row in df_players.iterrows():

    try:
        pd.DataFrame([row]).to_sql(
            "dim_player",
            engine,
            if_exists="append",
            index=False
        )

    except:
        pass


# INSERT BRIDGE

for _, row in df_bridge.iterrows():

    try:
        pd.DataFrame([row]).to_sql(
            "bridge_team_player",
            engine,
            if_exists="append",
            index=False
        )

    except:
        pass


print("Squads loaded")
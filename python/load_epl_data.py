import requests
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text


#CONFIG

API_KEY = "1715573ab8024985854d38aec520ea96"

SEASON = 2025

headers = {
    "X-Auth-Token": API_KEY
}

url = f"https://api.football-data.org/v4/competitions/PL/matches?season={SEASON}"


#FETCH

response = requests.get(url, headers=headers)

print("Status:", response.status_code)

if response.status_code != 200:
    print(response.text)
    exit()

data = response.json()
matches = data["matches"]


#Transform teams

teams = {}

for m in matches:
    home = m["homeTeam"]
    away = m["awayTeam"]

    teams[home["id"]] = {
        "team_id": home["id"],
        "team_name": home["name"],
        "short_name": home["shortName"]
    }

    teams[away["id"]] = {
        "team_id": away["id"],
        "team_name": away["name"],
        "short_name": away["shortName"]
    }

df_teams = pd.DataFrame(teams.values())



#Transform matches

rows = []

for m in matches:
    rows.append({
        "match_id": m["id"],
        "match_date": m["utcDate"][:10],
        "season": SEASON,

        "home_team_id": m["homeTeam"]["id"],
        "away_team_id": m["awayTeam"]["id"],

        "home_goals": m["score"]["fullTime"]["home"],
        "away_goals": m["score"]["fullTime"]["away"],

        "winner": m["score"]["winner"]
    })

df_matches = pd.DataFrame(rows)


print(df_teams.shape)
print(df_matches.shape)


#Load to MySQL
engine = create_engine(
    "mysql+pymysql://root:root@localhost/football_analytics"
)

#append teams
for _, row in df_teams.iterrows():
    try:
        pd.DataFrame([row]).to_sql(
            "dim_team",
            engine,
            if_exists="append",
            index=False
        )
    except:
        pass

print("Teams synced")



with engine.begin() as conn:
    for _, row in df_matches.iterrows():
        sql = text("""
            INSERT INTO fact_match (
                season,
                match_id,
                match_date,
                home_team_id,
                away_team_id,
                home_goals,
                away_goals,
                winner
            )
            VALUES (
                :season,
                :match_id,
                :match_date,
                :home_team_id,
                :away_team_id,
                :home_goals,
                :away_goals,
                :winner
            )
            ON DUPLICATE KEY UPDATE
                match_date = VALUES(match_date),
                home_goals = VALUES(home_goals),
                away_goals = VALUES(away_goals),
                winner = VALUES(winner)
        """)

        conn.execute(sql, row.to_dict())

print(f"Season {SEASON} synced")

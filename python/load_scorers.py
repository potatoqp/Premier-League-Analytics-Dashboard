import requests
from sqlalchemy import create_engine, text

from config import load_api_key


# CONFIG
API_KEY = load_api_key()
if not API_KEY:
    raise RuntimeError("Missing FOOTBALL_DATA_API_KEY in .env")
SEASON = 2025

headers = {
    "X-Auth-Token": API_KEY
}

engine = create_engine(
    "mysql+pymysql://root:root@localhost/football_analytics"
)



# FETCH SCORERS
url = "https://api.football-data.org/v4/competitions/PL/scorers"

r = requests.get(url, headers=headers)

print("Status:", r.status_code)

# if API failed
if r.status_code != 200:
    print(r.json())
    exit()

data = r.json()

# safety check
if "scorers" not in data:
    print("No scorers returned")
    print(data)
    exit()

scorers = data["scorers"]

print(f"Found {len(scorers)} scorers")


sql = text("""
    INSERT INTO fact_player_season
    (
        season,
        player_id,
        goals
    )
    VALUES
    (
        :season,
        :player_id,
        :goals
    )
    ON DUPLICATE KEY UPDATE
        goals = VALUES(goals)
""")


inserted = 0
failed = 0

for s in scorers:

    try:
        with engine.begin() as conn:
            conn.execute(sql, {
                "season": SEASON,
                "player_id": s["player"]["id"],
                "goals": s["goals"]
            })

        inserted += 1
        print(
            f"Inserted: {s['player']['name']} "
            f"({s['goals']} goals)"
        )

    except Exception as e:
        failed += 1
        print(
            f"FAILED: {s['player']['name']}"
        )
        print(e)


print()
print("Done")
print("Inserted:", inserted)
print("Failed:", failed)
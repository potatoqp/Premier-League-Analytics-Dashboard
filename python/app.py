import streamlit as st
import pandas as pd
from sqlalchemy import create_engine



engine = create_engine(
    "mysql+pymysql://root:root@localhost/football_analytics"
)



st.set_page_config(page_title="Premier League Team Tracker")

st.title("⚽ Premier League Team Tracker")



#Season selector

seasons = pd.read_sql("""
    SELECT DISTINCT season
    FROM fact_match
    ORDER BY season DESC
""", engine)

selected_season = st.selectbox(
    "Choose a season",
    seasons["season"]
)



#Team selector

teams = pd.read_sql("""
    SELECT team_id, team_name
    FROM dim_team
    ORDER BY team_name
""", engine)

team_name = st.selectbox(
    "Choose a team",
    teams["team_name"]
)

team_id = teams.loc[
    teams["team_name"] == team_name,
    "team_id"
].iloc[0]

# -----------------------------
# Last 5 matches
# -----------------------------
last5_query = f"""
SELECT
    f.match_date,
    ht.team_name AS home_team,
    at.team_name AS away_team,
    f.home_goals,
    f.away_goals
FROM fact_match f
JOIN dim_team ht
    ON f.home_team_id = ht.team_id
JOIN dim_team at
    ON f.away_team_id = at.team_id
WHERE (
        f.home_team_id = {team_id}
        OR f.away_team_id = {team_id}
      )
AND f.season = {selected_season}
ORDER BY f.match_date DESC
LIMIT 5
"""

last5 = pd.read_sql(last5_query, engine)


#Form (Last 5)

form_results = []

for _, row in last5.iterrows():

    # skip unplayed matches
    if pd.isna(row["home_goals"]) or pd.isna(row["away_goals"]):
        continue

    # determine if selected team was home or away
    if row["home_team"] == team_name:
        gf = row["home_goals"]
        ga = row["away_goals"]
    else:
        gf = row["away_goals"]
        ga = row["home_goals"]

    if gf > ga:
        form_results.append(
            '<span style="color:green; font-size:30px;">W</span>'
        )
    elif gf == ga:
        form_results.append(
            '<span style="color:gray; font-size:30px;">D</span>'
        )
    else:
        form_results.append(
            '<span style="color:red; font-size:30px;">L</span>'
        )


st.subheader("Form (Last 5)")
st.markdown(
    " ".join(form_results),
    unsafe_allow_html=True
)


#All matches

all_matches_query = f"""
SELECT
    f.match_date,
    f.home_team_id,
    f.away_team_id,
    ht.team_name AS home_team,
    at.team_name AS away_team,
    f.home_goals,
    f.away_goals
FROM fact_match f
JOIN dim_team ht
    ON f.home_team_id = ht.team_id
JOIN dim_team at
    ON f.away_team_id = at.team_id
WHERE (
        f.home_team_id = {team_id}
        OR f.away_team_id = {team_id}
      )
AND f.season = {selected_season}
ORDER BY f.match_date DESC
"""

all_matches = pd.read_sql(all_matches_query, engine)

# check if team existed in selected season
if all_matches.empty:
    st.warning(f"{team_name} was not in the Premier League in {selected_season}.")
    st.stop()

#League table position

league_query = f"""
SELECT
    home_team_id,
    away_team_id,
    home_goals,
    away_goals
FROM fact_match
WHERE season = {selected_season}
"""

league_matches = pd.read_sql(league_query, engine)

table = {}

# initialize every team
for _, row in teams.iterrows():
    table[row["team_id"]] = {
        "team_name": row["team_name"],
        "points": 0,
        "gf": 0,
        "ga": 0
    }

for _, row in league_matches.iterrows():

    # skip future/unplayed matches
    if pd.isna(row["home_goals"]) or pd.isna(row["away_goals"]):
        continue

    h = row["home_team_id"]
    a = row["away_team_id"]
    hg = row["home_goals"]
    ag = row["away_goals"]

    # goals
    table[h]["gf"] += hg
    table[h]["ga"] += ag

    table[a]["gf"] += ag
    table[a]["ga"] += hg

    # points
    if hg > ag:
        table[h]["points"] += 3
    elif ag > hg:
        table[a]["points"] += 3
    else:
        table[h]["points"] += 1
        table[a]["points"] += 1


league_df = pd.DataFrame(table.values())

league_df["gd"] = league_df["gf"] - league_df["ga"]

league_df = league_df.sort_values(
    ["points", "gd", "gf"],
    ascending=False
).reset_index(drop=True)

league_df["position"] = league_df.index + 1

team_position = league_df.loc[
    league_df["team_name"] == team_name,
    "position"
].iloc[0]

st.subheader("League Position")
def ordinal(n):
    if 10 <= n % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1:"st", 2:"nd", 3:"rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

st.metric("Position", ordinal(team_position))

#Wins, Draws, Loses record
wins = 0
draws = 0
losses = 0

for _, row in all_matches.iterrows():
    if pd.isna(row["home_goals"]) or pd.isna(row["away_goals"]):
        continue

    if row["home_team_id"] == team_id:
        gf, ga = row["home_goals"], row["away_goals"]
    else:
        gf, ga = row["away_goals"], row["home_goals"]

    if gf > ga:
        wins += 1
    elif gf == ga:
        draws += 1
    else:
        losses += 1

col1, col2, col3 = st.columns(3)
col1.metric("Wins", wins)
col2.metric("Draws", draws)
col3.metric("Losses", losses)

#Point total

points = wins * 3 + draws
st.metric("Points", points)

display_matches = all_matches[
    [
        "match_date",
        "home_team",
        "away_team",
        "home_goals",
        "away_goals"
    ]
].rename(columns={
    "match_date": "Match Date",
    "home_team": "Home Team",
    "away_team": "Away Team",
    "home_goals": "Home Goals",
    "away_goals": "Away Goals"
})

st.subheader("All Matches")
st.dataframe(display_matches)


#Home vs Away Form
home_matches = all_matches[
    all_matches["home_team_id"] == team_id
]

away_matches = all_matches[
    all_matches["away_team_id"] == team_id
]

home_avg_goals = home_matches["home_goals"].mean()
away_avg_goals = away_matches["away_goals"].mean()

form_df = pd.DataFrame({
    "Venue": ["Home", "Away"],
    "Average Goals": [
        home_avg_goals,
        away_avg_goals
    ]
})

st.subheader("Home vs Away Form")
st.bar_chart(
    form_df.set_index("Venue")
)

#Goals For / Against / Difference

gf = 0
ga = 0

for _, row in all_matches.iterrows():

    # skip unplayed matches
    if pd.isna(row["home_goals"]) or pd.isna(row["away_goals"]):
        continue

    # if selected team is home
    if row["home_team_id"] == team_id:
        gf += row["home_goals"]
        ga += row["away_goals"]

    # if selected team is away
    else:
        gf += row["away_goals"]
        ga += row["home_goals"]

gd = gf - ga


st.subheader("Goals Summary")

col1, col2, col3 = st.columns(3)

col1.metric("Goals For", gf)
col2.metric("Goals Against", ga)
col3.metric(
    "Goal Difference",
    f"+{gd}" if gd > 0 else gd
)


#Active unbeaten streak
def unbeaten(row):
    if pd.isna(row["home_goals"]) or pd.isna(row["away_goals"]):
        return None

    if row["home_team_id"] == team_id:
        return row["home_goals"] >= row["away_goals"]
    else:
        return row["away_goals"] >= row["home_goals"]


streak = 0

for _, row in all_matches.iterrows():
    result = unbeaten(row)

    if result is None:
        continue

    if result:
        streak += 1
    else:
        break


st.subheader("Active Unbeaten Streak")
st.metric("Matches", streak)


#Longest unbeaten streak

longest_streak = 0
current_streak = 0

# oldest to newest for proper streak calculation
chronological_matches = all_matches.sort_values("match_date")

for _, row in chronological_matches.iterrows():
    result = unbeaten(row)

    # ignore unplayed matches
    if result is None:
        continue

    if result:
        current_streak += 1
        longest_streak = max(longest_streak, current_streak)
    else:
        current_streak = 0


st.subheader("Longest Unbeaten Streak")
st.metric("Matches", longest_streak)


#Longest winning streak

longest_win_streak = 0
current_win_streak = 0

chronological_matches = all_matches.sort_values("match_date")

for _, row in chronological_matches.iterrows():

    if pd.isna(row["home_goals"]) or pd.isna(row["away_goals"]):
        continue

    # determine result
    if row["home_team_id"] == team_id:
        won = row["home_goals"] > row["away_goals"]
    else:
        won = row["away_goals"] > row["home_goals"]

    if won:
        current_win_streak += 1
        longest_win_streak = max(
            longest_win_streak,
            current_win_streak
        )
    else:
        current_win_streak = 0


st.subheader("Longest Winning Streak")
st.metric("Matches", longest_win_streak)


#Biggest win / biggest loss

biggest_win_margin = -999
biggest_loss_margin = 999

biggest_win_text = ""
biggest_loss_text = ""

for _, row in all_matches.iterrows():

    if pd.isna(row["home_goals"]) or pd.isna(row["away_goals"]):
        continue

    if row["home_team_id"] == team_id:
        gf = row["home_goals"]
        ga = row["away_goals"]
        opponent = row["away_team"]
    else:
        gf = row["away_goals"]
        ga = row["home_goals"]
        opponent = row["home_team"]

    margin = gf - ga

    # biggest win
    if margin > biggest_win_margin:
        biggest_win_margin = margin
        biggest_win_text = f"{gf}-{ga} vs {opponent}"

    # biggest loss
    if margin < biggest_loss_margin:
        biggest_loss_margin = margin
        biggest_loss_text = f"{gf}-{ga} vs {opponent}"


st.subheader("Biggest Results")

st.metric(
    "Biggest Win",
    biggest_win_text
)

st.metric(
    "Biggest Loss",
    biggest_loss_text
)
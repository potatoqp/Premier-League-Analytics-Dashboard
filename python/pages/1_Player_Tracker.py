import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy import text


engine = create_engine(
    "mysql+pymysql://root:root@localhost/football_analytics"
)


# PAGE CONFIG

st.set_page_config(
    page_title="Player Tracker"
)

st.title("👤 Premier League Player Tracker")


# SEASON SELECTOR

seasons = pd.read_sql("""
    SELECT DISTINCT season
    FROM bridge_team_player
    ORDER BY season DESC
""", engine)

selected_season = st.selectbox(
    "Choose a season",
    seasons["season"]
)


# TEAM SELECTOR

teams = pd.read_sql(
    text("""
        SELECT DISTINCT
            t.team_id,
            t.team_name
        FROM bridge_team_player b
        JOIN dim_team t
            ON b.team_id = t.team_id
        WHERE b.season = :selected_season
        ORDER BY t.team_name
    """),
    engine,
    params={"selected_season": selected_season}
)

team_name = st.selectbox(
    "Choose a team",
    teams["team_name"]
)

team_id = teams.loc[
    teams["team_name"] == team_name,
    "team_id"
].iloc[0]


# TEAM SECTION

st.header("Team Overview")


# TOP SCORER
top_scorer = pd.read_sql("""
    SELECT
        p.player_name,
        fps.goals
    FROM fact_player_season fps
    JOIN dim_player p
        ON fps.player_id = p.player_id
    JOIN bridge_team_player b
        ON p.player_id = b.player_id
    WHERE b.team_id = %(team_id)s
    AND b.season = %(season)s
    ORDER BY fps.goals DESC
    LIMIT 1
""", engine, params={"team_id": team_id, "season": selected_season})


# SQUAD SIZE
squad_size = pd.read_sql("""
    SELECT COUNT(*) AS squad_size
    FROM bridge_team_player
    WHERE team_id = %(team_id)s
    AND season = %(season)s
""", engine, params={"team_id": team_id, "season": selected_season})



# METRICS
col1, col2 = st.columns(2)

if not top_scorer.empty:

    scorer_name = top_scorer.iloc[0]["player_name"]
    scorer_goals = top_scorer.iloc[0]["goals"]

    col1.metric(
        #free api only gets scorers in the top 10
        "Top Scorer (in the top 10 league scorers)",
        f"{scorer_name} ({scorer_goals})"
    )

else:

    col1.metric(
        "No player from this team is in the top 10 league scorers",
        "N/A"
    )

col2.metric(
    "Squad Size",
    squad_size.iloc[0]["squad_size"]
)


# POSITION BREAKDOWN

positions = pd.read_sql("""
    SELECT
        p.position,
        COUNT(*) AS players
    FROM bridge_team_player b
    JOIN dim_player p
        ON b.player_id = p.player_id
    WHERE b.team_id = %(team_id)s
    AND b.season = %(season)s
    GROUP BY p.position
    ORDER BY players DESC
""", engine, params={"team_id": team_id, "season": selected_season})

# PLAYER SECTION
st.header("Player Stats")


# PLAYER DROPDOWN

players = pd.read_sql("""
    SELECT
        p.player_id,
        p.player_name
    FROM bridge_team_player b
    JOIN dim_player p
        ON b.player_id = p.player_id
    WHERE b.team_id = %(team_id)s
    AND b.season = %(season)s
    ORDER BY p.player_name
""", engine, params={"team_id": team_id, "season": selected_season})


player_name = st.selectbox(
    "Choose a player",
    players["player_name"]
)

player_id = players.loc[
    players["player_name"] == player_name,
    "player_id"
].iloc[0]


# PLAYER INFO

player = pd.read_sql("""
    SELECT
        p.player_name,
        p.nationality,
        p.position,
        COALESCE(f.goals, 'N/A') AS goals
    FROM dim_player p
    LEFT JOIN fact_player_season f
        ON p.player_id = f.player_id
        AND f.season = %(season)s
    WHERE p.player_id = %(player_id)s
""", engine, params={"season": selected_season, "player_id": player_id})


row = player.iloc[0]


# PLAYER METRICS

col1, col2 = st.columns(2)

col1.metric(
    "Nationality",
    row["nationality"]
)

col2.metric(
    "Position",
    row["position"]
)

st.metric(
    "Goals",
    row["goals"]
)
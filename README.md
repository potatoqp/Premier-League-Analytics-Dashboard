Premier League Analytics Dashboard

A football analytics project built using Python, MySQL, and Streamlit.

The project collects Premier League data from the football-data.org API, stores it in a MySQL database, and visualizes team/player statistics through an interactive dashboard. I have worked around some of the football-data.org API free limitations to make something that stands on its own. For example, we can only fetch the top 10 goalscorers of the league, and not every player that has scored a goal. Also, we can only fetch current season squads, not past seasons. Also, some teams had to be hardcoded in (to add their players), as to avoid api rate-limiting.


Features:

Team Tracker:

- Season selector
- Team selector
- Last 5 matches
- Full match history
- Home vs Away form
- Active unbeaten streak
- Longest unbeaten streak
- Longest winning streak
- Biggest win / biggest loss
- Goals For / Against / Goal Difference
- League position
- Form string (W/D/L)

Player Tracker:

- Squad size
- Position breakdown
- Top scorer (if included in the top 10 season scorers)
- Player nationality
- Player position
- Goals scored (not possible with the free api version)

MYSQL tables used:

dim_team
fact_match
dim_player
bridge_team_player
fact_player_season


Technologies used:

- Python
- Pandas
- SQLAlchemy
- MySQL
- Streamlit
- football-data.org API

Install dependancies:

pip install pandas requests sqlalchemy pymysql streamlit

How to run:

python python/load_epl_data.py
python python/load_players.py
python python/load_scorers.py

streamlit run python/app.py


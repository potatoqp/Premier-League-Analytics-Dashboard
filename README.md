# Premier League Analytics Dashboard

A football analytics dashboard built with Python, MySQL, and Streamlit.

This project collects Premier League data from the football-data.org API, stores it in a MySQL database, and visualizes team and player statistics through an interactive dashboard.

The project also works around several limitations of the free football-data.org API tier in order to provide a more complete analytics experience.

---

# Features

## Team Tracker

* Season selector
* Team selector
* Last 5 matches
* Full match history
* Home vs Away form
* Active unbeaten streak
* Longest unbeaten streak
* Longest winning streak
* Biggest win / Biggest loss
* Goals For / Against / Goal Difference
* League position
* Form string (W / D / L)

---

## Player Tracker

* Squad size
* Position breakdown
* Top scorer (if included in the API top scorers list)
* Player nationality
* Player position
* Goals scored *(limited by free API version)*

---

# API Limitations & Workarounds

The free football-data.org API plan includes several restrictions, such as:

* Only the top 10 league scorers are available
* Historical season squads are unavailable
* Strict API rate limiting

To improve the dashboard functionality:

* Some teams and player data were manually supplemented, in cases where API rate limiting was present
* Additional logic was implemented to reduce unnecessary API calls

These adjustments allow the application to function as a more complete standalone analytics platform.

---

# Database Schema

The project uses the following MySQL tables:

```text
dim_team
fact_match
dim_player
bridge_team_player
fact_player_season
```

---

# Technologies Used

* Python
* Pandas
* SQLAlchemy
* MySQL
* Streamlit
* football-data.org API

---

# Installation

Install the required dependencies:

```bash
pip install pandas requests sqlalchemy pymysql streamlit
```

---

# Running the Project

## Load Match Data

```bash
python python/load_epl_data.py
```

## Load Player Data

```bash
python python/load_players.py
```

## Load Scorer Data

```bash
python python/load_scorers.py
```

## Launch Dashboard

```bash
streamlit run python/app.py
```

---

# Future Improvements (with the use of a paid API tier)

* Historical season support
* More advanced player analytics
* Expected Goals (xG) metrics
* Match prediction models
* Additional league support
* Automated data refresh scheduling

---




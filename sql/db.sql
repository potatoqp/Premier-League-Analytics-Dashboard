CREATE DATABASE football_analytics;
USE football_analytics;


CREATE TABLE dim_team (
    team_id INT PRIMARY KEY,
    team_name VARCHAR(100),
    short_name VARCHAR(50)
);

CREATE TABLE fact_match (
    season INT,
    match_id INT,

    match_date DATE,

    home_team_id INT,
    away_team_id INT,

    home_goals INT,
    away_goals INT,

    winner VARCHAR(20),

    PRIMARY KEY (season, match_id),

    FOREIGN KEY (home_team_id)
        REFERENCES dim_team(team_id),

    FOREIGN KEY (away_team_id)
        REFERENCES dim_team(team_id)
);


CREATE TABLE dim_player (
    player_id INT PRIMARY KEY,
    player_name VARCHAR(100),
    nationality VARCHAR(100),
    position VARCHAR(50)
);

CREATE TABLE bridge_team_player (
    season INT,
    team_id INT,
    player_id INT,

    PRIMARY KEY (season, team_id, player_id),

    FOREIGN KEY (team_id)
        REFERENCES dim_team(team_id),

    FOREIGN KEY (player_id)
        REFERENCES dim_player(player_id)
);

CREATE TABLE fact_player_season (
    season INT,
    player_id INT,

    goals INT DEFAULT 0,

    PRIMARY KEY (season, player_id),

    FOREIGN KEY (player_id)
        REFERENCES dim_player(player_id)
);
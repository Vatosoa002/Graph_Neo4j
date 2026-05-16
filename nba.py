from neo4j import GraphDatabase
import pandas as pd

URI = "neo4j://localhost"
AUTH = ("neo4j", "password")

constraints = [
    "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Team)    REQUIRE t.TEAM_ID    IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Player)  REQUIRE p.PLAYER_ID  IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (g:Game)    REQUIRE g.GAME_ID    IS UNIQUE",
    "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Season)  REQUIRE s.year       IS UNIQUE",
]
for c in constraints:
    with GraphDatabase.driver(URI, auth=AUTH).session() as session:
        session.run(c)

team = pd.read_csv("teams.csv")
for i, row in team.iterrows():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.execute_query(
            "MERGE (a:TEAM {TEAM_ID: $ID})",
            ID=row["TEAM_ID"],
            database_="neo4j",
        )

player = pd.read_csv("players.csv")
for i, row in player.iterrows():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.execute_query(
            """
            MERGE (a:PLAYER {PLAYER_ID: $PLAYER_ID})
            SET a.NAME = $NAME
            WITH a
            MATCH (b:TEAM {TEAM_ID: $ID})
            MERGE (a)-[:PLAYS_FOR]->(b)
            """,
            ID=row["TEAM_ID"],
            PLAYER_ID=row["PLAYER_ID"],
            NAME=row["PLAYER_NAME"],
            database_="neo4j",
        )

games = pd.read_csv("games.csv")
for i, row in games.iterrows():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.execute_query(
            """
            MERGE (g:GAME {GAME_ID: $GAME_ID})
            SET g.DATE = $DATE, g.SEASON = $SEASON, g.STATUS = $STATUS,
                g.PTS_home = $PTS_home, g.PTS_away = $PTS_away,
                g.HOME_TEAM_WINS = $HOME_TEAM_WINS
            WITH g
            MATCH (home:TEAM {TEAM_ID: $HOME_TEAM_ID})
            MATCH (away:TEAM {TEAM_ID: $VISITOR_TEAM_ID})
            MERGE (home)-[:PLAYED_HOME]->(g)
            MERGE (away)-[:PLAYED_AWAY]->(g)
            """,
            GAME_ID=row["GAME_ID"],
            DATE=row["GAME_DATE_EST"],
            SEASON=row["SEASON"],
            STATUS=row["GAME_STATUS_TEXT"],
            PTS_home=row["PTS_home"],
            PTS_away=row["PTS_away"],
            HOME_TEAM_WINS=int(row["HOME_TEAM_WINS"]),
            HOME_TEAM_ID=row["HOME_TEAM_ID"],
            VISITOR_TEAM_ID=row["VISITOR_TEAM_ID"],
            database_="neo4j",
        )

details = pd.read_csv("games_details.csv")
for i, row in details.iterrows():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.execute_query(
            """
            MATCH (p:PLAYER {PLAYER_ID: $PLAYER_ID})
            MATCH (g:GAME   {GAME_ID:   $GAME_ID})
            MERGE (p)-[r:PLAYED_IN]->(g)
            SET r.PTS = $PTS, r.REB = $REB, r.AST = $AST,
                r.MIN = $MIN, r.START_POSITION = $START_POSITION
            """,
            PLAYER_ID=row["PLAYER_ID"],
            GAME_ID=row["GAME_ID"],
            PTS=row["PTS"],
            REB=row["REB"],
            AST=row["AST"],
            MIN=row["MIN"],
            START_POSITION=row["START_POSITION"],
            database_="neo4j",
        )

ranking = pd.read_csv("ranking.csv")
for i, row in ranking.iterrows():
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.execute_query(
            """
            MATCH (t:TEAM {TEAM_ID: $TEAM_ID})
            MERGE (s:SEASON {year: $SEASON_ID})
            MERGE (t)-[r:RANKED_IN]->(s)
            SET r.W = $W, r.L = $L, r.W_PCT = $W_PCT,
                r.CONFERENCE = $CONFERENCE,
                r.HOME_RECORD = $HOME_RECORD, r.ROAD_RECORD = $ROAD_RECORD
            """,
            TEAM_ID=row["TEAM_ID"],
            SEASON_ID=row["SEASON_ID"],
            W=row["W"],
            L=row["L"],
            W_PCT=row["W_PCT"],
            CONFERENCE=row["CONFERENCE"],
            HOME_RECORD=row["HOME_RECORD"],
            ROAD_RECORD=row["ROAD_RECORD"],
            database_="neo4j",
        )
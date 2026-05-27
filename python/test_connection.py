from sqlalchemy import create_engine

engine = create_engine(
    "mysql+pymysql://root:root@localhost/football_analytics"
)

conn = engine.connect()
print("Connected!")
conn.close()
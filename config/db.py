from sqlalchemy import create_engine, MetaData
from config.configkey import DATABASE_URL


engine = create_engine(DATABASE_URL)
meta = MetaData()
conn = engine.connect()
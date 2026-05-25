import databases
import sqlalchemy as sa
import os


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

database = databases.Database(DATABASE_URL)

metadata = sa.MetaData()

if os.getenv("RENDER"):
    engine = sa.create_engine(DATABASE_URL)
else:
    engine = sa.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

import databases
import sqlalchemy as sa
import os


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

database = databases.Database(DATABASE_URL)

metadata = sa.MetaData()

engine = sa.create_engine(
    DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
)

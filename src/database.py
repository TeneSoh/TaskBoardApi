from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:lyonnel@localhost:5432/taskboard"
SQLALCHEMY_DATABASE_URL = config("DATABASE_URL")

engin = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engin)

Base = declarative_base()

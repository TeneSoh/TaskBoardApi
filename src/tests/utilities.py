from typing import Annotated

from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.database import Base
from src.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine) 


def getTest_db():
    dbTest = TestingSessionLocal()
    try:
        yield dbTest
    finally:
        dbTest.close()


dbtest_dependency = Annotated[Session, Depends(getTest_db)]

client = TestClient(app)

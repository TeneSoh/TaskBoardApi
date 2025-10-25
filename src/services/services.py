from typing import Annotated

from fastapi import Depends, Path
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import SessionLocal, engin
from src.models import Base

Base.metadata.create_all(bind=engin)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

from datetime import datetime, timedelta, timezone
from typing import Annotated

from decouple import config
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from src.models import User
from src.services.services import *

route = APIRouter(prefix="/auth", tags=["auth"])


class UserRequest(BaseModel):
    username: str
    email: str
    password: str


# config the jwt
# secrete_key = secrets.token_urlsafe(64)
# ALGORITHM = "HS256"
# SECRET_KEY = secrete_key

# config to hash password
bcrypt_contex = CryptContext(["argon2", "bcrypt"], deprecated="auto")

# where to send request went we want to authenticate user
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/login")


# authenticate the user
def authenticateUser(db, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_contex.verify(password, str(user.hashed_password)):
        return False
    return user


# generate the access token
async def getAccessToken(username: str, id: int, expire_minutes: int):
    payload = {"sub": username, "id": id, "scope": "access_token"}
    expired_time = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload.update({"exp": expired_time})
    access_token = jwt.encode(
        claims=payload, key=config("SECRETE_KEY"), algorithm=config("ALGORITHME")  # type: ignore
    )
    return access_token


# generate the refresh token
async def getRefreshToken(username: str, id: int, expire_days: int = 7):
    payload = {"sub": username, "id": id, "scope": "refresh_token"}
    expired_days = datetime.now(timezone.utc) + timedelta(minutes=expire_days)
    payload.update({"exp": expired_days})
    access_token = jwt.encode(
        claims=payload, key=config("SECRETE_KEY"), algorithm=config("ALGORITHME")  # type: ignore
    )
    return access_token


# authenticate the current user
def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(
            token=token, key=config("SECRETE_KEY"), algorithms=config("ALGORITHME")  # type: ignore
        )
        if payload["scope"] == "access_token":
            username = payload["sub"]
            user_id = payload["id"]

            return {"username": username, "id": user_id}

        raise HTTPException(
            status_code=401, detail="Invalid scope for token newtwork !!"
        )
    except:
        raise HTTPException(status_code=401, detail="Invalid token")


# register the user
@route.post("/register-user", status_code=status.HTTP_201_CREATED)
def createUser(data: UserRequest, db: db_dependency):
    user = User(
        username=data.username,
        email=data.email,
        hashed_password=bcrypt_contex.hash(data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# login user
@route.post("/login-user", status_code=status.HTTP_202_ACCEPTED)
async def loginUser(
    db: db_dependency, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = authenticateUser(db, form_data.username, form_data.password)
    if user is not None:
        accessToken = await getAccessToken(form_data.username, user.id, 30)  # type: ignore
        refreshToken = await getRefreshToken(form_data.username, user.id)  # type: ignore
        return {
            "user": user,
            "access_token": accessToken,
            "refresh_token": refreshToken,
        }
    raise HTTPException(status_code=404, detail="invalide credentials")
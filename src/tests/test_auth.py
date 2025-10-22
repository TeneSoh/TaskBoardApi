import pytest
from decouple import config
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import text
from starlette import status

from src.models import User
from src.routes.auth import (
    authenticateUser,
    get_current_user,
    getAccessToken,
    getRefreshToken,
)
from src.services.services import get_db

from .utilities import *

# on recrit la dependence de l'application principale ce qui fait que lors du test c'est la sqlit3 qui est utiliser au lieu de postgresql
app.dependency_overrides[get_db] = getTest_db
bcrypt_context = CryptContext(["argon2", "bcrypt"], deprecated="auto")


@pytest.fixture
def test_user():
    with engine.connect() as con:
        con.execute(text("DELETE FROM users"))
        con.commit()

    user = User(
        username="lyonnel",
        email="lyonnel@example.com",
        hashed_password=bcrypt_context.hash("lyonnel123"),
    )

    db = TestingSessionLocal()
    db.add(user)
    db.commit()
    db.refresh(user)
    yield user
    with engine.connect() as con:
        con.execute(text("DELETE FROM users"))
        con.commit()


def test_authenticate_fuction(test_user):
    db = TestingSessionLocal()
    result = authenticateUser(db, test_user.username, "lyonnel123")

    assert result is not None
    assert result.username == test_user.username  # type:ignore
    assert result.email == test_user.email  # type:ignore
    assert bcrypt_context.verify("lyonnel123", result.hashed_password)  # type: ignore


@pytest.mark.asyncio
async def test_getAccessToken(test_user):
    token = await getAccessToken(test_user.username, test_user.id, 30)
    decode_username = ""
    decode_id = ""
    decode_scope = ""
    tokendecode = jwt.decode(token=token, key=config("SECRETE_KEY"), algorithms=config("ALGORITHME"))  # type: ignore

    decode_username = tokendecode["sub"]
    decode_id = tokendecode["id"]
    decode_scope = tokendecode["scope"]

    assert decode_username == test_user.username
    assert decode_id == test_user.id
    assert decode_scope == "access_token"


@pytest.mark.asyncio
async def test_getRefreshToken(test_user):
    token = await getRefreshToken(test_user.username, test_user.id, 7)
    decode_username = ""
    decode_id = ""
    decode_scope = ""
    tokendecode = jwt.decode(token=token, key=config("SECRETE_KEY"), algorithms=config("ALGORITHME"))  # type: ignore

    decode_username = tokendecode["sub"]
    decode_id = tokendecode["id"]
    decode_scope = tokendecode["scope"]

    assert decode_username == test_user.username
    assert decode_id == test_user.id
    assert decode_scope == "refresh_token"


@pytest.mark.asyncio
async def test_getCurentUser(test_user):
    username = test_user.username
    email = test_user.email
    id = test_user.id

    token = await getAccessToken(test_user.username, test_user.id, 30)

    user = get_current_user(token=token)
    assert test_user.username == user.get("username")
    assert test_user.id == user.get("id")


def test_create_user(test_user):
    data = {
        "username": "douglas",
        "email": "douglas@gmail.com",
        "password": "douglas123",
    }

    respose = client.post("/auth/register-user", json=data)

    assert respose.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    user = db.query(User).filter(User.username == data.get("username")).first()
    assert user is not None
    assert user.username == data["username"]  # type: ignore
    assert user.email == data["email"]  # type: ignore
    assert bcrypt_context.verify(data.get("password"), user.hashed_password)  # type: ignore


@pytest.mark.asyncio
async def test_login(test_user):
    data = {"username": test_user.username, "password": "lyonnel123"}

    response = client.post("/auth/login-user", data=data)
    assert response.status_code == status.HTTP_202_ACCEPTED
    response_data = response.json()
    assert response_data["user"]["username"] == test_user.username  # type:ignore
    assert response_data["user"]["email"] == test_user.email  # type:ignore
    assert bcrypt_context.verify("lyonnel123", response_data["user"]["hashed_password"])  # type: ignore

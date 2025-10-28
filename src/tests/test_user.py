import io
from pathlib import Path

import pytest
from fastapi import HTTPException, status

from src.models import User
from src.routes.auth.auth import get_db
from src.tests.test_auth import test_user
from src.tests.utilities import *

app.dependency_overrides[get_db] = getTest_db


@pytest.fixture
def test_auth_user(test_user):
    # Authentification
    testing_user = test_user
    data = {"username": testing_user.username, "password": "lyonnel123"}

    login_response = client.post("/auth/login-user", data=data)

    if login_response is None:
        raise HTTPException(
            status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            detail="Unauthorize information",
        )

    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    db = TestingSessionLocal()
    # saved_user = db.query(User).filter_by(id=testing_user.id).first()

    yield testing_user, headers


@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_user_profile_without_image(test_auth_user, tmp_path):

    testing_user, headers = test_auth_user

    file_content = b"test image file"
    file = io.BytesIO(file_content)
    file.name = "test_image.png"

    data = {"username": "updateduser", "email": "updated@example.com"}

    file = {"profile_image": (file.name, file, "image/png")}

    response = client.put("/user/edit/", data=data, files=file, headers=headers)

    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    resp_json = response.json()
    assert resp_json["user"]["username"] == data["username"]
    assert resp_json["user"]["email"] == data["email"]

    # Vérifie que l'image a été sauvegardée
    saved_path = Path(resp_json["user"]["profile_image"])
    assert saved_path.exists()
    assert saved_path.read_bytes() == file_content

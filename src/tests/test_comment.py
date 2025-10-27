import pytest
from fastapi import status
from sqlalchemy import text

from src.models import Comment
from src.services.services import get_db
from src.tests.test_auth import test_user
from src.tests.test_project import test_project
from src.tests.test_task import test_task
from src.tests.utilities import *
from src.tests.utilities import engine, getTest_db

app.dependency_overrides[get_db] = getTest_db


@pytest.fixture
def test_comment(test_task):
    with engine.connect() as con:
        con.execute(text("DELETE FROM comments"))
        con.commit()

    # Get information from test_task
    task, headers = test_task

    # creat fake comment for test

    comment = Comment(
        content="Test comment content", task_id=task.id, user_id=task.user_id
    )

    db = TestingSessionLocal()
    db.add(comment)
    db.commit()
    db.refresh(comment)

    yield comment, headers

    with engine.connect() as con:
        con.execute(text("DELETE FROM comments"))
        con.commit()


# Test get all task comments
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_all_task_comment(test_comment):
    comment, headers = test_comment

    response = client.get(f"/comment/{comment.task_id}", headers=headers)

    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0].get("content") == "Test comment content"


# Create_comment
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_comment(test_comment):
    comment, headers = test_comment

    data = {
        "content": "Comment storing test",
        "task_id": comment.task_id,
        "user_id": comment.user_id,
    }

    response = client.post("/comment/creat-comment/", json=data, headers=headers)

    result = response.json()

    assert response is not None
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    value = db.query(Comment).filter(Comment.id == result["id"]).first()
    assert value.content == data.get("content")  # type: ignore


# Edit comment
@pytest.mark.asyncio
@pytest.mark.integration
async def test_edit_comment(test_comment):
    comment, headers = test_comment

    data = {
        "content": "Comment editting test",
    }

    response = client.put(
        f"/comment/edit-comment/{comment.id}", json=data, headers=headers
    )

    result = response.json()

    print(f"Contenu de response : {result}")

    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    db = TestingSessionLocal()
    value = db.query(Comment).filter(Comment.id == result["id"]).first()
    assert value.content == data.get("content")  # type: ignore

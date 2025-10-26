from datetime import datetime, timezone

import pytest
from fastapi import status
from sqlalchemy import text

from src.models import Task
from src.services.services import get_db
from src.tests.test_auth import test_user
from src.tests.test_project import test_project
from src.tests.utilities import *

app.dependency_overrides[get_db] = getTest_db


@pytest.fixture
def test_task(test_project):
    with engine.connect() as con:
        con.execute(text("DELETE FROM tasks"))
        con.commit()

    project, headers = test_project

    test_task = Task(
        title="Test Task",
        description="This is a test task",
        user_id=project.user_id,
        project_id=project.id,
        deadline=datetime.now(timezone.utc),
        status="in_progress",
        priority="medium",
    )

    db = TestingSessionLocal()
    db.add(test_task)
    db.commit()
    db.refresh(test_task)
    yield test_task, headers

    with engine.connect() as con:
        con.execute(text("DELETE FROM tasks"))
        con.commit()


# test get tasks
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_tasks(test_task):
    task, headers = test_task
    response = client.get("/tasks/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0].get("title") == task.title
    assert response.json()[0].get("description") == task.description


# test create task
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_task(test_task):
    task, headers = test_task

    data = {
        "title": "test task",
        "description": "task description",
        "user_id": task.user_id,
        "project_id": task.project_id,
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "status": task.status,
        "priority": task.priority,
    }
    response = client.post("/tasks/create-task", json=data, headers=headers)
    assert response is not None
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    created_task = db.query(Task).filter(Task.id == response.json().get("id")).first()
    assert created_task is not None
    assert response.json().get("title") == created_task.title
    assert response.json().get("description") == created_task.description


# test update task
@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_task(test_task):
    task, headers = test_task
    updated_data = {
        "title": "Updated test Task",
        "description": "updated test task description",
        "user_id": task.user_id,
        "project_id": task.project_id,
        "deadline": task.deadline.isoformat() if task.deadline else None,
        "status": task.status,
        "priority": task.priority,
    }
    response = client.put(
        f"/tasks/update-task/{task.id}", json=updated_data, headers=headers
    )
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    db = TestingSessionLocal()
    updated_task = db.query(Task).filter(Task.id == task.id).first()
    assert updated_task is not None
    assert response.json().get("title") == updated_data.get("title")
    assert response.json().get("description") == updated_data.get("description")


# test delete task
@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_task(test_task):
    task, headers = test_task
    response = client.delete(f"/tasks/delete-task/{task.id}", headers=headers)
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    db = TestingSessionLocal()
    deleted_task = db.query(Task).filter(Task.id == task.id).first()
    assert deleted_task is None
    assert response.json().get("title") == task.title
    assert response.json().get("description") == task.description


# Test get user tasks
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_tasks(test_task):
    task, headers = test_task
    response = client.get(f"/tasks/user/{task.user_id}", headers=headers)
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0
    assert response.json()[0].get("id") == task.id
    assert response.json()[0].get("user_id") == task.user_id
    assert response.json()[0].get("project_id") == task.project_id

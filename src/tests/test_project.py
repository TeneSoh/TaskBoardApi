import pytest
from fastapi import HTTPException, status
from sqlalchemy import text

from src.models import Project
from src.services.services import get_db
from src.tests.test_auth import test_user
from src.tests.utilities import *

app.dependency_overrides[get_db] = getTest_db


@pytest.fixture
def test_project(test_user):
    with engine.connect() as con:
        con.execute(text("DELETE FROM projects"))
        con.commit()

    # Authentification
    data = {"username": test_user.username, "password": "lyonnel123"}

    login_response = client.post("/auth/login-user", data=data)

    if login_response is None:
        raise HTTPException(
            status_code=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
            detail="Unauthorize information",
        )

    token = login_response.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    project = Project(
        name="Developpement web",
        description="Projet de developpement web",
        user_id=test_user.id,
    )

    db = TestingSessionLocal()
    db.add(project)
    db.commit()
    db.refresh(project)

    yield project, headers

    with engine.connect() as con:
        con.execute(text("DELETE FROM projects"))
        con.commit()


# test get all projects
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_projects(test_project):
    # Test
    project, headers = test_project
    response = client.get("/project/", headers=headers)

    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            "id": project.id,
            "name": "Developpement web",
            "description": "Projet de developpement web",
            "user_id": project.user_id,
        }
    ]


# Test get unique project
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_unique_project(test_user, test_project):
    # Test
    project, headers = test_project
    response = client.get(f"/project/{project.id}", headers=headers)

    project_data = response.json()
    print(project_data)
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    assert project.name == project_data.get("name")
    assert project.description == project_data.get("description")


# Test create project
@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_project(test_project):
    # Test
    project, headers = test_project

    new_project = {
        "name": "New project",
        "description": "New project description",
        "user_id": project.user_id,
    }

    response = client.post("/project/create/", json=new_project, headers=headers)

    assert response is not None
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    data = response.json()
    get_new_project = db.query(Project).filter_by(id=data.get("id")).first()
    assert new_project.get("name") == get_new_project.name  # type:ignore
    assert new_project.get("description") == get_new_project.description  # type:ignore


# Test edit project
@pytest.mark.integration
@pytest.mark.asyncio
async def test_edit_project(test_project):
    # Test
    project, headers = test_project
    new_data = {
        "name": "edit project",
        "description": "edit project description",
    }
    response = client.put(
        f"/project/edit-project/{project.id}", json=new_data, headers=headers
    )
    edit_data = response.json()
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    db = TestingSessionLocal()
    unique_project = db.query(Project).filter_by(id=edit_data.get("id")).first()
    assert unique_project.name == new_data.get("name")  # type:ignore
    assert unique_project.description == new_data.get("description")  # type:ignore


# Test delete project
@pytest.mark.asyncio
@pytest.mark.integration
async def test_delete_project(test_project):
    # Test
    project, headers = test_project
    response = client.delete(f"/project/delete-project/{project.id}", headers=headers)

    deleted_data = response.json()
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    assert project.name == deleted_data.get("name")
    assert project.description == deleted_data.get("description")


# Test Get all projects for any user
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_any_user_projects(test_project):
    project, headers = test_project
    response = client.get(f"/project/user/{project.user_id}", headers=headers)
    deleted_data = response.json()
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    assert project.name == deleted_data[0].get("name")
    assert project.description == deleted_data[0].get("description")


# Test Get all projects for connected user
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_user_projects(test_project):
    project, headers = test_project

    response = client.get("/project/user/", headers=headers)
    all_data = response.json()
    print(response)
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    assert project.name == all_data[0].get("name")
    assert project.description == all_data[0].get("description")


# Test Get all projects tasks
@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_project_tasks(test_project):
    project, headers = test_project
    response = client.get(f"/project/{project.id}/tasks", headers=headers)
    deleted_data = response.json()
    assert response is not None
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(deleted_data, list)

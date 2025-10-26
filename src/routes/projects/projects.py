import traceback
from fastapi import APIRouter, HTTPException, status

from src.models import Project, Task
from src.routes.auth.auth import get_current_user
from src.services.services import *

user_dependency = Annotated[dict, Depends(get_current_user)]
route = APIRouter(prefix="/project", tags=["projects"])


# Project validating request
class ProjectRequest(BaseModel):
    name: str = "Web app"
    description: str = "Application web pour site de vente"


# Get all project
@route.get("/", status_code=status.HTTP_200_OK)
async def get_projects(db: db_dependency, user: user_dependency):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        projects = db.query(Project).filter(Project.user_id == user.get("id")).all()

        return projects
    except Exception as e:
        print("ERREUR get_projects :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Get unique project
@route.get("/{project_id}", status_code=status.HTTP_200_OK)
async def get_unique_project(
    db: db_dependency, user: user_dependency, project_id: int = Path(gt=0)
):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        project = (
            db.query(Project).filter_by(user_id=user.get("id"), id=project_id).first()
        )

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        return project
    except Exception as e:
        print("ERREUR get_unique_project :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Create project
@route.post("/create/", status_code=status.HTTP_201_CREATED)
async def create_project(
    db: db_dependency, user: user_dependency, data: ProjectRequest
):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        new_project = Project(
            name=data.name, description=data.description, user_id=user.get("id")
        )

        db.add(new_project)
        db.commit()
        db.refresh(new_project)

        return new_project
    except Exception as e:
        print("ERREUR create_project :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# edit project
@route.put("/edit-project/{project_id}", status_code=status.HTTP_200_OK)
async def edit_project(
    db: db_dependency,
    user: user_dependency,
    data: ProjectRequest,
    project_id: int = Path(gt=0),
):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        project = (
            db.query(Project).filter_by(user_id=user.get("id"), id=project_id).first()
        )

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        setattr(project, "name", data.name)
        setattr(project, "description", data.description)

        db.commit()
        db.refresh(project)

        return project
    except Exception as e:
        print("ERREUR edit_project :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Delete project
@route.delete("/delete-project/{project_id}", status_code=status.HTTP_200_OK)
async def delete_project(
    db: db_dependency, user: user_dependency, project_id: int = Path(gt=0)
):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        project = (
            db.query(Project).filter_by(id=project_id, user_id=user.get("id")).first()
        )

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        db.delete(project)
        db.commit()

        return project

    except Exception as e:
        print("ERREUR delete_project :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


# Get all projects for connected user
@route.get("/user/", status_code=status.HTTP_200_OK)
async def get_user_projects(db: db_dependency, user: user_dependency):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        projects = db.query(Project).filter(Project.user_id == user.get("id")).all()

        return projects

    except Exception as e:
        print("ERREUR get_all_user_project :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Get all projects for any user
@route.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_any_user_projects(
    db: db_dependency, user: user_dependency, user_id: int = Path(gt=0)
):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        projects = db.query(Project).filter(Project.user_id == user_id).all()
        return projects
    except Exception as e:
        print("ERREUR get_any_user_projects :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Get all projects tasks
@route.get("/{project_id}/tasks", status_code=status.HTTP_200_OK)
async def get_user_projects_tasks(
    db: db_dependency, user: user_dependency, project_id: int = Path(gt=0)
):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        tasks = db.query(Task).filter(Task.project_id == project_id).all()
        return tasks
    except Exception as e:
        print("ERREUR get_all_project_task :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

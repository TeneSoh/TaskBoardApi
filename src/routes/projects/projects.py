from fastapi import APIRouter, HTTPException, status

from src.models import Project
from src.routes.auth.auth import get_current_user
from src.services.services import *

user_dependency = Annotated[dict, Depends(get_current_user)]
rout = APIRouter(prefix="/project", tags=["projects"])


# Project validating request
class ProjectRequest(BaseModel):
    name: str = "Web app"
    description: str = "Application web pour site de vente"


# Get all project
@rout.get("/", status_code=status.HTTP_200_OK)
async def get_projects(db: db_dependency, user: user_dependency):

    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    projects = db.query(Project).filter(Project.user_id == user.get("id")).all()

    return projects


# Get unique project
@rout.get("/{project_id}", status_code=status.HTTP_200_OK)
async def get_unique_project(
    db: db_dependency, user: user_dependency, project_id: int = Path(gt=0)
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    project = db.query(Project).filter_by(user_id=user.get("id"), id=project_id).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


# Create project
@rout.post("/create", status_code=status.HTTP_201_CREATED)
async def create_project(
    db: db_dependency, user: user_dependency, data: ProjectRequest
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    new_project = Project(
        name=data.name, description=data.description, user_id=user.get("id")
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


# edit project
@rout.put("/edit-project/{project_id}", status_code=status.HTTP_200_OK)
async def edit_project(
    db: db_dependency,
    user: user_dependency,
    data: ProjectRequest,
    project_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    project = db.query(Project).filter_by(user_id=user.get("id"), id=project_id).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    setattr(project, "name", data.name)
    setattr(project, "description", data.description)

    db.commit()
    db.refresh(project)

    return project


# Delete project
@rout.delete("/delete-project/{project_id}", status_code=status.HTTP_200_OK)
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
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")

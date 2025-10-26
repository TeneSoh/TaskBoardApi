import traceback
from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from src.models import Task
from src.routes.auth.auth import get_current_user
from src.services.services import *

route = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskRequest(BaseModel):
    title: str
    description: str
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.LOW
    deadline: datetime  # type: ignore
    project_id: int
    # user_id: int


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    deadline: Optional[datetime] = None  # type: ignore
    project_id: Optional[int] = None
    user_id: Optional[int] = None


user_dependency = Annotated[dict, Depends(get_current_user)]


@route.get("/", status_code=status.HTTP_200_OK)
async def get_tasks(db: db_dependency, user: user_dependency):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        tasks = db.query(Task).filter(Task.user_id == user.get("id")).all()

        return tasks
    except Exception as e:
        print("ERREUR get_tasks :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@route.post("/create-task", status_code=status.HTTP_201_CREATED)
async def create_task(db: db_dependency, user: user_dependency, task: TaskRequest):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        data = task.model_dump()

        # Convertir la deadline (string ISO → datetime)
        if isinstance(data.get("deadline"), str):
            data["deadline"] = datetime.fromisoformat(data["deadline"])

        new_task = Task(**data, user_id=user.get("id"))
        db.add(new_task)
        db.commit()
        db.refresh(new_task)

        return new_task
    except Exception as e:
        print("ERREUR create_task :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@route.put("/update-task/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(
    db: db_dependency,
    user: user_dependency,
    task: TaskUpdate,
    task_id: int = Path(gt=0),
):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        existing_task = (
            db.query(Task)
            .filter(Task.id == task_id, Task.user_id == user.get("id"))
            .first()
        )
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")

        for key, value in task.model_dump().items():
            if value is not None:
                setattr(existing_task, key, value)

        db.commit()
        db.refresh(existing_task)

        return existing_task
    except Exception as e:
        print("ERREUR update_task :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@route.delete("/delete-task/{task_id}", status_code=status.HTTP_200_OK)
async def delete_task(
    db: db_dependency, user: user_dependency, task_id: int = Path(gt=0)
):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        existing_task = (
            db.query(Task)
            .filter(Task.id == task_id, Task.user_id == user.get("id"))
            .first()
        )
        if not existing_task:
            raise HTTPException(status_code=404, detail="Task not found")

        db.delete(existing_task)
        db.commit()
        return existing_task
    except Exception as e:
        print("ERREUR delete_task :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@route.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_tasks(
    db: db_dependency, user: user_dependency, user_id: int = Path(gt=0)
):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        tasks = db.query(Task).filter(Task.user_id == user_id).all()
        return tasks
    except Exception as e:
        print("ERREUR get_user_tasks :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

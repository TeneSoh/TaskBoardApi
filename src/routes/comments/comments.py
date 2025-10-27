import traceback
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from src.models import Comment
from src.routes.auth.auth import get_current_user
from src.services.services import *

user_dependency = Annotated[dict, Depends(get_current_user)]
route = APIRouter(prefix="/comment", tags=["comments"])


class CommentRequest(BaseModel):
    content: str
    task_id: int


class CommentUpdate(BaseModel):
    content: Optional[str] = None


# Get all user task comments
@route.get("/{task_id}", status_code=status.HTTP_200_OK)
async def get_all_task_comment(
    db: db_dependency, user: user_dependency, task_id: int = Path(gt=0)
):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")
        comments = (
            db.query(Comment).filter_by(user_id=user.get("id"), task_id=task_id).all()
        )

        return comments

    except Exception as e:
        print("ERREUR get_all_task_comment :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Create Comment by log user
@route.post("/creat-comment/", status_code=status.HTTP_201_CREATED)
async def create_comment(
    db: db_dependency, user: user_dependency, data: CommentRequest
):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        comment = Comment(**data.model_dump(), user_id=user.get("id"))

        db.add(comment)
        db.commit()
        db.refresh(comment)

        return comment
    except Exception as e:
        print("ERREUR create_comment :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# Edit comment by user
@route.put("/edit-comment/{comment_id}", status_code=status.HTTP_200_OK)
async def edit_comment(
    db: db_dependency,
    user: user_dependency,
    data: CommentUpdate,
    comment_id: int = Path(gt=0),
):
    try:
        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")

        edit_comment = db.query(Comment).filter_by(id=comment_id).first()
        print(edit_comment)
        if edit_comment is None:
            raise HTTPException(status_code=404, detail="Comment not found")

        new_data = data.model_dump()
        setattr(edit_comment, "content", new_data.get("content"))

        db.commit()
        db.refresh(edit_comment)

        return edit_comment

    except Exception as e:
        print("ERREUR edit_comment :", e)
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

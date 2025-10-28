import shutil
from pathlib import Path as Pathlib

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from src.models import User
from src.routes.auth.auth import get_current_user
from src.services.services import *

route = APIRouter(prefix="/user", tags=["users"])

user_dependency = Annotated[dict, Depends(get_current_user)]


# Edit user profile
@route.put("/edit/", status_code=status.HTTP_200_OK)
async def edit_user_profile(
    db: db_dependency,
    user: user_dependency,
    username: str = Form(...),
    email: str = Form(...),
    profile_image: UploadFile = File(None),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    edit_user = db.query(User).filter_by(id=user.get("id")).first()

    if profile_image is None:
        setattr(edit_user, "username", username)
        setattr(edit_user, "email", email)

        db.commit()
        db.refresh(edit_user)
        return {"message": "Profil mis à jour sans image", "user": edit_user}

    # Ajout de l'image
    if profile_image is not None:
        content_type = getattr(profile_image, "content_type", None)
        if content_type is None or not content_type.startswith("image/"):
            raise HTTPException(
                status_code=400, detail="Ce fichier n'est pas une image valide"
            )

    path = Pathlib.cwd().parent.parent / "images/profiles" / str(user.get("id"))
    imagepath = Pathlib(path)
    imagepath.mkdir(exist_ok=True, parents=True)

    file_path = imagepath / f"{user.get('id')}_{profile_image.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(profile_image.file, buffer)

    setattr(edit_user, "profile_image", str(file_path))
    setattr(edit_user, "username", username)
    setattr(edit_user, "email", email)

    db.commit()
    db.refresh(edit_user)
    return {"message": "Profil mis à jour avec image", "user": edit_user}

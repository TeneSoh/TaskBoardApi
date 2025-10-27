from fastapi import FastAPI

import src.routes.auth.auth as auths
import src.routes.comments.comments as comments
import src.routes.projects.projects as projects
import src.routes.tasks.task as tasks
from src.services.services import *

app = FastAPI()

# using routes
app.include_router(auths.route)
app.include_router(projects.route)
app.include_router(tasks.route)
app.include_router(comments.route)

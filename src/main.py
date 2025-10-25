from fastapi import FastAPI

import src.routes.auth.auth as auth
import src.routes.projects.projects as projects
from src.services.services import *

app = FastAPI()

# using routes
app.include_router(auth.route)
app.include_router(projects.rout)

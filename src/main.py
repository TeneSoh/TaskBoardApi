from fastapi import FastAPI

import src.routes.auth as auth
from src.services.services import *

app = FastAPI()

# using routes
app.include_router(auth.route)

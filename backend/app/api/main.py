from fastapi import APIRouter

from backend.app.api.routes import audio
from backend.app.api.routes import users, login

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(audio.router, tags=["audio"])


# from sqlmodel import SQLModel
# SQLModel.metadata.create_all(engine)
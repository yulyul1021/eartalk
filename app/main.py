from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from app.api.main import api_router
from app.core.config import settings

app = FastAPI()
app.include_router(api_router)
app.mount(f'/{settings.AUDIO_DIR}', StaticFiles(directory=settings.AUDIO_DIR_NAME), name=settings.AUDIO_DIR_NAME)

origins = [
    "http://localhost:3000",
    "localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
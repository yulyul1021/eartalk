import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.api.dependencies import CurrentUser, SessionDep
from app.core.config import settings
from app.models import AudioPublic, Audio

router = APIRouter()


@router.post("/", response_model=AudioPublic)
async def create_audio(
        *, session: SessionDep, current_user: CurrentUser,
        text: str = None, audio: UploadFile = File(None)
) -> Any:
    """
    Create new audio.
    """
    if not text and not audio:
        raise HTTPException(status_code=400, detail="텍스트 혹은 음성 둘 중 하나를 입력해주세요.")
    if text and audio:
        raise HTTPException(status_code=400, detail="텍스트 혹은 음성 둘 중 하나만 입력해주세요.")

    # TODO 원본 wav 저장
    # TODO 가공 wav 저장
    audio = Audio.model_validate({
        "text":         "임시 text입니다.",
        "original":     settings.ORIGINAL_AUDIO_DIR + str(uuid.uuid4()) + ".wav",
        "processed":    settings.PROCESSED_AUDIO_DIR + str(uuid.uuid4()) + ".wav",
        "create_date":  datetime.now()
    }, update={"owner_id": current_user.id})
    session.add(audio)
    session.commit()
    session.refresh(audio)
    return audio
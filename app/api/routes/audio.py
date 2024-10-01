import os
import shutil
import uuid
from datetime import datetime, timezone
from typing import Any, Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from sqlmodel import select
from starlette.responses import FileResponse

from app.api.dependencies import SessionDep, OptionalCurrentUser
from app.core.config import settings
from app.models import AudioPublic, Audio
from app.utils import utils
from app.utils.utils import get_hashed_folder_name

router = APIRouter()


@router.get("/")
def index():
    return FileResponse("frontend/build/index.html")


@router.post("/audio", response_model=AudioPublic)
async def create_audio(
    *,
    session: SessionDep,
    current_user: OptionalCurrentUser,
    input_text: Annotated[str | None, Form()] = None,
    audio: Annotated[UploadFile | None, File()] = None
) -> Any:
    """
    Create new audio.
    """

    if not input_text and not audio:
        raise HTTPException(status_code=400, detail="텍스트 혹은 음성 둘 중 하나를 입력해주세요.")
    if input_text and audio:
        raise HTTPException(status_code=400, detail="텍스트 혹은 음성 둘 중 하나만 입력해주세요.")

    # current_user가 없을 경우 id를 0으로 설정
    user_id = current_user.id if current_user else 0

    # 사용자별 폴더 경로 생성
    user_folder_name = get_hashed_folder_name(user_id)
    user_folder = os.path.join(settings.AUDIO_ROOT, user_folder_name)
    original_folder = os.path.join(user_folder, "original")
    processed_folder = os.path.join(user_folder, "processed")

    # 폴더가 존재하지 않으면 생성
    os.makedirs(original_folder, exist_ok=True)
    os.makedirs(processed_folder, exist_ok=True)

    # UUID를 이용한 파일 이름 생성
    file_uuid = str(uuid.uuid4())
    original_file_path = os.path.join(original_folder, f"{file_uuid}.wav")
    print(original_file_path)

    # 원본 wav 저장
    if audio:
        try:
            data = await audio.read()
            with open(original_file_path, "wb") as f:
                f.write(data)
        finally:
            await audio.close()  # 파일을 명시적으로 닫기
        input_text = utils.temp_speech_to_text(audio)    # FIXME 테스트용

    # FIXME 가공 로직 (임시)
    processed_file_path = os.path.join(processed_folder, f"{file_uuid}_processed.wav")
    processed_audio = utils.temp_text_to_speech(input_text)
    data = processed_audio.file.read()  # 비동기 처리가 필요 없습니다.
    with open(processed_file_path, "wb") as f:
        f.write(data)

    audio = Audio.model_validate({
        "text":                 input_text,
        "original_filepath":    original_file_path,
        "processed_filepath":   processed_file_path,
        "create_date":          datetime.now(),
        "identifier":           utils.generate_uuid()
    }, update={"owner_id": current_user.id if current_user else None})
    session.add(audio)
    session.commit()
    session.refresh(audio)
    return audio


@router.get("/audio/{identifier}", response_model=AudioPublic)
async def get_file_info(session: SessionDep, identifier: str) -> Any:
    '''
    식별자로 파일 정보 가져오기
    '''
    statement = select(Audio).where(Audio.identifier == identifier)
    audio = session.exec(statement).first()
    return audio


@router.get("/audio/{folder}/{file_type}/{filename}")
async def get_file(folder: str, file_type: str, filename: str):
    file_path = os.path.join("audio", folder, file_type, filename)

    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        return {"error": "File not found"}
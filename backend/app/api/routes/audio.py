import os
from datetime import datetime
from typing import Any, Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from sqlmodel import select, col
from starlette.responses import FileResponse

from backend.app.api.dependencies import SessionDep, OptionalCurrentUser
from backend.app.core.config import settings
from backend.app.models import AudioPublic, Audio
from backend.app.utils import utils
from backend.app.utils.api_client import send_tts_request, send_stt_tts_request

router = APIRouter()


@router.get("/")
def index():
    return FileResponse("frontend/build/index.html")


@router.post("/audio", response_model=AudioPublic)
async def create_audio(
    *,
    session:        SessionDep,
    current_user:   OptionalCurrentUser,
    input_text:     Annotated[str | None, Form()] = None,
    audio:          Annotated[UploadFile | None, File()] = None
) -> Any:
    """
    Create new audio.
    """
    if not input_text and not audio:
        raise HTTPException(status_code=400, detail="텍스트 혹은 음성 둘 중 하나를 입력해주세요.")
    if input_text and audio:
        raise HTTPException(status_code=400, detail="텍스트 혹은 음성 둘 중 하나만 입력해주세요.")

    create_date = datetime.now()
    file_paths = utils.create_file_path(create_date)
    original_file_path = str(file_paths["original_file_path"])
    processed_file_path = str(file_paths["processed_file_path"])

    if input_text and current_user:
        # text input: ref 음성 추출
        # current_user의 가장 최근 음성을 ref로 쓴다. 만약 없다면 기본 ref
        statement = select(Audio).where(Audio.owner_id == current_user.id).order_by(col(Audio.id).desc())
        ref_audio_path = session.exec(statement).first()
        if ref_audio_path:
            with open(ref_audio_path, "rb") as file:
                ref_audio = file.read()
        else:
            ref_audio = utils.get_default_ref_audio(current_user)

        # text input: AI 모델 서버로 TTS API 요청 보내기
        try:
            file = {'file': (audio.filename, ref_audio, audio.content_type)}
            data = {'text': input_text, 'output_path': processed_file_path}
            result = send_tts_request(settings.AI_REQUEST_URL, file, data)
            processed_file_path = result["file_path"]

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"audio processing failed: {str(e)}")

    if audio:
        try:
            # audio input: 원본 wav 저장
            audio_data = await audio.read()
            with open(original_file_path, "wb") as f:
                f.write(audio_data)

            # audio input: AI 모델 서버로 STT + TTS 요청 보내기
            files = {'file': (audio.filename, audio_data, audio.content_type)}
            data = {'output_path': processed_file_path}
            result = send_stt_tts_request(settings.AI_REQUEST_URL, files, data)
            input_text = result["stt_result"]["text"]
            processed_file_path = result["tts_result"]["file_path"]

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"audio processing failed: {str(e)}")

    audio_data = Audio.model_validate({
        "text":                 input_text,
        "original_filepath":    original_file_path,
        "processed_filepath":   processed_file_path,
        "create_date":          create_date,
        "identifier":           utils.generate_uuid()
    }, update={"owner_id": current_user.id if current_user else None})
    session.add(audio_data)
    session.commit()
    session.refresh(audio_data)
    return audio_data


@router.get("/audio/{identifier}", response_model=AudioPublic)
async def get_file_info(session: SessionDep, identifier: str) -> Any:
    '''
    식별자로 파일 정보 가져오기
    '''
    statement = select(Audio).where(Audio.identifier == identifier)
    audio = session.exec(statement).first()
    return audio
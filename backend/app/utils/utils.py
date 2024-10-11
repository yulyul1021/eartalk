import hashlib
import io
import logging
import logging.handlers
import os
import secrets
import string
import smtplib
import uuid
from datetime import datetime
from pathlib import Path

import speech_recognition as sr
from fastapi import UploadFile
from gtts import gTTS

from backend.app.core.config import settings
from email.message import EmailMessage
from ssl import create_default_context

from backend.app.models import User


def generate_random_string(length: str = 8) -> str:
    res = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                  for _ in range(length))
    return res


def generate_uuid():
    return str(uuid.uuid4())


# user_id를 해시하여 고유 폴더 이름 생성
def get_hashed_folder_name(id: int) -> str:
    return hashlib.sha256(str(id).encode()).hexdigest()


# 저장할 파일 경로 생성
def create_file_path(create_date: datetime):
    # 인자로 받은 create_date를 yyyy/mm/dd/hhmmssSSS 형식으로 변환
    formatted_time = create_date.strftime("%Y/%m/%d/%H%M%S%f")

    # 디렉토리 경로 생성 (yyyy/mm/dd)
    dir_path = Path(settings.MEDIA_DIR) / "/".join(formatted_time.split("/")[:-1])
    dir_path.mkdir(parents=True, exist_ok=True)  # 디렉토리 없으면 생성

    # 파일 전체 경로 생성 (원본 파일과 처리된 파일 두 가지)
    original_file_name = f"{formatted_time}_original.wav"
    processed_file_name = f"{formatted_time}_processed.wav"

    # 짧은 파일명 생성 (hhmmssSSS)
    short_original_file_name = f"{create_date.strftime('%H%M%S%f')}_original.wav"
    short_processed_file_name = f"{create_date.strftime('%H%M%S%f')}_processed.wav"

    # 파일 전체 경로와 짧은 파일명 리턴
    return {
        "original_file_path": dir_path / original_file_name,
        "processed_file_path": dir_path / processed_file_name,
        "short_original_file_name": short_original_file_name,
        "short_processed_file_name": short_processed_file_name
    }


def get_default_ref_audio(user: User) -> bytes:
    current_year = datetime.now().year
    birth_year = int(user.birthyear)  # 문자열을 정수로 변환
    age = current_year - birth_year

    age_group = "young" if age <= 29 else "old"
    gender = "male" if user.sex else "female"

    full_file_path = os.path.join(settings.DEFAULT_REF_AUDIO_DIR, f"REF_{gender}_{age_group}.wav")

    with open(full_file_path, "rb") as file:
        file_content = file.read()
    return file_content  # 파일 내용을 반환 (바이너리 데이터)


def temp_speech_to_text(audio) -> str:
    r = sr.Recognizer()
    read_audio = sr.AudioFile(audio)
    with read_audio as source:
        f = r.record(source)
    out_text = r.recognize_google(f, language="ko-KR")
    return out_text


def temp_text_to_speech(in_text: str) -> UploadFile:
    tts = gTTS(text=in_text, lang='ko')
    wav_data = io.BytesIO()
    tts.write_to_fp(wav_data)
    wav_data.seek(0)  # 파일 포인터를 시작으로 되돌려야 읽을 수 있습니다.

    # UploadFile과 유사한 객체로 변환
    return UploadFile(filename="speech.wav", file=wav_data)


def send_email_for_password(*, receiver_email: str, new_password: str) -> None:
    # 이메일 메시지 생성
    msg = EmailMessage()
    msg['Subject'] = '[이어톡] 임시 비밀번호 발급 안내'  # 제목 설정
    msg['From'] = settings.SENDER_EMAIL
    msg['To'] = receiver_email

    # HTML 본문 설정
    html_content = f"""
    <html>
        <body>
            <p style="font-size: 16px;">귀하의 임시 비밀번호는 다음과 같습니다.</p>
            <p style="font-size: 20px;"><b>{new_password}</b></p>
            <p style="font-size: 16px;">임시 비밀번호로 로그인 한 뒤, 비밀번호를 변경해 주세요.</p>
        </body>
    </html>
    """

    # HTML 본문을 이메일 메시지에 추가
    msg.add_alternative(html_content, subtype='html')

    # 이메일 전송
    context = create_default_context()
    with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_SSL_PORT, context=context) as server:
        server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        server.send_message(msg)  # 메시지 전송


def get_logger(name=None):
    # 현재 날짜에 해당하는 폴더 경로 생성
    date_str = datetime.now().strftime("%Y%m%d")
    log_dir = os.path.join(settings.LOGFILE_ROOT, date_str)

    # 폴더가 없으면 생성
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 핸들러가 중복으로 추가되지 않도록 확인
    if not logger.hasHandlers():
        # log format
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s")

        # log 파일에 기록 (일별 생성)
        console = logging.StreamHandler()
        timedfilehandler_info = logging.handlers.TimedRotatingFileHandler(
            filename=os.path.join(log_dir, "apiLog_info_{:%Y%m%d}.log".format(datetime.now())),
            when="midnight", interval=1, encoding="utf-8")
        timedfilehandler_error = logging.handlers.TimedRotatingFileHandler(
            filename=os.path.join(log_dir, "apiLog_error_{:%Y%m%d}.log".format(datetime.now())),
            when="midnight", interval=1, encoding="utf-8")

        timedfilehandler_info.setFormatter(formatter)
        timedfilehandler_error.setFormatter(formatter)

        # level 설정
        console.setLevel(logging.INFO)
        timedfilehandler_info.setLevel(logging.INFO)
        timedfilehandler_error.setLevel(logging.ERROR)

        # format
        console.setFormatter(formatter)
        timedfilehandler_info.setFormatter(formatter)
        timedfilehandler_error.setFormatter(formatter)

        # add handler
        logger.addHandler(console)
        logger.addHandler(timedfilehandler_info)
        logger.addHandler(timedfilehandler_error)

    return logger
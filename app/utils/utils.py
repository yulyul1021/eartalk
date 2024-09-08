import hashlib
import io
import logging
import logging.handlers
import os
import secrets
import string
import smtplib, ssl
from datetime import datetime

import speech_recognition as sr
from fastapi import UploadFile
from gtts import gTTS

from app.core.config import settings
from email.message import EmailMessage
from ssl import create_default_context


def generate_random_string(length: str = 8) -> str:
    res = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                  for _ in range(length))
    return res


# user_id를 해시하여 고유 폴더 이름 생성
def get_hashed_folder_name(id: int) -> str:
    return hashlib.sha256(str(id).encode()).hexdigest()


def speech_to_text(audio) -> str:
    r = sr.Recognizer()
    read_audio = sr.AudioFile(audio)
    with read_audio as source:
        f = r.record(source)
    out_text = r.recognize_google(f, language="ko-KR")
    return out_text


def text_to_speech(in_text: str) -> UploadFile:
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
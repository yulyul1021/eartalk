import secrets
import string
import smtplib, ssl
from app.core.config import settings


def generate_random_string(length: str = 8) -> str:
    res = ''.join(secrets.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits)
                  for _ in range(length))
    return res


context = ssl.create_default_context()

def send_email_for_password(*, receiver_email: str, new_password: str) -> None:
    with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_SSL_PORT, context=context) as server:
        server.login(settings.SENDER_EMAIL, settings.SENDER_PASSWORD)
        server.sendmail(settings.SENDER_EMAIL, receiver_email, # 제목 [이어톡] 임시 비밀번호 발급 안내
                        f"귀하의 임시 비밀번호는 다음과 같습니다.\n"
                        f"{new_password}", )
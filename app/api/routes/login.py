from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.dependencies import SessionDep
from app.core import security
from app.core.config import settings
from app.models import Token, Message

router = APIRouter()


# 로그인(JWT 생성)
@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires
        )
    )


# 비밀번호 찾기
@router.post("/reset-password/{email}", response_model=Message)
def reset_password(session: SessionDep, email: str) -> Message:
    """
    비밀번호 찾기(임시 비밀번호 발급)
    """
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this email does not exist in the system.",
        )
    # TODO 임시 비밀번호 생성 + db 저장 + 메일 전송
    return Message(message="임시 비밀번호가 발송되었습니다. 메일함을 확인해주세요.")
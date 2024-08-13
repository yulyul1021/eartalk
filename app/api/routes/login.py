from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.dependencies import SessionDep, QueryDep
from app.core import security
from app.core.config import settings
from app.models import Token, Message
from app.utils.kakao_manager import kakao_api
from app.utils.naver_manager import naver_api

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


@router.post("/login/kakao-login")
async def login_kakao_token(
    session: SessionDep, code: QueryDep
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    kakao_token = await kakao_api.get_token(code) # 이거 버리고 새로 발급할 것
    user_info = await kakao_api.get_user_info(kakao_token)
    # user_info에서 이메일 가져와서 회원 조회 해서 있으면 토큰발급
    # 없으면 회원가입 시키고 토큰 발급


@router.post("/login/naver-login")
async def login_naver_token(
    session: SessionDep, code: QueryDep
) -> Token:
    naver_token = await naver_api.get_token(code)  # 이거 버리고 새로 발급할 것
    user_info = await naver_api.get_user_info(naver_token)
    # user_info에서 이메일 가져와서 회원 조회 해서 있으면 토큰발급
    # 없으면 회원가입 시키고 토큰 발급


@router.post("/login/google-login")
async def login_google_token(
    session: SessionDep, code: QueryDep
) -> Token:
    pass


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
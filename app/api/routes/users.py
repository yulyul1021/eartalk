from typing import Any

from fastapi import APIRouter, HTTPException

from app import crud
from app.api.dependencies import SessionDep, CurrentUser
from app.core.security import verify_password, get_password_hash
from app.models import UserCreate, UserRegister, UserPublic, Message, UpdatePassword

router = APIRouter()


@router.post("/signup")
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    """
    유저 생성(회원가입)
    """
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    if user_in.password != user_in.verify_password:
        raise HTTPException(
            status_code=400,
            detail="비밀번호가 다릅니다.",
        )

    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return user


@router.post("/password", response_model=Message)
def update_password(
        *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    비밀번호 변경
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="비밀번호가 올바르지 않습니다.")

    if body.new_password != body.verify_new_password:
        raise HTTPException(
            status_code=400,
            detail="비밀번호가 다릅니다.",
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="비밀번호가 성공적으로 변경되었습니다.")



from typing import Annotated

from fastapi import Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.orm import Session, sessionmaker
from starlette import status
from sqlmodel import Session as SQLModelSession

from app.core import security
from app.core.config import settings
from app.core.database import engine
from app.models import User, TokenPayload


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/login/access-token"
)
optional_reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/login/access-token",
    auto_error=False
)

SessionLocal = sessionmaker(class_=SQLModelSession, autoflush=False, bind=engine)


def get_session():
    with SessionLocal() as session:
        yield session


QueryDep = Annotated[str, Query()]
SessionDep = Annotated[Session, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
OptionalTokenDep = Annotated[str, Depends(optional_reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_user_or_none(session: SessionDep, token: OptionalTokenDep) -> User | None:
    if token:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
            token_data = TokenPayload(**payload)
        except (InvalidTokenError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
        user = session.get(User, token_data.sub)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    return None


OptionalCurrentUser = Annotated[User | None, Depends(get_current_user_or_none)]
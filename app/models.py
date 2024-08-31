from datetime import datetime
from typing import List

from fastapi import UploadFile
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


class UserBase(SQLModel):
    email:      EmailStr | None = Field(unique=True, max_length=255)
    birthyear:  str | None = Field(min_length=4, max_length=4)
    sex:        bool | None  # True male False female


class UserCreate(UserBase):
    oauth_id: str | None = Field(default=None, unique=True)  # 소셜 로그인용
    password: str | None = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email:              EmailStr | None = Field(unique=True, max_length=255)
    password:           str = Field(min_length=8, max_length=40)
    verify_password:    str = Field(min_length=8, max_length=40)
    birthyear:          str | None = Field(min_length=4, max_length=4)
    sex:                bool  # True: male, False: female


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)
    verify_new_password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):
    id:                 int | None = Field(default=None, primary_key=True)
    oauth_id:           str | None = Field(default=None, unique=True)   # 소셜 로그인용
    hashed_password:    str | None  # None -> 소셜 회원가입 시
    audios:             list["Audio"] = Relationship(back_populates="owner")


class UserPublic(UserBase):
    id: int


class AudioBase(SQLModel):
    text:       str
    original_filepath:   str # filepath
    processed_filepath:  str # filepath


class AudioCreate(SQLModel):
    text:   str | None = Field(default=None)
    audio:  UploadFile | None = Field(default=None)


class Audio(AudioBase, table=True):
    id:             int | None = Field(default=None, primary_key=True)
    owner_id:       int | None = Field(default=None, foreign_key="user.id")
    owner:          User | None = Relationship(back_populates="audios")
    create_date:    datetime


class AudioPublic(AudioBase):
    id:         int


class AudiosPublic(SQLModel):
    data: List[AudioPublic] | None
    count: int


class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token:   str
    token_type:     str = "bearer"


class TokenPayload(SQLModel):
    sub: int | None = None

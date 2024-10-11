from datetime import datetime

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.concurrency import iterate_in_threadpool
from starlette.staticfiles import StaticFiles

from backend.app.api.main import api_router
from backend.app.utils.utils import get_logger

app = FastAPI()
app.include_router(api_router)
app.mount("/static", StaticFiles(directory="frontend/build/static"))
# app.mount(f'/{settings.AUDIO_DIR}', StaticFiles(directory=), name=settings.)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 로깅 미들웨어
# @app.middleware("http")
# async def log_request(request: Request, call_next):
#     logger = get_logger()
#
#     # 유입 시간
#     start_time = datetime.utcnow()
#
#     # 요청 로깅
#     logger.info(f"Request: {request.method} {request.url}")
#     body = await request.body()
#
#     # UTF-8로 디코딩할 수 없는 경우에 대비하여 예외 처리
#     try:
#         # 본문이 텍스트일 경우에만 UTF-8로 디코딩
#         logger.info(f"Request Body: {body.decode('utf-8')}")
#     except UnicodeDecodeError:
#         # 디코딩할 수 없는 경우 바이너리 데이터를 기록하거나 생략
#         logger.info("Request Body contains non-text data.")
#
#     response = await call_next(request)
#
#     # 응답 로깅
#     logger.info(f"Response: {response.status_code}")
#
#     # 응답 본문 읽기 및 로그 기록
#     response_body = [chunk async for chunk in response.body_iterator]
#
#     if response_body:  # 응답 본문이 비어있지 않은 경우에만 처리
#         try:
#             logger.info(f"Response Body: {response_body[0].decode()}")
#         except UnicodeDecodeError:
#             logger.info("Response Body contains non-text data.")
#     else:
#         logger.info("Response Body is empty.")
#
#     # 응답 본문 다시 설정 (원래 상태로 돌려놓기)
#     response.body_iterator = iterate_in_threadpool(iter(response_body))
#
#     # 작업 시간 로깅
#     process_time = (datetime.utcnow() - start_time).total_seconds()
#     logger.info(f"Process-Time: {'{:.3f}'.format(process_time)}")
#
#     return response
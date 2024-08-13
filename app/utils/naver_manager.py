import uuid

import httpx # aiohttp 로 변경해야함
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class NaverAPI:
    def __init__(self):
        # 카카오 API 관련 정보를 환경 변수에서 로드
        self.client_id = os.getenv('')
        self.client_secret = os.getenv('')
        self.redirect_uri = os.getenv('')
        self.rest_api_key = os.getenv('')
        self.logout_redirect_uri = os.getenv('')

    async def get_token(self, code):
        # 네이버로부터 인증 코드를 사용해 액세스 토큰 요청
        token_request_url = 'https://nid.naver.com/oauth2.0/token'
        token_request_payload = {
            "grant_type": "code",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "state": str(uuid.uuid4())
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_request_url, data=token_request_payload)
        result = response.json()
        return result

    async def get_user_info(self, access_token):
        # 액세스 토큰을 사용하여 네이버로부터 사용자 정보 요청
        userinfo_endpoint = 'https://openapi.naver.com/v1/nid/me'
        headers = {'Authorization': f'Bearer {access_token}'}

        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_endpoint, headers=headers)
        return response.json() if response.status_code == 200 else None

    # async def refreshAccessToken(self, clientId, refresh_token):
    #     # 리프레시 토큰을 사용하여 액세스 토큰 갱신 요청
    #     url = "https://kauth.kakao.com/oauth/token"
    #     payload = {
    #         "grant_type": "refresh_token",
    #         "client_id": clientId,
    #         "refresh_token": refresh_token
    #     }
    #
    #     async with httpx.AsyncClient() as client:
    #         response = await client.post(url, data=payload)
    #     refreshToken = response.json()
    #     return refreshToken


naver_api = NaverAPI()
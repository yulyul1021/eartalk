import uuid
import json
import httpx # aiohttp 로 변경해야함
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class KakaoAPI:
    def __init__(self):
        # 카카오 API 관련 정보를 환경 변수에서 로드
        self.client_id = os.getenv('KAKAO_CLIENT_ID')
        self.client_secret = os.getenv('KAKAO_CLIENT_SECRET')
        self.redirect_uri = os.getenv('KAKAO_REDIRECT_URI')

    async def get_token(self, code):
        # 카카오로부터 인증 코드를 사용해 액세스 토큰 요청
        token_request_url = 'https://kauth.kakao.com/oauth/token'
        token_request_payload = {
            "grant_type": "authorization_code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "code": code,
            "client_secret": self.client_secret
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_request_url, data=token_request_payload)
        result = response.json()
        return result

    async def get_user_info(self, access_token):
        # 액세스 토큰을 사용하여 카카오로부터 사용자 정보 요청
        userinfo_endpoint = 'https://kapi.kakao.com/v2/user/me'
        headers = {'Authorization': f'Bearer {access_token}'}

        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_endpoint, headers=headers)
        return response.json() if response.status_code == 200 else None


class NaverAPI:
    def __init__(self):
        # 네이버 API 관련 정보를 환경 변수에서 로드
        self.client_id = os.getenv('NAVER_CLIENT_ID')
        self.client_secret = os.getenv('NAVER_CLIENT_SECRET')
        self.redirect_uri = os.getenv('NAVER_REDIRECT_URI')

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


class GoogleAPI:
    def __init__(self):
        # 구글 API 관련 정보를 환경 변수에서 로드
        self.client_id = os.getenv('')
        self.client_secret = os.getenv('')
        self.redirect_uri = os.getenv('')
        self.rest_api_key = os.getenv('')
        self.logout_redirect_uri = os.getenv('')

    async def get_token(self, code):
        # 구글로부터 인증 코드를 사용해 액세스 토큰 요청
        token_request_url = 'https://oauth2.googleapis.com/token'
        token_request_payload = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": 'authorization_code'
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(token_request_url, data=token_request_payload)
        result = response.json()
        return result

    async def get_user_info(self, access_token):
        # 액세스 토큰을 사용하여 구글로부터 사용자 정보 요청
        userinfo_endpoint = 'https://www.googleapis.com/userinfo/v2/me'
        headers = {'Authorization': f'Bearer {access_token}'}

        async with httpx.AsyncClient() as client:
            response = await client.get(userinfo_endpoint, headers=headers)
        return response.json() if response.status_code == 200 else None


kakao_api = KakaoAPI()
naver_api = NaverAPI()
google_api = GoogleAPI()

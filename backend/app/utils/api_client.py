import requests
from fastapi import HTTPException


def send_tts_request(ai_url, files, data):
    try:
        response = requests.post(f"{ai_url}/tts", files=files, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=f"API call failed with status: {response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"External API call failed: {str(e)}")


def send_stt_tts_request(ai_url, files, data):
    try:
        response = requests.post(f"{ai_url}/stt_tts", files=files, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=response.status_code, detail=f"API call failed with status: {response.status_code}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"External API call failed: {str(e)}")

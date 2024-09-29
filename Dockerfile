FROM python:3.9-slim

# venv 패키지 설치 (추가)
RUN apt-get update && apt-get install -y python3-venv

# 작업 디렉토리 설정
WORKDIR /app

# 가상환경 생성
RUN python3 -m venv venv

# 가상환경을 이용해 필요한 패키지 설치
COPY requirements.txt .
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt

# 소스코드 복사
COPY . .

# 컨테이너 시작 시 가상환경을 사용하여 애플리케이션 실행
CMD ["/app/venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
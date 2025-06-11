# Dockerfile

# 파이썬 공식 이미지를 기반으로 합니다.
FROM python:3.9-slim-buster

# 작업 디렉토리를 설정합니다.
WORKDIR /app

# 필요한 파이썬 패키지를 설치합니다.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 스크립트와 data 디렉토리를 컨테이너에 복사합니다.
COPY data/ data/
COPY handwriting_practice_generator.py .

# 컨테이너가 시작될 때 실행될 기본 명령어를 설정합니다.
ENTRYPOINT ["python", "handwriting_practice_generator.py"]

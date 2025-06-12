# Dockerfile
FROM python:3.11-slim-buster

# 작업 디렉토리를 설정합니다.
WORKDIR /app

# 전체 파일을 컨테이너에 복사합니다.
COPY . .

# uv를 설치하고 의존성을 동기화합니다.
# uv sync는 pyproject.toml에 정의된 모든 의존성을 설치합니다.
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir uv && \
    uv sync

# pyproject.toml에 정의된 스크립트('pdf-generate')를 uv를 통해 실행합니다.
# uv run은 프로젝트의 스크립트 항목을 실행하는 데 사용됩니다.
CMD ["uv", "run", "pdf-generate", "--input_dir", "data/input"]

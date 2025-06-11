# practice-handwriting

Generate handwriting templates for practice.

이 프로젝트는 파이썬을 사용하여 **모눈 종이 배경의 손글씨 연습 시트 PDF를 자동으로 생성**하는 도구입니다. 특정 텍스트 파일(들)에 있는 문구를 여러 폰트 파일(들)을 적용하여 다양한 연습 시트를 만들 수 있으며, Docker 및 GitHub Actions를 통해 PDF 생성 및 릴리스 과정을 자동화합니다.


## ✨ 주요 기능

* **다중 텍스트 파일 지원**: `data/input/` 폴더 내의 모든 `.txt` 파일에 있는 문구를 사용하여 PDF를 생성합니다.
* **다중 폰트 지원**: `data/fonts/` 폴더 내의 모든 `.ttf` 또는 `.otf` 폰트를 사용하여 각 텍스트 파일에 대해 다양한 스타일의 연습 시트를 만듭니다.
* **모눈 종이 배경**: PDF 시트는 사용자 지정 가능한 간격의 모눈 종이 배경을 가집니다.
* **커스터마이징 가능한 설정**: 폰트 크기, 줄 높이, 모눈 간격 등을 명령줄 인자를 통해 쉽게 조절할 수 있습니다.
* **Docker 지원**: 컨테이너화된 환경에서 일관된 PDF 생성을 보장합니다.
* **GitHub Actions 자동화**: 코드 변경 사항이 푸시되거나 수동으로 트리거될 때마다 자동으로 PDF를 생성하고 GitHub Releases에 압축 파일 형태로 릴리스합니다.


## 📂 프로젝트 구조

프로젝트는 다음 디렉토리 구조를 가집니다:

```
.
├── data/
│   ├── fonts/
│   │   ├── NanumPenScript-Regular.ttf  # 사용할 폰트 파일들을 여기에 넣으세요 (.ttf 또는 .otf)
│   │   └── YourAnotherFont.ttf
│   ├── input/
│   │   ├── my_text_1.txt                 # 연습할 문구가 담긴 텍스트 파일들을 여기에 넣으세요
│   │   └── my_text_2.txt
│   └── output/                         # 생성된 PDF 파일이 저장될 위치 (스크립트가 자동 생성)
├── .github/
│   └── workflows/
│       └── main.yml                    # GitHub Actions 워크플로우 정의
├── Dockerfile                          # Docker 이미지 빌드를 위한 설정 파일
├── handwriting_practice_generator.py   # PDF 생성 핵심 파이썬 스크립트
└── requirements.txt                    # 파이썬 종속성 목록
```


## 🚀 시작하기

### 📝 전제 조건

* **Python 3.11+**: 스크립트 실행을 위한 파이썬 환경.
* **pip**: 파이썬 패키지 관리자 (파이썬 설치 시 함께 설치됨).
* **Docker**: 컨테이너 환경에서 실행하거나 GitHub Actions의 Docker 빌드를 사용하기 위함.
* **Git**: 리포지토리를 클론하기 위함.

### 💻 로컬 환경 설정 및 실행

1.  **리포지토리 클론**:
    ```bash
    git clone [https://github.com/your-username/practice-handwriting.git](https://github.com/your-username/practice-handwriting.git)
    cd practice-handwriting
    ```

2.  **파이썬 종속성 설치**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **데이터 준비**:
    * `data/fonts/` 폴더 안에 사용할 **폰트 파일(.ttf 또는 .otf)**을 복사합니다. (예: `NanumPenScript-Regular.ttf`)
    * `data/input/` 폴더 안에 연습할 문구가 담긴 **텍스트 파일(.txt)**을 생성합니다.
        예시: `data/input/my_text.txt`
        ```
        안녕하세요.
        반갑습니다.
        손글씨 연습을 시작해볼까요?
        즐거운 시간 되세요.
        ```

4.  **스크립트 직접 실행**:
    ```bash
    python handwriting_practice_generator.py \
      --input_dir data/input \
      --font_dir data/fonts \
      --output_dir data/output \
      --font_size 24 \
      --line_height_factor 1.5 \
      --grid_spacing_mm 10
    ```
    * 생성된 PDF 파일은 `data/output/` 폴더에 `[텍스트파일명]_[폰트파일명].pdf` 형식으로 저장됩니다.

5.  **Docker를 사용하여 실행**:
    * **Docker 이미지 빌드**:
        ```bash
        docker build -t handwriting-generator .
        ```
    * **Docker 컨테이너 실행 및 PDF 생성**:
        (생성된 PDF 파일이 호스트 머신의 `data/output` 폴더에 저장되도록 볼륨 마운트)
        ```bash
        docker run -v "$(pwd)/data/output:/app/data/output" handwriting-generator \
          --input_dir "/app/data/input" \
          --font_dir "/app/data/fonts" \
          --output_dir "/app/data/output" \
          --grid_spacing_mm 8
        ```
        * `--input_dir` 및 `--font_dir` 경로는 **Docker 컨테이너 내부의 경로**를 나타냅니다.
        * 생성된 PDF 파일은 호스트 머신의 `data/output/` 폴더에서 확인할 수 있습니다.

## 🤖 GitHub Actions 통합

이 프로젝트는 GitHub Actions를 활용하여 코드 푸시 시 자동으로 PDF를 생성하고 GitHub Releases에 압축 파일 형태로 업로드합니다.

**다음 단계:**

1.  **프로젝트 파일 준비**: 위에서 설명한 `data/fonts`, `data/input`, `.github/workflows` (및 그 안의 `main.yml`), `Dockerfile`, `handwriting_practice_generator.py`, `requirements.txt` 파일들을 올바른 위치에 배치합니다.
2.  **GitHub 리포지토리 생성 및 푸시**: 이 모든 파일을 GitHub 리포지토리 (예: `main` 브랜치)에 푸시합니다.
3.  **GitHub Actions 확인**:
    * GitHub 리포지토리 페이지에서 **"Actions" 탭**으로 이동합니다.
    * `Generate Handwriting Practice PDFs` 워크플로우가 자동으로 실행되는 것을 확인할 수 있습니다.
    * 성공적으로 완료되면 **"Releases" 탭**으로 이동하여 생성된 `handwriting_practice_pdfs.zip` 파일을 다운로드할 수 있습니다. 이 ZIP 파일에는 `data/input`의 각 텍스트 파일과 `data/fonts`의 각 폰트 조합으로 생성된 모든 PDF가 포함되어 있습니다.


## 📄 라이선스

이 프로젝트는 MIT License에 따라 라이선스가 부여됩니다.

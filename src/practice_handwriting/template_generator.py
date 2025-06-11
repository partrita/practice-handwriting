import os
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
import click

def create_grid_image(width, height, grid_spacing, line_color=(220, 220, 220)):
    """
    지정된 크기와 간격으로 모눈 종이 배경 이미지를 생성합니다. (현재 사용 안 함)
    Args:
        width (int): 이미지의 너비 (픽셀).
        height (int): 이미지의 높이 (픽셀).
        grid_spacing (int): 모눈 선 간격 (픽셀).
        line_color (tuple): 모눈 선의 RGB 색상.
    Returns:
        PIL.Image.Image: 생성된 모눈 종이 이미지.
    """
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # 가로 선 그리기
    for i in range(0, height, grid_spacing):
        draw.line([(0, i), (width, i)], fill=line_color, width=1)
    # 세로 선 그리기
    for i in range(0, width, grid_spacing):
        draw.line([(i, 0), (i, height)], fill=line_color, width=1)
    return image

def generate_practice_sheet(text_content, font_path, font_name_for_log, font_size, line_height_factor, output_filepath, grid_spacing_mm=5):
    """
    모눈 종이 배경에 텍스트를 사용하여 손글씨 연습 시트를 생성하고 PDF로 저장합니다.
    Args:
        text_content (str): 연습 시트에 들어갈 문구.
        font_path (str): 사용할 폰트 파일의 경로 (.ttf 또는 .otf).
        font_name_for_log (str): 로그 출력용 폰트 이름 (예: 파일 이름).
        font_size (int): 폰트 크기.
        line_height_factor (float): 줄 높이를 조절하는 요소 (폰트 크기에 곱해짐).
        output_filepath (str): 생성될 PDF 파일의 전체 경로 (경로 포함).
        grid_spacing_mm (int): 모눈 선 간격 (mm).
    """
    # PDF를 저장할 디렉토리가 없으면 생성합니다.
    output_dir = os.path.dirname(output_filepath)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # letter 사이즈를 사용합니다 (8.5 x 11 인치).
    page_width, page_height = letter

    # PDF 캔버스 생성
    c = canvas.Canvas(output_filepath, pagesize=letter)

    # 픽셀 단위로 모눈 간격 계산 (ReportLab은 포인트 단위를 사용하고, 1인치는 72포인트)
    # 1mm = 1/25.4 인치
    grid_spacing_pt = grid_spacing_mm * mm

    # PDF에 직접 모눈 그리기
    c.setStrokeColorRGB(0.86, 0.86, 0.86) # 회색
    c.setLineWidth(0.5)

    # 페이지 여백 설정 (mm 단위)
    margin_left = 20 * mm
    margin_right = 20 * mm
    margin_top = 20 * mm
    margin_bottom = 20 * mm

    # 세로선 그리기
    x_start = margin_left
    while x_start <= page_width - margin_right:
        c.line(x_start, margin_bottom, x_start, page_height - margin_top)
        x_start += grid_spacing_pt

    # 가로선 그리기
    y_start = margin_bottom
    while y_start <= page_height - margin_top:
        c.line(margin_left, y_start, page_width - margin_right, y_start)
        y_start += grid_spacing_pt

    try:
        # ReportLab 폰트 등록 및 설정
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        # 폰트 이름이 충돌하지 않도록 파일 경로 기반으로 고유하게 생성
        pdfmetrics.registerFont(TTFont(f'CustomFont_{font_name_for_log}', font_path))
        c.setFont(f'CustomFont_{font_name_for_log}', font_size)
    except Exception as e:
        click.echo(f"Error loading font '{font_name_for_log}' from '{font_path}': {e}. Falling back to Helvetica.", err=True)
        # 폰트 로드 실패 시 기본 폰트로 폴백
        c.setFont("Helvetica", font_size)

    line_height = font_size * line_height_factor # 줄 간격 조절

    # 텍스트 쓰기 시작 위치
    x_pos = margin_left
    y_pos = page_height - margin_top - line_height

    lines = text_content.split('\n')
    for line_text in lines:
        if y_pos < margin_bottom + line_height: # 페이지 하단에 도달하면 새 페이지 추가
            c.showPage()
            # 새 페이지에도 모눈 다시 그리기
            c.setStrokeColorRGB(0.86, 0.86, 0.86) # 회색
            c.setLineWidth(0.5)
            x_start = margin_left
            while x_start <= page_width - margin_right:
                c.line(x_start, margin_bottom, x_start, page_height - margin_top)
                x_start += grid_spacing_pt
            y_start = margin_bottom
            while y_start <= page_height - margin_top:
                c.line(margin_left, y_start, page_width - margin_right, y_start)
                y_start += grid_spacing_pt
            # 새 페이지에 폰트 다시 설정 (폰트 로드 성공 시)
            try:
                c.setFont(f'CustomFont_{font_name_for_log}', font_size)
            except Exception:
                c.setFont("Helvetica", font_size) # 폰트 로드 실패 시
            y_pos = page_height - margin_top - line_height # 새 페이지 상단부터 시작

        # 텍스트 그리기
        c.drawString(x_pos, y_pos, line_text)
        y_pos -= line_height # 다음 줄로 이동

    c.save()
    click.echo(f"'{output_filepath}' 파일이 성공적으로 생성되었습니다. (텍스트: '{text_content[:20]}...', 폰트: '{font_name_for_log}')")

@click.command()
@click.option("--input_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True), required=True,
              help="연습 시트에 포함될 문구가 있는 텍스트 파일들을 담은 디렉토리의 경로 (예: 'data/input').")
@click.option("--font_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True), required=True,
              help="사용할 폰트 파일들을 담은 디렉토리의 경로 (예: 'data/fonts').")
@click.option("--output_dir", type=click.Path(file_okay=False, dir_okay=True), default="data/output",
              help="생성될 PDF 파일들이 저장될 디렉토리의 경로 (기본값: 'data/output').")
@click.option("--font_size", type=int, default=24,
              help="폰트 크기 (기본값: 24).")
@click.option("--line_height_factor", type=float, default=1.5,
              help="줄 높이 조절 요소 (폰트 크기에 곱해짐, 기본값: 1.5).")
@click.option("--grid_spacing_mm", type=int, default=10,
              help="모눈 선 간격 (mm 단위, 기본값: 10).")
def main(input_dir, font_dir, output_dir, font_size, line_height_factor, grid_spacing_mm):
    """
    손글씨 연습 시트 PDF 생성기
    지정된 입력 디렉토리의 모든 텍스트 파일과 폰트 디렉토리의 모든 폰트를 사용하여 PDF를 생성합니다.
    """
    # 입력 텍스트 파일 목록 가져오기
    text_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.txt')]
    if not text_files:
        click.echo(f"Error: No .txt files found in '{input_dir}'.", err=True)
        exit(1)

    # 폰트 파일 목록 가져오기
    font_files = [os.path.join(font_dir, f) for f in os.listdir(font_dir) if f.endswith('.ttf') or f.endswith('.otf')]
    if not font_files:
        click.echo(f"Error: No .ttf or .otf font files found in '{font_dir}'.", err=True)
        exit(1)

    # 출력 디렉토리 생성 (클릭 옵션에서 이미 경로가 디렉토리임을 검증하지만, 없는 경우 생성)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 각 텍스트 파일과 각 폰트에 대해 PDF 생성
    for text_file_path in text_files:
        text_filename_without_ext = os.path.splitext(os.path.basename(text_file_path))[0]
        try:
            with open(text_file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        except Exception as e:
            click.echo(f"Error reading text file '{text_file_path}': {e}", err=True)
            continue # 다음 텍스트 파일로 건너뛰기

        for font_file_path in font_files:
            font_filename_without_ext = os.path.splitext(os.path.basename(font_file_path))[0]
            
            # PDF 파일 이름 생성: [텍스트파일명]_[폰트파일명].pdf
            output_filename = f"{text_filename_without_ext}_{font_filename_without_ext}.pdf"
            output_full_path = os.path.join(output_dir, output_filename)

            generate_practice_sheet(
                text_content=text_content,
                font_path=font_file_path,
                font_name_for_log=font_filename_without_ext, # 로그 출력을 위한 폰트 이름 전달
                font_size=font_size,
                line_height_factor=line_height_factor,
                output_filepath=output_full_path,
                grid_spacing_mm=grid_spacing_mm
            )

if __name__ == "__main__":
    main()
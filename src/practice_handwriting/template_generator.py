import os
from PIL import Image, ImageDraw, ImageFont
# letter 대신 A4를 사용하도록 수정
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
# ReportLab의 자동 줄바꿈을 위한 Flowables 및 스타일 임포트
from reportlab.platypus import Paragraph, Spacer, SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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

def _draw_grid_on_page(canvas_obj, doc, grid_spacing_mm, margins_pt):
    """
    각 페이지에 모눈을 그리는 헬퍼 함수입니다.
    """
    page_width, page_height = doc.pagesize
    grid_spacing_pt = grid_spacing_mm * mm
    margin_left, margin_right, margin_top, margin_bottom = margins_pt

    canvas_obj.setStrokeColorRGB(0.86, 0.86, 0.86) # 밝은 회색
    canvas_obj.setLineWidth(0.5)

    # 세로선 그리기
    x_start = margin_left
    while x_start <= page_width - margin_right:
        canvas_obj.line(x_start, margin_bottom, x_start, page_height - margin_top)
        x_start += grid_spacing_pt

    # 가로선 그리기
    y_start = margin_bottom
    while y_start <= page_height - margin_top:
        canvas_obj.line(margin_left, y_start, page_width - margin_right, y_start)
        y_start += grid_spacing_pt


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

    # A4 사이즈를 사용하고 ReportLab의 SimpleDocTemplate을 초기화합니다.
    # ReportLab은 기본적으로 포인트 단위를 사용합니다 (1인치 = 72포인트).
    # 여백을 mm 단위로 설정 후 포인트로 변환합니다.
    margin_left_mm = 20
    margin_right_mm = 20
    margin_top_mm = 20
    margin_bottom_mm = 20

    margins_pt = (margin_left_mm * mm, margin_right_mm * mm, margin_top_mm * mm, margin_bottom_mm * mm)

    doc = SimpleDocTemplate(output_filepath, pagesize=A4,
                            leftMargin=margins_pt[0],
                            rightMargin=margins_pt[1],
                            topMargin=margins_pt[2],
                            bottomMargin=margins_pt[3])

    Story = [] # PDF 내용(flowables)을 담을 리스트

    styles = getSampleStyleSheet()
    
    # 폰트 등록 및 사용
    custom_font_name = f'CustomFont_{font_name_for_log}'
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        pdfmetrics.registerFont(TTFont(custom_font_name, font_path))
        font_to_use = custom_font_name
    except Exception as e:
        click.echo(f"Error loading font '{font_name_for_log}' from '{font_path}': {e}. Falling back to Helvetica.", err=True)
        font_to_use = "Helvetica"

    # 텍스트 스타일 정의
    # ParagraphStyle을 사용하여 폰트, 크기, 줄 간격 및 자동 줄바꿈을 설정합니다.
    styles.add(ParagraphStyle(name='CustomContentStyle',
                              fontName=font_to_use,
                              fontSize=font_size,
                              # leading은 줄 간격(base-line to base-line)을 설정합니다.
                              leading=font_size * line_height_factor,
                              spaceBefore=0, # 단락 전 공간
                              spaceAfter=0,  # 단락 후 공간
                              # wrapOn=True는 Paragraph의 기본값이므로 명시적으로 설정할 필요는 없지만,
                              # 여기서는 텍스트 영역에 맞춰 자동으로 줄바꿈됩니다.
                             ))

    # 텍스트 내용을 줄바꿈 문자('\n') 기준으로 분리하여 각 줄을 별도의 단락으로 처리
    lines = text_content.split('\n')
    for line_text in lines:
        # Paragraph 객체를 생성하여 Story에 추가합니다.
        # Paragraph는 지정된 스타일과 페이지 너비에 맞춰 자동으로 텍스트를 줄바꿈합니다.
        p = Paragraph(line_text, styles['CustomContentStyle'])
        Story.append(p)
        # 각 줄/단락 사이에 추가 공간을 주기 위해 Spacer를 추가할 수 있습니다.
        # 여기서는 leading에 이미 줄 간격이 포함되어 있으므로, 필요에 따라 조절합니다.
        # Story.append(Spacer(1, font_size * (line_height_factor - 1)))

    # PDF 문서 빌드
    # onFirstPage와 onLaterPages를 사용하여 각 페이지에 모눈을 그립니다.
    doc.build(Story,
              onFirstPage=lambda canvas_obj, doc: _draw_grid_on_page(canvas_obj, doc, grid_spacing_mm, margins_pt),
              onLaterPages=lambda canvas_obj, doc: _draw_grid_on_page(canvas_obj, doc, grid_spacing_mm, margins_pt))

    click.echo(f"'{output_filepath}' 파일이 성공적으로 생성되었습니다. (텍스트: '{text_content[:20]}...', 폰트: '{font_name_for_log}')")

@click.command()
@click.option("--input_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True), required=True, default="data/input",
              help="연습 시트에 포함될 문구가 있는 텍스트 파일들을 담은 디렉토리의 경로 (예: 'data/input').")
@click.option("--font_dir", type=click.Path(exists=True, file_okay=False, dir_okay=True), required=True, default="data/fonts",
              help="사용할 폰트 파일들을 담은 디렉토리의 경로 (예: 'data/fonts').")
@click.option("--output_dir", type=click.Path(file_okay=False, dir_okay=True), default="data/output",
              help="생성될 PDF 파일들이 저장될 디렉토리의 경로 (기본값: 'data/output').")
@click.option("--font_size", type=int, default=24,
              help="폰트 크기 (기본값: 24).")
@click.option("--line_height_factor", type=float, default=1.5,
              help="줄 높이 조절 요소 (폰트 크기에 곱해짐, 기본값: 1.5).")
@click.option("--grid_spacing_mm", type=int, default=4,
              help="모눈 선 간격 (mm 단위, 기본값: 4).")
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

# -*- coding: utf-8 -*-
"""KAHA 표준 서식 스타일 — 협회 사무국 제작 양식(미용 마취 동의서)을 기준으로 삼는다.

모든 양식은 이 모듈의 요소만 조합해 만든다. 새 양식을 추가할 때 임의로
색·테두리·머리글을 만들지 말고 여기 함수를 재사용한다.

구성 요소
  page_frame()   페이지 전체를 감싸는 남색 테두리 + 중앙 워터마크 (onPage 콜백)
  title_block()  원형 엠블럼 + 큰 제목 + 근거 법령 한 줄
  info_table()   좌측 회색 라벨 열이 있는 인적사항 표
  sec()          좌측 회색 라벨 칸 + 우측 내용의 구획 상자
  bullets()      · 로 시작하는 안내 문단
  numbered()     1) 2) 3) 형식의 나열
  asa_table()    ASA 등급 · 정의 · 사망률 표
  closing()      가운데 정렬 동의 선언문
  sign_row()     날짜 + 보호자 서명란
  footer_mark()  하단 협회 로고와 회원병원 표기 (onPage 콜백에서 그림)
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image as RLImage, KeepTogether)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

FONT_DIR = "/usr/share/fonts/truetype/nanum"
pdfmetrics.registerFont(TTFont("Nanum", os.path.join(FONT_DIR, "NanumGothic.ttf")))
pdfmetrics.registerFont(TTFont("NanumB", os.path.join(FONT_DIR, "NanumGothicBold.ttf")))
pdfmetrics.registerFont(TTFont("NanumEB", os.path.join(FONT_DIR, "NanumSquareB.ttf")))   # 제목용 굵은 고딕

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "forms")
LOGO = os.path.join(BASE, "assets", "kaha-logo.png")
EMBLEM = os.path.join(BASE, "assets", "kaha-emblem.png")
LOGO_W, LOGO_H = 1197, 238

# ── 팔레트 (사무국 양식 기준) ─────────────────────────────────────
NAVY = colors.HexColor("#1B3A5C")      # 테두리 · 제목
INK = colors.HexColor("#333333")       # 본문
LABEL_BG = colors.HexColor("#EFEFEF")  # 좌측 라벨 칸 바탕
LINE = colors.HexColor("#BFBFBF")      # 표 괘선
SOFT = colors.HexColor("#767676")      # 보조 설명

# ── 페이지 규격 ──────────────────────────────────────────────────
FRAME_INSET = 9.5 * mm     # 남색 테두리가 종이 끝에서 떨어진 거리
                           # (프린터 인쇄 불가 영역에 걸리지 않도록 안쪽으로)
FRAME_W = 2.4 * mm         # 남색 테두리 두께
MARGIN = 17 * mm           # 본문 좌우 여백
TOP = 15 * mm
BOTTOM = 30 * mm           # 하단 로고 자리 확보
FOOTER_Y = 14 * mm         # 하단 협회 표기의 아래 기준선 — 인쇄 시 잘리지 않도록 여유를 둔다
W = A4[0] - 2 * MARGIN


def P(text, size=9.4, bold=False, color=INK, leading=None, align=None):
    st = ParagraphStyle("p", fontName="NanumB" if bold else "Nanum",
                        fontSize=size, leading=leading or (size + 4.4), textColor=color)
    if align is not None:
        st.alignment = align
    return Paragraph(text, st)


def _label_cell(text, note="", size=9.3):
    body = '<font size="%.1f">' % size + text.replace("\n", "<br/>") + "</font>"
    if note:
        body += ('<br/><font size="7.2" color="#767676">'
                 + note.replace("\n", "<br/>") + "</font>")
    return Paragraph(body, ParagraphStyle(
        "lb", fontName="NanumB", fontSize=size, leading=size + 3.6,
        textColor=INK, alignment=TA_CENTER))


def page_frame(canvas, doc):
    """남색 테두리 · 중앙 워터마크 · 하단 협회 표기."""
    canvas.saveState()
    # 워터마크 (엠블럼을 크게, 아주 옅게)
    canvas.saveState()
    canvas.setFillAlpha(0.04)
    canvas.setStrokeAlpha(0.04)
    wm = 118 * mm
    canvas.drawImage(EMBLEM, (A4[0] - wm) / 2, (A4[1] - wm) / 2 + 6 * mm,
                     width=wm, height=wm, mask="auto")
    canvas.restoreState()
    # 남색 테두리
    canvas.setStrokeColor(NAVY)
    canvas.setLineWidth(FRAME_W)
    canvas.roundRect(FRAME_INSET + FRAME_W / 2, FRAME_INSET + FRAME_W / 2,
                     A4[0] - 2 * FRAME_INSET - FRAME_W,
                     A4[1] - 2 * FRAME_INSET - FRAME_W, 2.5 * mm, stroke=1, fill=0)
    # 하단 협회 표기
    y = FOOTER_Y
    lh = 8.6 * mm
    lw = lh * LOGO_W / LOGO_H
    gap = 4 * mm
    note1 = "* 본 병원은 한국동물병원협회(KAHA) 회원병원입니다."
    note2 = "● Korean Animal Hospital Association (KAHA)"
    canvas.setFont("Nanum", 7.6)
    tw = max(canvas.stringWidth(note1, "Nanum", 7.6), canvas.stringWidth(note2, "Nanum", 7.6))
    x = (A4[0] - (lw + gap + tw)) / 2
    canvas.drawImage(LOGO, x, y, width=lw, height=lh, mask="auto")
    canvas.setFillColor(INK)
    canvas.drawString(x + lw + gap, y + lh - 3.4 * mm, note1)
    canvas.drawString(x + lw + gap, y + lh - 7.2 * mm, note2)
    canvas.restoreState()


def title_block(title, legal, title_size=25):
    """원형 엠블럼 + 큰 제목 + 근거 법령 한 줄."""
    eh = 13 * mm
    emblem = RLImage(EMBLEM, width=eh, height=eh)
    t = Paragraph(title, ParagraphStyle(
        "tt", fontName="NanumEB", fontSize=title_size, leading=title_size + 3, textColor=NAVY))
    head = Table([[emblem, t]], colWidths=[eh + 3 * mm, W - eh - 3 * mm])
    head.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 0), ("RIGHTPADDING", (0, 0), (0, 0), 3 * mm),
        ("LEFTPADDING", (1, 0), (1, 0), 0), ("RIGHTPADDING", (1, 0), (1, 0), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return [head, Spacer(1, 2 * mm), P(legal, size=9), Spacer(1, 3.2 * mm)]


def info_table(groups, widths, heights=None):
    """인적사항 표. groups = [(그룹명, [[셀, ...], ...]), ...]

    각 그룹의 첫 열은 자동으로 그룹명 라벨(세로 병합)이 된다.
    행 안에서 None을 넣으면 왼쪽 셀과 가로 병합된다.
    """
    rows, styles, r = [], [], 0
    for gname, grows in groups:
        start = r
        for i, cells in enumerate(grows):
            row = [_label_cell(gname) if i == 0 else ""] + list(cells)
            # None 자리를 가로 병합으로 처리
            c = 1
            while c < len(row):
                if row[c] is None:
                    c0 = c - 1
                    while c < len(row) and row[c] is None:
                        row[c] = ""
                        c += 1
                    styles.append(("SPAN", (c0, r), (c - 1, r)))
                else:
                    c += 1
            rows.append(row)
            r += 1
        styles.append(("SPAN", (0, start), (0, r - 1)))
    t = Table(rows, colWidths=widths, rowHeights=heights)
    styles += [
        ("GRID", (0, 0), (-1, -1), 0.6, LINE),
        ("BOX", (0, 0), (-1, -1), 0.9, LINE),
        ("BACKGROUND", (0, 0), (0, -1), LABEL_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]
    t.setStyle(TableStyle(styles))
    return t


def sec(label, content, note="", label_w=34 * mm, height=None, pad_top=4, pad_left=8):
    """좌측 회색 라벨 + 우측 내용의 구획 상자."""
    t = Table([[_label_cell(label, note), content]],
              colWidths=[label_w, W - label_w], rowHeights=height)
    t.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.9, LINE),
        ("LINEAFTER", (0, 0), (0, 0), 0.6, LINE),
        ("BACKGROUND", (0, 0), (0, 0), LABEL_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 3), ("RIGHTPADDING", (0, 0), (0, 0), 3),
        ("LEFTPADDING", (1, 0), (1, 0), pad_left), ("RIGHTPADDING", (1, 0), (1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, -1), pad_top),
        ("BOTTOMPADDING", (0, 0), (-1, -1), pad_top),
    ]))
    return t


def bullets(lines, size=9, leading=13.6, marker="· ", indent=None):
    """머리기호 안내 줄. 줄이 넘어가면 머리기호 폭만큼 들여써서 글머리를 맞춘다."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    ind = indent if indent is not None else stringWidth(marker or "· ", "Nanum", size)
    st = ParagraphStyle("bl", fontName="Nanum", fontSize=size, leading=leading,
                        textColor=INK, leftIndent=ind, firstLineIndent=-ind)
    paras = [[Paragraph(marker + x, st)] for x in lines]
    t = Table(paras, colWidths=["*"])
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def fields(rows, widths, heights, valign_top=(), size=8.8):
    """구획 안에 넣는 기입 칸 표. 행 안의 None은 왼쪽 셀과 가로 병합된다."""
    body, styles = [], []
    for r, cells in enumerate(rows):
        row = list(cells)
        c = 0
        while c < len(row):
            if row[c] is None:
                c0 = c - 1
                while c < len(row) and row[c] is None:
                    row[c] = ""
                    c += 1
                styles.append(("SPAN", (c0, r), (c - 1, r)))
            else:
                c += 1
        body.append(row)
    t = Table(body, colWidths=widths, rowHeights=heights)
    styles += [
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    for r in valign_top:
        styles.append(("VALIGN", (0, r), (-1, r), "TOP"))
        styles.append(("TOPPADDING", (0, r), (-1, r), 3))
    t.setStyle(TableStyle(styles))
    return t


def rec_table(headers, widths, n_rows, row_h=5.4 * mm, head_h=5.4 * mm, size=7.8):
    """기록용 빈 표 — 모니터링·투약 기록처럼 손으로 채우는 칸."""
    def C(t):
        return Paragraph(t, ParagraphStyle("h", fontName="NanumB", fontSize=size,
                                           leading=size + 2.4, textColor=INK,
                                           alignment=TA_CENTER))
    rows = [[C(h) for h in headers]] + [[""] * len(headers) for _ in range(n_rows)]
    t = Table(rows, colWidths=widths, rowHeights=[head_h] + [row_h] * n_rows)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LABEL_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def stack(items, width):
    """구획 안에서 여러 요소를 위아래로 쌓는다."""
    rows = [[it] for it in items]
    t = Table(rows, colWidths=[width])
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def numbered(items, size=9, leading=13.6):
    return Paragraph("<br/>".join("%d) %s" % (i, x) for i, x in enumerate(items, 1)),
                     ParagraphStyle("nb", fontName="Nanum", fontSize=size,
                                    leading=leading, textColor=INK))


ASA_ROWS = [
    ("Ⅰ", "정상적이고 건강한 개체", "0.1"),
    ("Ⅱ", "활동을 제한하지 않는 가벼운 전신적 질환", "1"),
    ("Ⅲ", "활동이 가능한 중증의 전신적 질환", "10"),
    ("Ⅳ", "지속적으로 생명을 위협하며, 활동이 불가능한 전신적 질환", "30"),
    ("Ⅴ", "수술과 관계없이 24시간 이내에 사망할 수 있는 빈사 상태", "50"),
]


def grid_list(items, total_w, cols=3, size=9, leading=14):
    """1) 2) 3) … 을 여러 열로 나눠 배치. 세로 공간을 아낀다."""
    import math
    rows_n = int(math.ceil(len(items) / float(cols)))
    cw = total_w / cols
    grid = []
    for r in range(rows_n):
        row = []
        for c in range(cols):
            i = r * cols + c
            row.append(P("%d) %s" % (i + 1, items[i]), size=size, leading=leading)
                       if i < len(items) else "")
        grid.append(row)
    t = Table(grid, colWidths=[cw] * cols)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return t


def asa_table(total_w, row_h=4.9 * mm):
    """체크 · ASA 등급 · 정의 · 사망률 표. 해당 등급에 표시할 수 있게 체크칸을 둔다."""
    def C(t, bold=False, size=8.0):
        return Paragraph(t, ParagraphStyle(
            "a", fontName="NanumB" if bold else "Nanum", fontSize=size,
            leading=size + 2.2, textColor=INK, alignment=TA_CENTER))
    w = [10 * mm, 14 * mm, total_w - 40 * mm, 16 * mm]
    rows = [[C("체크", size=7.4), C("ASA 등급", size=7.4), C("정 의", size=7.4), C("사망률(%)", size=7.4)]]
    rows += [[C("□", size=9), C(g, size=7.6), C(d, size=7.6), C(m, size=7.6)] for g, d, m in ASA_ROWS]
    t = Table(rows, colWidths=w, rowHeights=[row_h] * 6)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), LABEL_BG),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]))
    return t


def closing(text, note=""):
    body = text
    if note:
        body += '<br/><font size="8.8">' + note + "</font>"
    return Paragraph(body, ParagraphStyle(
        "cl", fontName="Nanum", fontSize=8.8, leading=12.8, textColor=INK,
        alignment=TA_CENTER))


def sign_row(roles):
    """가운데 정렬 서명줄. roles = ["보호자", "설명 수의사"]

    글자 실제 폭을 재서 열 너비를 잡는다 — 라벨이 두 줄로 꺾이면 행 높이가
    넘쳐 다음 장으로 밀리기 때문이다.
    """
    from reportlab.pdfbase.pdfmetrics import stringWidth
    note_txt = "(서명 또는 인)"
    n = len(roles)
    date_w = 56 * mm
    label_w = max(stringWidth(r, "NanumB", 9.6) for r in roles) + 10
    note_w = stringWidth(note_txt, "Nanum", 7.8) + 8
    line_w = (W - date_w - n * (label_w + note_w)) / n
    # 날짜: 20 [   ] 년 [   ] 월 [   ] 일 — 숫자를 적을 빈칸을 실제로 벌려 둔다
    unit = (date_w - stringWidth("20 년 월 일", "Nanum", 9.6) - 14 - 5 * mm) / 3
    dcells = [P("20", size=9.6), "", P("년", size=9.6), "", P("월", size=9.6), "", P("일", size=9.6), ""]
    dwidths = [7 * mm, unit, 5 * mm, unit, 5 * mm, unit, 5 * mm, 5 * mm]
    date_tbl = Table([dcells], colWidths=dwidths, rowHeights=[9 * mm])
    date_tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1), ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LINEBELOW", (1, 0), (1, 0), 0.7, colors.HexColor("#9A9A9A")),
        ("LINEBELOW", (3, 0), (3, 0), 0.7, colors.HexColor("#9A9A9A")),
        ("LINEBELOW", (5, 0), (5, 0), 0.7, colors.HexColor("#9A9A9A")),
    ]))
    cells, widths = [date_tbl], [date_w]
    for r in roles:
        cells += [P(r, size=9.6, bold=True), P("", size=9), P(note_txt, size=7.8, color=SOFT)]
        widths += [label_w, line_w, note_w]
    t = Table([cells], colWidths=widths, rowHeights=[11 * mm], hAlign="CENTER")
    style = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(n):
        c = 2 + i * 3
        # 사무국 양식과 같이 점선 상자로 서명 자리를 표시한다
        style.append(("BOX", (c, 0), (c, 0), 0.7, colors.HexColor("#9A9A9A"), None, (1.6, 1.6)))
        style.append(("TOPPADDING", (c, 0), (c, 0), 1))
        style.append(("BOTTOMPADDING", (c, 0), (c, 0), 1))
    t.setStyle(TableStyle(style))
    return t


def build(filename, title, story):
    dest = os.path.join(OUT, filename)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    d = SimpleDocTemplate(dest, pagesize=A4, topMargin=TOP, bottomMargin=BOTTOM,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          title=title, author="사단법인 한국동물병원협회")
    d.build(story, onFirstPage=page_frame, onLaterPages=page_frame)

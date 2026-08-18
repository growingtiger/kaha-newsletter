# -*- coding: utf-8 -*-
"""KAHA 회원병원 실무 소식지 제공 양식 PDF 생성.

브랜드 팔레트(공식 로고 추출): KAHA 블루 #035293, 차콜 #231916.
새 양식 추가 시 이 스크립트의 스타일 함수를 재사용해 통일성을 유지한다.
필요 패키지: reportlab, 시스템 폰트 fonts-nanum.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image as RLImage)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

FONT_DIR = "/usr/share/fonts/truetype/nanum"
pdfmetrics.registerFont(TTFont("Nanum", os.path.join(FONT_DIR, "NanumGothic.ttf")))
pdfmetrics.registerFont(TTFont("NanumB", os.path.join(FONT_DIR, "NanumGothicBold.ttf")))

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # kaha/
OUT = os.path.join(BASE, "forms")
LOGO = os.path.join(BASE, "assets", "kaha-logo.png")
LOGO_W, LOGO_H = 1197, 238
os.makedirs(OUT, exist_ok=True)

BLUE = colors.HexColor("#035293")
BLUE_DK = colors.HexColor("#023A68")
BLUE_BG = colors.HexColor("#EDF3FA")
INK = colors.HexColor("#231916")
GREY = colors.HexColor("#6B7683")
LINE = colors.HexColor("#B9CCDE")

MARGIN = 16 * mm
W = A4[0] - 2 * MARGIN

st_title = ParagraphStyle("t", fontName="NanumB", fontSize=17, leading=21, textColor=BLUE_DK)
st_sub = ParagraphStyle("sub", fontName="Nanum", fontSize=8, leading=11, textColor=GREY)
st_note = ParagraphStyle("n", fontName="Nanum", fontSize=7.6, leading=10.5, textColor=GREY)


def P(text, bold=False, size=9, color=INK, leading=None):
    return Paragraph(text, ParagraphStyle(
        "c", fontName="NanumB" if bold else "Nanum", fontSize=size,
        leading=leading or (size + 3.4), textColor=color))


def section(title):
    t = Table([[P(title, bold=True, size=9.5, color=colors.white)]],
              colWidths=[W], rowHeights=[6 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return [Spacer(1, 2 * mm), t, Spacer(1, 0.7 * mm)]


def grid(rows, widths, heights=None, label_cols=(0,), valign_top=()):
    """label_cols: 연한 파랑 배경을 칠할 열 인덱스. valign_top: 위 정렬할 행 인덱스."""
    t = Table(rows, colWidths=widths, rowHeights=heights)
    style = [
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]
    for c in label_cols:
        style.append(("BACKGROUND", (c, 0), (c, -1), BLUE_BG))
    for r in valign_top:
        style.append(("VALIGN", (0, r), (-1, r), "TOP"))
        style.append(("TOPPADDING", (0, r), (-1, r), 4))
    t.setStyle(TableStyle(style))
    return t


def header(title, subtitle, form_no):
    lh = 9.5 * mm
    logo = RLImage(LOGO, width=lh * LOGO_W / LOGO_H, height=lh)
    meta = Table([[P("서식번호", bold=True, size=7.4, color=BLUE_DK), P(form_no, size=7.4)],
                  [P("시행일자", bold=True, size=7.4, color=BLUE_DK), P("2026. 8.", size=7.4)]],
                 colWidths=[16 * mm, 24 * mm], rowHeights=[5 * mm, 5 * mm])
    meta.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("BACKGROUND", (0, 0), (0, -1), BLUE_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    top = Table([[logo, "", meta]], colWidths=[W - 60 * mm, 20 * mm, 40 * mm])
    top.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    rule = Table([[""]], colWidths=[W], rowHeights=[0.9 * mm])
    rule.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), BLUE)]))
    return [top, Spacer(1, 1.8 * mm), rule, Spacer(1, 2 * mm),
            Paragraph(title, st_title), Spacer(1, 1 * mm),
            Paragraph(subtitle, st_sub)]


def band_header(title, legal, form_no=None):
    """상단 브랜드 밴드 — 왼쪽 제목·근거법령, 오른쪽 흰 칩 안에 공식 로고.

    form_no를 주면 아래에 서식번호 띠를 붙인다(내부 관리용 양식).
    보호자에게 바로 배부하는 동의서는 생략한다.
    """
    tw = W - 62 * mm - 9 * mm
    tcell = Table([[Paragraph(title, ParagraphStyle(
                        "bt", fontName="NanumB", fontSize=17.5, leading=21, textColor=colors.white))],
                   [Spacer(1, 1.2 * mm)],
                   [Paragraph(legal, ParagraphStyle(
                        "bl", fontName="Nanum", fontSize=7.4, leading=10,
                        textColor=colors.HexColor("#C8DCEF")))]],
                  colWidths=[tw])
    tcell.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    lh = 9.2 * mm
    logo = RLImage(LOGO, width=lh * LOGO_W / LOGO_H, height=lh)
    chip = Table([[logo]], colWidths=[62 * mm], rowHeights=[16.5 * mm])
    chip.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    band = Table([[tcell, chip]], colWidths=[W - 62 * mm, 62 * mm], rowHeights=[16.5 * mm])
    band.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BLUE_DK),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, -1), 6 * mm), ("RIGHTPADDING", (0, 0), (0, -1), 3 * mm),
        ("LEFTPADDING", (1, 0), (1, -1), 0), ("RIGHTPADDING", (1, 0), (1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    if not form_no:
        return [band]
    meta = Table([[P("서식번호 " + form_no + "  ·  시행일자 2026. 8.  ·  작성 후 1년 보존",
                     size=7.4, color=colors.white)]], colWidths=[W], rowHeights=[5.4 * mm])
    meta.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BLUE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6 * mm),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return [band, meta]


def divider(text):
    """양옆에 가는 선을 둔 가운데 정렬 구분 제목."""
    st = ParagraphStyle("dv", fontName="NanumB", fontSize=11, leading=13,
                        textColor=BLUE_DK, alignment=TA_CENTER)
    t = Table([["", Paragraph(text, st), ""]],
              colWidths=[(W - 44 * mm) / 2, 44 * mm, (W - 44 * mm) / 2], rowHeights=[7 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (0, 0), 0.7, LINE),
        ("LINEBELOW", (2, 0), (2, 0), 0.7, LINE),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return [Spacer(1, 1.6 * mm), t, Spacer(1, 0.6 * mm)]


def cap(title, note=""):
    """가운데 정렬 소제목 바 — 연한 파랑 바탕 + 왼쪽 파란 강조선(KAHA 식별)."""
    body = title if not note else title + '  <font size="7.6" color="#6B7683">' + note + "</font>"
    t = Table([["", Paragraph(body, ParagraphStyle(
        "cp", fontName="NanumB", fontSize=9.4, leading=12, textColor=BLUE_DK,
        alignment=TA_CENTER))]], colWidths=[2.2 * mm, W - 2.2 * mm], rowHeights=[6 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), BLUE),
        ("BACKGROUND", (1, 0), (1, 0), BLUE_BG),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return [Spacer(1, 1.6 * mm), t, Spacer(1, 0.7 * mm)]


def footer_fn(form_no, y=12 * mm):
    def draw(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(BLUE)
        canvas.setLineWidth(0.8)
        canvas.line(MARGIN, y + 4.2 * mm, A4[0] - MARGIN, y + 4.2 * mm)
        canvas.setFont("Nanum", 7)
        canvas.setFillColor(GREY)
        canvas.drawString(MARGIN, y, "사단법인 한국동물병원협회 · 회원병원 실무 소식지 제공 양식 — 병원 실정에 맞게 수정 후 사용하십시오.")
        canvas.drawRightString(A4[0] - MARGIN, y, form_no)
        canvas.restoreState()
    return draw


def build(filename, form_no, title, story, top=12 * mm, bottom=18 * mm, footer=True):
    d = SimpleDocTemplate(os.path.join(OUT, filename), pagesize=A4,
                          topMargin=top, bottomMargin=bottom,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          title=title, author="사단법인 한국동물병원협회",
                          subject="KAHA 회원병원 실무 소식지 제공 양식")
    if footer:
        fn = footer_fn(form_no, y=bottom - 6 * mm)
        d.build(story, onFirstPage=fn, onLaterPages=fn)
    else:
        d.build(story)


# ═══════════════════════════════════════════════════════════════════
# 1. 수술·마취 동의서  (KAHA-F-2601)
# ═══════════════════════════════════════════════════════════════════
s = band_header("수술등중대진료(마취) 동의서",
                "수의사법 제13조의2 및 같은 법 시행규칙 제13조의3에 따른 설명 · 서면동의")

# ── 인적사항: 보호자 · 반려동물 · 수의사 3구획 (좌측 라벨 병합) ──
LC, KC = 20 * mm, 24 * mm
VC = (W - LC - KC * 2) / 2
info = [
    [P("보호자", bold=True, size=9.5, color=BLUE_DK), P("성 명"), "", P("생년월일"), ""],
    ["", P("연 락 처"), "", P("동물과의 관계"), P("□ 소유자     □ 대리인", size=8.6)],
    ["", P("주 소"), "", "", ""],
    [P("반려동물", bold=True, size=9.5, color=BLUE_DK), P("이 름"), "", P("종 / 품종"), ""],
    ["", P("성별 / 중성화"), "", P("연령 / 체중"), ""],
    ["", P("특이사항"), "", "", ""],
    [P("수의사", bold=True, size=9.5, color=BLUE_DK), P("동물병원명"), "", P("면허번호"), ""],
    ["", P("성 명"), "", "", P("(서명 또는 인)", size=8.4, color=GREY)],
]
it = Table(info, colWidths=[LC, KC, VC, KC, VC], rowHeights=[7.6 * mm] * 8)
it.setStyle(TableStyle([
    ("GRID", (1, 0), (-1, -1), 0.5, LINE),
    ("BOX", (0, 0), (-1, -1), 0.5, LINE),
    ("SPAN", (0, 0), (0, 2)), ("SPAN", (0, 3), (0, 5)), ("SPAN", (0, 6), (0, 7)),
    ("SPAN", (2, 2), (4, 2)), ("SPAN", (2, 5), (4, 5)), ("SPAN", (2, 7), (3, 7)),
    ("LINEBELOW", (0, 2), (-1, 2), 0.9, BLUE),
    ("LINEBELOW", (0, 5), (-1, 5), 0.9, BLUE),
    ("BACKGROUND", (0, 0), (0, -1), BLUE_BG),
    ("BACKGROUND", (1, 0), (1, -1), BLUE_BG),
    ("BACKGROUND", (3, 0), (3, -1), BLUE_BG),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (0, -1), "CENTER"),
    ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
]))
s.append(Spacer(1, 2 * mm))
s.append(it)

s += divider("설명 및 동의 사항")

# ── 1. 필요성 · 방법 및 내용 ──
s += cap("수술등중대진료의 필요성, 방법 및 내용")
s.append(grid([
    [P("진단명 (추정 포함)"), "", P("예정 일시"), ""],
    [P("수술 / 처치명"), "", P("마취 방식"), ""],
], [30 * mm, W / 2 - 30 * mm, 26 * mm, W / 2 - 26 * mm], heights=[7.6 * mm] * 2, label_cols=(0, 2)))
s.append(grid([
    [P("필요성 · 현재 상태"), ""],
    [P("방법 및 내용"), ""],
], [30 * mm, W - 30 * mm], heights=[11 * mm, 11 * mm], valign_top=(0, 1)))

# ── 2. 후유증 · 부작용 + ASA 등급 ──
s += cap("수술등중대진료에 따라 전형적으로 발생이 예상되는 후유증 또는 부작용")
risk_items = [
    "1)  저혈압 · 저체온 · 고체온", "2)  약물 과민반응에 의한 쇼크",
    "3)  순환부전에 의한 쇼크", "4)  췌장염 · 신부전 및 폐수종",
    "5)  기저질환 발현 및 현증 악화", "6)  삽관에 의한 일시적 기침",
    "7)  출혈 · 감염 · 봉합 부위 벌어짐", "8)  드물게 심정지 및 사망",
]
rt = Table([[P(risk_items[i], size=8.4) for i in range(0, 4)],
            [P(risk_items[i], size=8.4) for i in range(4, 8)]],
           colWidths=[W / 4] * 4, rowHeights=[5.6 * mm] * 2)
rt.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
    ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
]))
s.append(rt)
s.append(Spacer(1, 1 * mm))

ASA_W = [16 * mm, 20 * mm, W - 66 * mm, 30 * mm]
ac = ParagraphStyle("ac", fontName="Nanum", fontSize=8.2, leading=10.4, alignment=TA_CENTER,
                    textColor=INK)
ah = ParagraphStyle("ah", fontName="NanumB", fontSize=8.6, leading=11, alignment=TA_CENTER,
                    textColor=BLUE_DK)


def AC(t, bold=False, color=INK):
    st = ParagraphStyle("x", parent=ah if bold else ac, textColor=color)
    return Paragraph(t, st)


asa_rows = [
    [AC("체크", bold=True), AC("ASA 등급", bold=True), AC("정 의", bold=True),
     AC("사망률(%)", bold=True)],
    [AC("□"), AC("Ⅰ"), AC("정상적이고 건강한 개체"), AC("0.1")],
    [AC("□"), AC("Ⅱ"), AC("활동을 제한하지 않는 가벼운 전신질환"), AC("1")],
    [AC("□"), AC("Ⅲ"), AC("활동이 가능한 중증의 전신질환"), AC("10")],
    [AC("□"), AC("Ⅳ"), AC("지속적으로 생명을 위협하며 활동이 불가능한 전신질환"), AC("30")],
    [AC("□"), AC("Ⅴ"), AC("수술과 관계없이 24시간 이내에 사망할 수 있는 빈사 상태"), AC("50")],
]
at = Table(asa_rows, colWidths=ASA_W, rowHeights=[6.3 * mm] * 6)
at.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), BLUE_BG),
    ("LINEABOVE", (0, 0), (-1, 0), 0.9, BLUE),
    ("LINEBELOW", (0, 0), (-1, 0), 0.9, BLUE),
    ("LINEBELOW", (0, -1), (-1, -1), 0.9, BLUE),
    ("INNERGRID", (0, 1), (-1, -1), 0.4, LINE),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
]))
s.append(at)

# ── 3. 보호자 준수·숙지 사항 및 추가 확인 ──
s += cap("수술등중대진료 전후에 보호자가 준수 및 숙지하여야 할 사항", "— 해당 항목에 표시하여 주십시오")
s.append(grid([
    [P("□  마취 시 수술 전 일정 시간의 금식과 금수가 필요합니다.  ( 음식 ______ 시간 · 물 ______ 시간 )", size=8.6)],
    [P("□  마취를 시행함에 있어 발생할 수 있는 부작용 · 합병증 또는 후유증에 대한 설명을 충분히 듣고 이해하였습니다.", size=8.6)],
    [P("□  마취 과정에 있어 불가항력적이거나 환자의 특이체질로 인한 우발사고의 가능성을 인정합니다.", size=8.6)],
    [P("□  수술 후 주의사항(넥카라 · 활동 제한 · 투약 등)을 준수하고, 응급상황에 연락 가능한 연락처를 유지합니다.", size=8.6)],
], [W], heights=[6.7 * mm] * 4, label_cols=()))
s.append(grid([
    [P("□  심폐소생술(CPR) :  □ 시행 원함   □ 원하지 않음(DNR)", size=8.6),
     P("□  마취 및 수술비 설명을 들었음  ( 예상 : __________ 원 )", size=8.6)],
    [P("□  수술 중 상태에 따라 범위가 변경될 수 있음을 설명받음", size=8.6),
     P("변경 시 :  □ 사전 연락 요망   □ 수의사 판단에 위임", size=8.6)],
], [W / 2, W / 2], heights=[6.7 * mm] * 2, label_cols=()))

# ── 동의문 · 서명 ──
s.append(Spacer(1, 1.4 * mm))
agree = Table([[Paragraph(
    "「수의사법」 제13조의2 및 같은 법 시행규칙 제13조의3에 따라 위와 같이 수의사로부터 수술등중대진료에 관한 설명을 들었으며, "
    "그 필요성 · 방법 · 내용과 전형적으로 예상되는 후유증 및 부작용을 충분히 이해하였습니다. 이에 위 수술등중대진료 및 마취의 시행에 동의하며, "
    "관련한 수의학적 처치를 담당 수의사에게 위임합니다.",
    ParagraphStyle("ag", fontName="Nanum", fontSize=8.4, leading=12, textColor=INK))]],
    colWidths=[W])
agree.setStyle(TableStyle([
    ("BOX", (0, 0), (-1, -1), 0.9, BLUE),
    ("BACKGROUND", (0, 0), (-1, -1), BLUE_BG),
    ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
    ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
]))
s.append(agree)
s.append(Spacer(1, 1.4 * mm))
s.append(grid([
    [P("작성일", size=8.6), P("20____년  ____월  ____일", size=8.6),
     P("보호자", size=8.6), P("성명 : __________ (서명 또는 인)", size=8.6),
     P("설명 수의사", size=8.6), P("성명 : __________ (서명 또는 인)", size=8.6)],
], [13 * mm, 38 * mm, 13 * mm, 47 * mm, 20 * mm, W - 131 * mm],
    heights=[11 * mm], label_cols=(0, 2, 4)))

build("surgery-anesthesia-consent.pdf", "KAHA-F-2601", "수술등중대진료(마취) 동의서", s,
      top=10 * mm, bottom=10 * mm, footer=False)

# ═══════════════════════════════════════════════════════════════════
# 2. 마취 전 평가·모니터링 체크리스트  (KAHA-F-2602)
# ═══════════════════════════════════════════════════════════════════
s = header("마취 전 평가 · 모니터링 체크리스트",
           "2020 AAHA Anesthesia and Monitoring Guidelines for Dogs and Cats 기반 (aaha.org 전문 무료 공개)",
           "KAHA-F-2602")

s += section("환자 정보")
s.append(grid([
    [P("동물명 / 차트번호"), "", P("종 / 품종"), "", P("체중(kg)"), ""],
], [32 * mm, 34 * mm, 24 * mm, 34 * mm, 20 * mm, W - 144 * mm],
    heights=[8 * mm], label_cols=(0, 2, 4)))
s.append(grid([
    [P("병력 · 현재 투약"), ""],
    [P("신체검사 요약"), ""],
], [32 * mm, W - 32 * mm], heights=[9.5 * mm, 9.5 * mm], valign_top=(0, 1)))
s.append(grid([
    [P("사전 혈액검사"), P("□ CBC     □ 혈액화학     □ 전해질     □ 응고계     □ 기타 : ")],
    [P("ASA 분류"), P("□ Ⅰ 건강    □ Ⅱ 경미한 전신질환    □ Ⅲ 중등도 전신질환    □ Ⅳ 생명 위협    □ Ⅴ 위중    □ E 응급")],
], [32 * mm, W - 32 * mm], heights=[8 * mm, 8 * mm]))

s += section("마취 전 준비")
s.append(grid([
    [P("□  금식 확인 — 음식 ______ 시간 · 물 ______ 시간   (병원 프로토콜 · AAHA 금식 권고표 참고)")],
    [P("□  IV 카테터 장착      □  기관튜브 3종 준비 ( ____ / ____ / ____ )      □  응급약물 용량 사전 계산 · 비치")],
    [P("□  마취 회로 · 산소 · 흡인기 점검      □  항불안 처치 필요 여부 평가 (겁 많음 · 공격성)")],
    [P("□  보호자 설명 및 동의서 작성 완료 (서식 KAHA-F-2601)")],
], [W], heights=[7.4 * mm] * 4, label_cols=()))

s += section("마취 중 모니터링 기록  (15분 간격 권장)")
head = [P(x, bold=True, size=8.6, color=BLUE_DK) for x in
        ["시각", "HR", "RR", "SpO₂", "EtCO₂", "혈압", "체온", "마취심도 · 처치 · 비고"]]
mon_rows = [head] + [[""] * 8 for _ in range(10)]
mt = Table(mon_rows,
           colWidths=[18 * mm, 15 * mm, 15 * mm, 17 * mm, 17 * mm, 21 * mm, 17 * mm, W - 120 * mm],
           rowHeights=[7 * mm] + [7.3 * mm] * 10)
mt.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, LINE),
    ("BACKGROUND", (0, 0), (-1, 0), BLUE_BG),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
]))
s.append(mt)
s.append(Spacer(1, 1.2 * mm))
s.append(Paragraph("※ 저체온과 저혈압은 가장 흔한 마취 중 합병증입니다. 조기 인지와 가온 · 수액 대응 프로토콜을 준비하십시오.", st_note))

s += section("회복기 관리  (마취 관련 사망 위험이 높은 구간 — 담당자 지정)")
s.append(grid([
    [P("□  발관 시각 : ________       □  체온 회복 확인 ( ________ ℃ )       □  통증 평가 ( 도구 / 점수 : ____________ )")],
    [P("□  의식 · 기립 확인       □  퇴원 전 보호자 주의사항 전달")],
], [W], heights=[7.6 * mm, 7.6 * mm], label_cols=()))
s.append(Spacer(1, 3 * mm))
s.append(grid([
    [P("마취 담당"), P("성명 : __________ (서명)"),
     P("회복기 담당"), P("성명 : __________ (서명)")],
], [20 * mm, 69 * mm, 22 * mm, W - 111 * mm], heights=[11 * mm], label_cols=(0, 2)))

build("pre-anesthesia-checklist.pdf", "KAHA-F-2602", "마취 전 평가·모니터링 체크리스트", s)

# ═══════════════════════════════════════════════════════════════════
# 3. 영양 평가·BCS/MCS 기록지  (KAHA-F-2603)
# ═══════════════════════════════════════════════════════════════════
s = header("영양 평가 · BCS / MCS 기록지",
           "WSAVA 영양 평가 가이드라인(2011, JSAP) · 글로벌 영양 툴킷 기반 — 모든 환자, 모든 내원 시 스크리닝",
           "KAHA-F-2603")

s += section("환자 정보")
s.append(grid([
    [P("동물명 / 차트번호"), "", P("종 / 품종"), "", P("연령"), "", P("중성화"), P("□ 예  □ 아니오")],
], [30 * mm, 28 * mm, 20 * mm, 26 * mm, 12 * mm, 16 * mm, 14 * mm, W - 146 * mm],
    heights=[9 * mm], label_cols=(0, 2, 4, 6)))

s += section("1. 식이 이력")
s.append(grid([
    [P("주식 (제품명 · 형태)"), "", P("1일 급여량 / 횟수"), ""],
    [P("간식 · 사람 음식"), "", P("영양제 · 보조제"), ""],
    [P("식욕 변화"), P("□ 없음  □ 증가  □ 감소 (기간: ______)", size=8.6),
     P("음수량 변화"), P("□ 없음  □ 증가  □ 감소", size=8.6)],
], [32 * mm, 62 * mm, 30 * mm, W - 124 * mm], heights=[9.5 * mm] * 3, label_cols=(0, 2)))

s += section("2. 체중 및 신체 평가")
s.append(grid([
    [P("금일 체중(kg)"), "", P("직전 체중 / 측정일"), "", P("변화율(%)"), ""],
], [28 * mm, 30 * mm, 34 * mm, 40 * mm, 22 * mm, W - 154 * mm],
    heights=[9 * mm], label_cols=(0, 2, 4)))
s.append(Spacer(1, 1.5 * mm))
bcs = [[P("BCS (9점)", bold=True, size=8.6, color=BLUE_DK)] +
       [P("□ %d" % i, size=8.6) for i in range(1, 10)]]
bt = Table(bcs, colWidths=[26 * mm] + [(W - 26 * mm) / 9] * 9, rowHeights=[9 * mm])
bt.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, LINE),
    ("BACKGROUND", (0, 0), (0, -1), BLUE_BG),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (1, 0), (-1, -1), "CENTER"),
]))
s.append(bt)
s.append(Spacer(1, 1 * mm))
s.append(Paragraph("1–3 저체중 · 4–5 이상적 · 6–7 과체중 · 8–9 비만  (갈비뼈 촉진, 허리 라인, 복부 턱업으로 판정)", st_note))
s.append(Spacer(1, 1.5 * mm))
s.append(grid([
    [P("MCS (근육상태)"), P("□ 정상      □ 경도 소실      □ 중등도 소실      □ 중증 소실")],
], [30 * mm, W - 30 * mm], heights=[9 * mm]))
s.append(Spacer(1, 1 * mm))
s.append(Paragraph("척추 · 견갑 · 측두부 · 골반 촉진으로 판정 — 비만 개체도 근소실이 동반될 수 있습니다 (특히 고령 · 만성질환).", st_note))

s += section("3. 위험요인 스크리닝  (하나라도 해당 시 확장 평가)")
s.append(grid([
    [P("□ 질병(만성 포함)     □ 고령     □ 비만 / 저체중     □ 수제식 · 생식 · 비전형 식이     □ 피모 · 치아 이상     □ 체중 급변")],
], [W], heights=[9.5 * mm], label_cols=()))

s += section("4. 평가 결과 및 계획")
s.append(grid([
    [P("확장 평가 필요"), P("□ 불필요       □ 필요  ( 사유 : ________________________________________ )")],
    [P("권장 사료 · 급여량"), ""],
    [P("목표 체중 · 재평가 일정"), ""],
    [P("보호자 상담 내용"), ""],
], [38 * mm, W - 38 * mm],
    heights=[9 * mm, 20 * mm, 20 * mm, 36 * mm], valign_top=(1, 2, 3)))
s.append(Spacer(1, 3 * mm))
s.append(grid([
    [P("평가일"), P("20____년  ____월  ____일"),
     P("평가자"), P("성명 : __________ (서명)")],
], [16 * mm, 44 * mm, 16 * mm, W - 76 * mm], heights=[10.5 * mm], label_cols=(0, 2)))

build("nutrition-assessment-chart.pdf", "KAHA-F-2603", "영양 평가·BCS/MCS 기록지", s)

# ═══════════════════════════════════════════════════════════════════
# 4. 입원 동의서  (KAHA-F-2604)
# ═══════════════════════════════════════════════════════════════════
s = header("입원 동의서",
           "입원 진료에 관한 설명·비용·연락 방식 합의서 — 본 서식은 수의사법 제13조의2의 수술등중대진료 동의서가 아닙니다.",
           "KAHA-F-2604")

s += section("동물 · 보호자 정보")
s.append(grid([
    [P("동 물 명"), "", P("보호자 성명"), ""],
    [P("종 / 품종"), "", P("연 락 처"), ""],
    [P("성별 / 중성화"), "", P("제2연락처"), ""],
], [30 * mm, 60 * mm, 28 * mm, W - 118 * mm],
    heights=[8 * mm] * 3, label_cols=(0, 2)))
s.append(grid([
    [P("연령"), "", P("체중(kg)"), "", P("차트번호"), "", P("관계"), P("□ 소유자&nbsp;&nbsp;&nbsp; □ 대리인", size=8.4)],
], [16 * mm, 22 * mm, 20 * mm, 20 * mm, 20 * mm, 24 * mm, 14 * mm, W - 136 * mm],
    heights=[8 * mm], label_cols=(0, 2, 4, 6)))

s += section("1. 입원 사유 및 예상 기간")
s.append(grid([
    [P("추정 진단명"), "", P("입원 목적"), ""],
], [26 * mm, 62 * mm, 24 * mm, W - 112 * mm], heights=[8.4 * mm], label_cols=(0, 2)))
s.append(grid([
    [P("예상 입원 기간"), P("약 ______ 일        ( 20____. ____. ____.  ～  20____. ____. ____. )")],
], [30 * mm, W - 30 * mm], heights=[8.4 * mm]))

s += section("2. 비용 안내   ※ 1일 입원비는 병원 게시 금액과 동일해야 합니다")
s.append(grid([
    [P("1일 입원비"), P("____________ 원"), P("예상 총액"), P("____________ 원 (변동 가능)")],
], [26 * mm, 42 * mm, 26 * mm, W - 94 * mm], heights=[8.4 * mm], label_cols=(0, 2)))
s.append(grid([
    [P("입원비 포함 항목"), ""],
    [P("별도 청구 항목"), P("□ 검사&nbsp;&nbsp;&nbsp;&nbsp; □ 처치&nbsp;&nbsp;&nbsp;&nbsp; □ 약제&nbsp;&nbsp;&nbsp;&nbsp; □ 수혈&nbsp;&nbsp;&nbsp;&nbsp; □ 기타 : ")],
], [30 * mm, W - 30 * mm], heights=[9 * mm, 8.4 * mm]))
s.append(grid([
    [P("□&nbsp; 예상액의 ______ % 또는 ____________ 원을 초과할 것으로 예상되면 진행 전에 보호자에게 연락합니다.")],
], [W], heights=[7.8 * mm], label_cols=()))

s += section("3. 경과 보고 및 연락")
s.append(grid([
    [P("정기 보고"), P("□ 1일 1회&nbsp;&nbsp;&nbsp; □ 1일 2회&nbsp;&nbsp;&nbsp; □ 기타", size=8.4),
     P("보고 방법"), P("□ 전화&nbsp;&nbsp; □ 문자·메신저&nbsp;&nbsp; □ 면회 시 구두", size=8.4)],
], [24 * mm, 54 * mm, 24 * mm, W - 102 * mm], heights=[8 * mm], label_cols=(0, 2)))
s.append(grid([
    [P("□&nbsp; 상태 급변 시 즉시 연락&nbsp;&nbsp;&nbsp;／&nbsp;&nbsp;&nbsp;연락 불통 시 : &nbsp;□ 수의사 판단으로 필요한 처치 시행&nbsp;&nbsp;&nbsp; □ 응급처치만 시행 후 재시도")],
], [W], heights=[7.6 * mm], label_cols=()))

s += section("4. 면회 · 반입물품 · 야간 관리")
s.append(grid([
    [P("면회 가능 시간"), "", P("면회 제한 사유"), P("□ 감염&nbsp;&nbsp; □ 중환자&nbsp;&nbsp; □ 기타", size=8.4)],
], [28 * mm, 46 * mm, 28 * mm, W - 102 * mm], heights=[8.4 * mm], label_cols=(0, 2)))
s.append(grid([
    [P("반입물품"), P("(사료 · 약 · 담요 등 :                                            )  ※ 분실 시 병원이 책임지지 않을 수 있습니다.", size=8.4)],
], [24 * mm, W - 24 * mm], heights=[8.4 * mm]))
s.append(grid([
    [P("야간·휴일 관리"), P("□ 야간 수의사 상주&nbsp;&nbsp; □ 야간 간호인력 상주&nbsp;&nbsp; □ 야간 무인 관리 ( ____시 최종 처치 → ____시 확인 )", size=8.4)],
], [28 * mm, W - 28 * mm], heights=[8.4 * mm]))

s += section("5. 응급 상황 및 사망 시 처리")
s.append(grid([
    [P("□&nbsp; 심정지 시 심폐소생술(CPR) : &nbsp;□ 시행&nbsp;&nbsp; □ 시행하지 않음(DNR)&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; □&nbsp; 생명 유지에 필요한 응급처치는 연락 전 시행에 동의")],
    [P("□&nbsp; 사망 시 : &nbsp;□ 사체 인도 희망&nbsp;&nbsp; □ 병원 위탁 처리&nbsp;&nbsp; □ 동물장묘업 등록 시설 이용 안내 희망")],
], [W], heights=[8 * mm, 8 * mm], label_cols=()))

s += section("6. 입원 중 중대진료가 필요해지는 경우")
s.append(grid([
    [P("전신마취를 동반하는 내부장기 · 뼈 · 관절 수술 또는 전신마취를 동반하는 수혈이 필요해지면, 수의사법 제13조의2에 따라 "
       "<b>별도의 수술등중대진료 동의서</b>(서식 KAHA-F-2601)를 작성합니다. 본 입원 동의서가 이를 대신하지 않습니다.", size=8.6)],
], [W], heights=[11.5 * mm], label_cols=(), valign_top=(0,)))

s.append(Spacer(1, 1.8 * mm))
agree = Table([[P("본인은 위 내용에 대하여 설명을 듣고 이해하였으며, 입원 및 위 조건에 동의합니다.",
                  bold=True, size=9.5)]], colWidths=[W], rowHeights=[8 * mm])
agree.setStyle(TableStyle([
    ("BOX", (0, 0), (-1, -1), 1, BLUE),
    ("BACKGROUND", (0, 0), (-1, -1), BLUE_BG),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 7),
]))
s.append(agree)
s.append(Spacer(1, 1.5 * mm))
s.append(grid([
    [P("작성일"), P("20____년  ____월  ____일"),
     P("보호자"), P("성명 : __________ (서명)"),
     P("설명 수의사"), P("성명 : __________ (서명)")],
], [14 * mm, 42 * mm, 14 * mm, 44 * mm, 20 * mm, W - 134 * mm],
    heights=[10 * mm], label_cols=(0, 2, 4)))

build("hospitalization-consent.pdf", "KAHA-F-2604", "입원 동의서", s)

# ═══════════════════════════════════════════════════════════════════
# 5. 퇴원 안내문  (KAHA-F-2605)
# ═══════════════════════════════════════════════════════════════════
s = header("퇴원 안내문",
           "가정 투약 · 관리 · 재진 안내 — 2020 AAHA 마취·모니터링 가이드라인의 서면 지침 권고를 참고한 참고용 서식 (처방전이 아닙니다)",
           "KAHA-F-2605")

s += section("환자 정보")
s.append(grid([
    [P("동 물 명"), "", P("보호자 성명"), "", P("체중(kg)"), ""],
    [P("차트번호"), "", P("담당 수의사"), "", P("퇴원 일시"), ""],
], [24 * mm, 34 * mm, 26 * mm, 34 * mm, 22 * mm, W - 140 * mm],
    heights=[7.6 * mm] * 2, label_cols=(0, 2, 4)))
s.append(grid([
    [P("진단명 / 시행한 처치"), ""],
], [34 * mm, W - 34 * mm], heights=[8 * mm]))
s.append(grid([
    [P("퇴원 시점 상태 확인"), P("□ 각성&nbsp;&nbsp; □ 반응 있음&nbsp;&nbsp; □ 체온 회복&nbsp;&nbsp; □ 통증 조절됨&nbsp;&nbsp;&nbsp;&nbsp; (마취 시행 : □ 예&nbsp;&nbsp; □ 아니오)", size=8.4)],
], [34 * mm, W - 34 * mm], heights=[7.8 * mm]))

s += section("1. 가정 투약 안내   ※ 원내 조제·투약분입니다. 처방전이 필요하시면 별도로 요청해 주십시오.")
med_head = [P(x, bold=True, size=8.2, color=BLUE_DK) for x in
            ["약품명", "무엇 때문에", "1회 용량", "경로", "1일 횟수", "종료일", "식전/식후", "주의할 점"]]
med_w = [24 * mm, 26 * mm, 18 * mm, 13 * mm, 16 * mm, 18 * mm, 17 * mm, W - 132 * mm]
med_rows = [med_head] + [[""] * 8 for _ in range(3)]
mt = Table(med_rows, colWidths=med_w, rowHeights=[6.6 * mm] + [7.4 * mm] * 3)
mt.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, LINE),
    ("BACKGROUND", (0, 0), (-1, 0), BLUE_BG),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
]))
s.append(mt)
s.append(Spacer(1, 1 * mm))
s.append(grid([
    [P("□&nbsp; 퇴원 전 경구약 투여 방법을 보호자가 직접 해보고 확인하였습니다.&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; □&nbsp; 약 보관 방법을 안내하였습니다.")],
], [W], heights=[7.2 * mm], label_cols=()))

s += section("2. 투약 체크 달력   (투여 후 표시하세요)")
day_head = [P("", size=8)] + [P("%d일차" % i, bold=True, size=8, color=BLUE_DK) for i in range(1, 8)]
cw = [18 * mm] + [(W - 18 * mm) / 7] * 7
cal = [day_head,
       [P("아침", bold=True, size=8.4, color=BLUE_DK)] + [""] * 7,
       [P("저녁", bold=True, size=8.4, color=BLUE_DK)] + [""] * 7]
ct = Table(cal, colWidths=cw, rowHeights=[6.4 * mm, 7.4 * mm, 7.4 * mm])
ct.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, LINE),
    ("BACKGROUND", (0, 0), (-1, 0), BLUE_BG),
    ("BACKGROUND", (0, 1), (0, -1), BLUE_BG),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
]))
s.append(ct)

s += section("3. 가정 관리   (담당 수의사가 환자에 맞게 기입합니다)")
s.append(grid([
    [P("활동 제한"), P("□ 산책 제한&nbsp;&nbsp; □ 계단·점프 금지&nbsp;&nbsp; □ 목줄 산책만&nbsp;&nbsp;&nbsp;&nbsp; 기간 : ________")],
    [P("넥카라 · 수술복"), P("□ 착용 필요&nbsp;&nbsp;&nbsp;&nbsp; 착용 기간 : ________&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; □ 해당 없음")],
    [P("절개 부위 관리"), P("□ 물 닿지 않게&nbsp;&nbsp; □ 소독 : ______________&nbsp;&nbsp;&nbsp;&nbsp; 목욕 가능 시점 : ________")],
    [P("식이 · 급수"), ""],
    [P("관찰 사항"), P("배뇨 · 배변 · 식욕 · 활력 변화 시 기록해 주세요.", size=8.4)],
], [30 * mm, W - 30 * mm], heights=[7 * mm, 7 * mm, 7 * mm, 7.4 * mm, 7 * mm]))

s += section("4. 재진 및 응급 연락")
s.append(grid([
    [P("다음 내원일"), P("20____.&nbsp;____.&nbsp;____.&nbsp;&nbsp;____시"), P("재진 목적"), P("□ 경과 확인&nbsp;&nbsp; □ 봉합사 제거&nbsp;&nbsp; □ 재검사", size=8.4)],
], [26 * mm, 54 * mm, 24 * mm, W - 104 * mm], heights=[7.8 * mm], label_cols=(0, 2)))
s.append(grid([
    [P("아래 증상이 보이면 즉시 연락 주십시오 (담당 수의사 기입) :")],
    [P(" ")],
], [W], heights=[6.4 * mm, 8 * mm], label_cols=(), valign_top=(1,)))
s.append(grid([
    [P("병원 연락처"), "", P("야간 · 휴일"), ""],
], [26 * mm, 48 * mm, 26 * mm, W - 100 * mm], heights=[7.8 * mm], label_cols=(0, 2)))
s.append(Paragraph("※ 마취 후에는 회복기에 상태가 변할 수 있습니다. 퇴원 후 몇 시간 동안 특히 주의 깊게 지켜봐 주십시오.", st_note))

s.append(Spacer(1, 1.5 * mm))
s.append(grid([
    [P("□&nbsp; 위 내용을 안내문과 함께 읽으며 설명하였고, 보호자가 이해하였음을 확인합니다.")],
], [W], heights=[7.4 * mm], label_cols=()))
s.append(Spacer(1, 1.2 * mm))
s.append(grid([
    [P("설명일"), P("20____년&nbsp;____월&nbsp;____일"),
     P("보호자"), P("성명 : __________ (서명)"),
     P("설명자"), P("성명 : __________ (서명)")],
], [16 * mm, 46 * mm, 16 * mm, 44 * mm, 16 * mm, W - 138 * mm],
    heights=[9 * mm], label_cols=(0, 2, 4)))

build("discharge-instructions.pdf", "KAHA-F-2605", "퇴원 안내문", s)

print("생성 완료")
for f in sorted(os.listdir(OUT)):
    print(" -", f, os.path.getsize(os.path.join(OUT, f)), "bytes")

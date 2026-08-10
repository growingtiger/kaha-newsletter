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
    return [Spacer(1, 2.4 * mm), t, Spacer(1, 0.9 * mm)]


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
    return [top, Spacer(1, 2 * mm), rule, Spacer(1, 2.5 * mm),
            Paragraph(title, st_title), Spacer(1, 1 * mm),
            Paragraph(subtitle, st_sub)]


def footer_fn(form_no):
    def draw(canvas, doc):
        canvas.saveState()
        y = 12 * mm
        canvas.setStrokeColor(BLUE)
        canvas.setLineWidth(0.8)
        canvas.line(MARGIN, y + 4.2 * mm, A4[0] - MARGIN, y + 4.2 * mm)
        canvas.setFont("Nanum", 7)
        canvas.setFillColor(GREY)
        canvas.drawString(MARGIN, y, "사단법인 한국동물병원협회 · 회원병원 실무 소식지 제공 양식 — 병원 실정에 맞게 수정 후 사용하십시오.")
        canvas.drawRightString(A4[0] - MARGIN, y, form_no)
        canvas.restoreState()
    return draw


def build(filename, form_no, title, story):
    d = SimpleDocTemplate(os.path.join(OUT, filename), pagesize=A4,
                          topMargin=12 * mm, bottomMargin=18 * mm,
                          leftMargin=MARGIN, rightMargin=MARGIN,
                          title=title, author="사단법인 한국동물병원협회",
                          subject="KAHA 회원병원 실무 소식지 제공 양식")
    fn = footer_fn(form_no)
    d.build(story, onFirstPage=fn, onLaterPages=fn)


# ═══════════════════════════════════════════════════════════════════
# 1. 수술·마취 동의서  (KAHA-F-2601)
# ═══════════════════════════════════════════════════════════════════
s = header("수술·마취 동의서",
           "수의사법 제13조의2(수술등중대진료 설명·서면동의)에 따른 동의서 — 전신마취 동반 내부장기·뼈·관절 수술 및 수혈 / 작성 후 1년 보존",
           "KAHA-F-2601")

s += section("동물·보호자 정보")
s.append(grid([
    [P("동 물 명"), "", P("보호자 성명"), ""],
    [P("종 / 품종"), "", P("연 락 처"), ""],
    [P("성별 / 중성화"), "", P("동물과의 관계"), P("□ 소유자        □ 대리인")],
], [30 * mm, 60 * mm, 30 * mm, W - 120 * mm],
    heights=[7.5 * mm] * 3, label_cols=(0, 2)))
s.append(grid([
    [P("연령(생년월일)"), "", P("체중(kg)"), "", P("차트번호"), ""],
], [30 * mm, 34 * mm, 22 * mm, 24 * mm, 22 * mm, W - 132 * mm],
    heights=[7.5 * mm], label_cols=(0, 2, 4)))

s += section("1. 진단명 및 현재 상태")
s.append(grid([
    [P("진단명 (추정 포함)"), ""],
    [P("현재 상태 요약"), ""],
    [P("ASA 신체상태 분류"), P("□ Ⅰ 건강    □ Ⅱ 경미한 전신질환    □ Ⅲ 중등도 전신질환    □ Ⅳ 생명 위협    □ Ⅴ 위중    □ E 응급")],
], [34 * mm, W - 34 * mm], heights=[8 * mm, 9.5 * mm, 7.5 * mm], valign_top=(1,)))

s += section("2. 예정 진료의 필요성 · 방법 · 내용")
s.append(grid([
    [P("수술 / 처치명"), "", P("예정 일시"), ""],
    [P("집도 수의사"), "", P("마취 방식"), ""],
], [34 * mm, 66 * mm, 26 * mm, W - 126 * mm], heights=[7.8 * mm] * 2, label_cols=(0, 2)))
s.append(grid([
    [P("필 요 성"), ""],
    [P("방법 및 내용"), ""],
], [34 * mm, W - 34 * mm], heights=[8.5 * mm, 11 * mm], valign_top=(0, 1)))

s += section("3. 전형적으로 발생이 예상되는 후유증 · 부작용")
s.append(grid([
    [P("□  마취 관련 : 저혈압, 저체온, 부정맥, 드물게 심정지 등")],
    [P("□  수술 관련 : 출혈, 감염, 봉합 부위 벌어짐, 재수술 가능성 등")],
    [P("□  개체 상태에 따른 추가 위험 :")],
    [P("※  위 내용은 전형적으로 예상되는 사항이며, 예측하지 못한 상황이 발생할 수 있음을 설명받았습니다.", size=8.4, color=GREY)],
], [W], heights=[7 * mm, 7 * mm, 8 * mm, 7 * mm], label_cols=()))

s += section("4. 보호자 준수사항")
s.append(grid([
    [P("□  수술 전 금식 : 음식 ________ 시간  ·  물 ________ 시간")],
    [P("□  수술 후 주의사항(넥카라 · 활동 제한 · 투약 등) 준수     □  응급상황 연락 가능한 연락처 유지")],
], [W], heights=[7 * mm, 7 * mm], label_cols=()))

s += section("5. 추가 확인")
s.append(grid([
    [P("□  수술 중 상태에 따라 범위가 변경될 수 있음을 설명받음   ( 변경 시 :  □ 사전 연락 요망   □ 수의사 판단에 위임 )")],
    [P("□  예상 진료비용 안내를 받음   ( 예상 범위 : ____________________ 원 )")],
    [P("□  심폐소생술(CPR) :  □ 시행   □ 시행하지 않음(DNR)")],
], [W], heights=[7 * mm] * 3, label_cols=()))

s.append(Spacer(1, 1.8 * mm))
agree = Table([[P("본인은 위 내용에 대하여 충분한 설명을 듣고 이해하였으며, 수술 및 마취 시행에 동의합니다.",
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

build("surgery-anesthesia-consent.pdf", "KAHA-F-2601", "수술·마취 동의서", s)

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
           rowHeights=[7 * mm] + [7.6 * mm] * 10)
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

print("생성 완료")
for f in sorted(os.listdir(OUT)):
    print(" -", f, os.path.getsize(os.path.join(OUT, f)), "bytes")

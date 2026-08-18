# -*- coding: utf-8 -*-
"""KAHA 양식 PDF 생성 — 협회 사무국 표준 서식(form_style.py) 기준.

모든 양식은 form_style 의 요소만 조합해 만든다. 색·테두리·머리글을
이 파일에서 새로 정의하지 않는다.
실행: python3 tools/make_forms.py   (필요: reportlab, fonts-nanum)
"""
import os
import sys
from reportlab.lib.units import mm
from reportlab.platypus import Spacer, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from form_style import (W, P, title_block, info_table, sec, bullets, fields,
                        grid_list, asa_table, rec_table, stack, closing,
                        sign_row, build, LINE, OUT)

LB = 34 * mm              # 구획 라벨 열 폭
CW = W - LB               # 구획 내용 폭
IW = CW - 16              # 구획 안쪽 실제 사용 폭
GAP = 4 * mm

# 인적사항 표 열 폭
L, M = 28 * mm, 26 * mm
V = (W - L - 2 * M) / 2
IN_W = [L, M, V, M, V]

ASA_LINE = "□ Ⅰ 건강    □ Ⅱ 경미한 전신질환    □ Ⅲ 중등도 전신질환    □ Ⅳ 생명 위협    □ Ⅴ 위중    □ E 응급"


G = [GAP]          # 현재 양식의 구획 간격


def gap(h=None):
    return Spacer(1, h if h is not None else G[0])


# ═══════════════════════════════════════════════════════════════════
# 1. 수술등중대진료(마취) 동의서
# ═══════════════════════════════════════════════════════════════════
G[0] = 2.6 * mm
s = title_block("수술등중대진료(마취) 동의서",
                "본 동의서는 「수의사법」 제13조의2 및 같은 법 시행규칙 제13조의3에 따라 작성되었습니다.",
                title_size=22)
s.append(info_table([
    ("보호자", [[P("성명"), "", P("연락처"), ""], [P("주소"), "", None, None]]),
    ("반려동물", [[P("이름"), "", P("종 / 품종"), ""],
                [P("성별 / 중성화"), "", P("연령 / 체중"), ""],
                [P("특이사항"), "", None, None]]),
    ("수의사", [[P("동물병원명"), "", P("면허번호"), ""]]),
], widths=IN_W, heights=[6.9 * mm] * 6))
s.append(gap())

cpr = Paragraph("□ 심폐소생술 원함<br/>□ 심폐소생술 원하지 않음",
                ParagraphStyle("c", fontName="Nanum", fontSize=9, leading=14))
inner = Table([[bullets([
    "위 반려동물의 수술등중대진료를 위해 전신마취가 필요합니다.",
    "마취 중 심정지가 발생할 경우 아래 처치에 동의합니다.",
]), cpr]], colWidths=[CW - 44 * mm, 44 * mm])
inner.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
]))
s.append(sec("설명 및\n동의사항", inner, note="동의하시는 부분에\n체크해주세요.", pad_top=5))
s.append(gap())

lw, mw = 22 * mm, 20 * mm
vw = (IW - lw - mw) / 2
s.append(sec("수술등중대진료의\n필요성 ·\n방법 및 내용", fields([
    [P("진단명"), "", P("예정 일시"), ""],
    [P("수술 / 처치명"), "", P("마취 방식"), ""],
    [P("필요성"), "", None, None],
    [P("방법 및 내용"), "", None, None],
], [lw, vw, mw, vw], [6.5 * mm, 6.5 * mm, 8 * mm, 8 * mm], valign_top=(2, 3)),
    pad_top=4, pad_left=5))
s.append(gap())

s.append(sec("수술등중대진료에\n따라 전형적으로\n발생이 예상되는\n후유증 또는 부작용", stack([
    grid_list(["저혈압, 저체온, 고체온", "약물과민반응에 의한 쇼크", "순환부전에 의한 쇼크",
               "췌장염, 신부전 및 폐수종", "기저질환 발현 및 현증악화", "삽관에 의한 일시적 기침"],
              IW, cols=3, size=8.6, leading=12.4),
    Spacer(1, 2.4 * mm),
    asa_table(IW - 30 * mm),
], IW), pad_top=5))
s.append(gap())

s.append(sec("수술등중대진료\n전후에 보호자의\n준수 및 숙지사항", bullets([
    "마취 시 수술 전 일정 시간의 금식과 금수가 필수적입니다.",
    "마취를 시행함에 있어 발생할 수 있는 부작용, 합병증 또는 후유증에 대한 설명을 충분히 듣고 이해했습니다.",
    "마취 과정에 있어 불가항력적이거나 환자의 특이체질로 인한 우발사고의 가능성을 인정합니다.",
    "보호자의 자유 의사에 의하여 마취를 시행하는 것에 동의합니다.",
    "마취 및 수술비에 관한 구두 설명을 들었으며, 필요시 구두 동의 하에 추가 검사 및 추가 수술을 진행함에 동의합니다.",
], size=8.4, leading=12), pad_top=4))
s.append(Spacer(1, 3.5 * mm))
s.append(closing(
    "「수의사법」 제13조의2 및 같은 법 시행규칙 제13조의3에 따라 위와 같이 수의사로부터 수술등중대진료의 "
    "필요성 · 방법 · 내용과 전형적으로 발생이 예상되는 후유증 및 부작용에 관한 설명을 충분히 듣고 이해하였습니다. "
    "이에 위 수술등중대진료 및 마취의 시행에 동의하며, 시행 과정에서 필요한 수의학적 판단과 처리를 담당 수의사에게 위임합니다.",
    note="*기타 내용이 발생할 경우 별지를 포함합니다."))
s.append(Spacer(1, 3 * mm))
s.append(sign_row(["보호자", "설명 수의사"]))
build("01_수술마취/마취동의서_한국동물병원협회.pdf", "수술등중대진료(마취) 동의서", s)


# ═══════════════════════════════════════════════════════════════════
# 2. 입원 동의서
# ═══════════════════════════════════════════════════════════════════
G[0] = 3.4 * mm
s = title_block("입원 동의서",
                "본 동의서는 입원 진료의 내용 · 비용 · 연락 방식에 관한 설명과 동의를 확인하기 위해 작성되었습니다.",
                title_size=24)
s.append(info_table([
    ("보호자", [[P("성명"), "", P("연락처"), ""], [P("주소"), "", P("제2연락처"), ""]]),
    ("반려동물", [[P("이름"), "", P("종 / 품종"), ""],
                [P("성별 / 중성화"), "", P("연령 / 체중"), ""]]),
    ("수의사", [[P("동물병원명"), "", P("담당 수의사"), ""]]),
], widths=IN_W, heights=[6.9 * mm] * 5))
s.append(gap())

lw = 24 * mm
vw = (IW - lw * 2) / 2
s.append(sec("입원 사유 및\n예상 기간", fields([
    [P("추정 진단명"), "", P("입원 목적"), ""],
    [P("예상 입원 기간"), P("약 ______ 일        ( 20____. ____. ____.  ～  20____. ____. ____. )"), None, None],
], [lw, vw, lw, vw], [8 * mm, 8 * mm]), pad_top=5, pad_left=5))
s.append(gap())

s.append(sec("비용 안내", stack([
    fields([
        [P("1일 입원비"), P("____________ 원"), P("예상 총액"), P("____________ 원")],
        [P("입원비 포함 항목"), "", None, None],
        [P("별도 청구 항목"), P("□ 검사    □ 처치    □ 약제    □ 수혈    □ 기타 :"), None, None],
    ], [lw + 6 * mm, vw - 6 * mm, lw, vw], [8 * mm, 11 * mm, 8 * mm], valign_top=(1,)),
    Spacer(1, 1.6 * mm),
    bullets(["예상액의 ______ % 또는 ____________ 원을 초과할 것으로 예상되면 진행 전에 보호자에게 연락합니다."],
            size=8.4, leading=12),
], IW), pad_top=4, pad_left=5))
s.append(gap())

s.append(sec("경과 보고 및\n연락 방식", bullets([
    "정기 보고 :  □ 1일 1회    □ 1일 2회    □ 기타 ________        보고 방법 :  □ 전화   □ 문자 · 메신저   □ 면회 시 구두",
    "상태가 급변하면 즉시 연락합니다.",
    "연락이 닿지 않을 경우 :  □ 수의사 판단으로 필요한 처치 시행    □ 응급처치만 시행 후 연락 재시도",
], size=8.4, leading=13.4), pad_top=5))
s.append(gap())

s.append(sec("면회 · 반입물품 ·\n야간 관리", bullets([
    "면회 가능 시간 : ____________        면회 제한 사유 :  □ 감염   □ 중환자   □ 기타",
    "반입물품(사료 · 약 · 담요 등) : ____________________   ※ 분실 시 병원이 책임지지 않을 수 있습니다.",
    "야간 · 휴일 관리 :  □ 수의사 상주   □ 간호인력 상주   □ 무인 관리 ( ____시 최종 처치 → ____시 확인 )",
], size=8.4, leading=13.4), pad_top=5))
s.append(gap())

s.append(sec("응급 상황 및\n사망 시 처리", bullets([
    "심정지 시 심폐소생술(CPR) :  □ 시행   □ 시행하지 않음(DNR)",
    "생명 유지에 필요한 응급처치는 연락 전 시행하는 것에 동의합니다.",
    "사망 시 :  □ 사체 인도 희망   □ 병원 위탁 처리   □ 동물장묘업 등록 시설 이용 안내 희망",
], size=8.4, leading=13.4), pad_top=5))
s.append(gap())

s.append(sec("입원 중\n중대진료가\n필요해지는 경우", bullets([
    "전신마취를 동반하는 내부장기 · 뼈 · 관절 수술 또는 전신마취를 동반하는 수혈이 필요해지면, "
    "「수의사법」 제13조의2에 따라 별도의 수술등중대진료 동의서를 작성합니다. 본 입원 동의서가 이를 대신하지 않습니다.",
], size=8.4, leading=13.4), pad_top=5))
s.append(Spacer(1, 3.5 * mm))
s.append(closing(
    "위와 같이 입원 진료의 내용과 예상 비용, 경과 보고 및 연락 방식, 응급 상황에서의 처리에 관하여 "
    "수의사로부터 설명을 충분히 듣고 이해하였으며, 위 조건에 따른 입원 진료에 동의합니다.",
    note="*기타 내용이 발생할 경우 별지를 포함합니다."))
s.append(Spacer(1, 3 * mm))
s.append(sign_row(["보호자", "설명 수의사"]))
build("02_입원응급/입원동의서_한국동물병원협회.pdf", "입원 동의서", s)


# ═══════════════════════════════════════════════════════════════════
# 3. 퇴원 안내문
# ═══════════════════════════════════════════════════════════════════
G[0] = 3.4 * mm
s = title_block("퇴원 안내문",
                "본 안내문은 가정에서의 투약과 관리, 재진 일정에 관한 설명 내용을 기록하기 위해 작성되었습니다.",
                title_size=24)
s.append(info_table([
    ("보호자", [[P("성명"), "", P("연락처"), ""]]),
    ("반려동물", [[P("이름"), "", P("종 / 품종"), ""],
                [P("차트번호"), "", P("퇴원 일시"), ""]]),
    ("수의사", [[P("동물병원명"), "", P("담당 수의사"), ""]]),
], widths=IN_W, heights=[6.9 * mm] * 4))
s.append(gap())

lw = 26 * mm
s.append(sec("진단명 및\n시행한 처치", fields([
    [P("진단명 / 처치"), "", None, None],
    [P("퇴원 시점 상태"), P("□ 각성   □ 반응 있음   □ 체온 회복   □ 통증 조절됨"),
     P("마취 시행"), P("□ 예   □ 아니오")],
], [lw, IW - lw - 20 * mm - 26 * mm, 20 * mm, 26 * mm], [8 * mm, 8 * mm]), pad_top=5, pad_left=5))
s.append(gap())

med_w = [22 * mm, 24 * mm, 16 * mm, 12 * mm, 15 * mm, 17 * mm, 16 * mm]
med_w.append(IW - sum(med_w))
s.append(sec("가정 투약 안내", stack([
    rec_table(["약품명", "무엇 때문에", "1회 용량", "경로", "1일 횟수", "종료일", "식전/식후", "주의할 점"],
              med_w, 3, row_h=7 * mm, head_h=5.6 * mm),
    Spacer(1, 1.6 * mm),
    bullets(["퇴원 전 경구약 투여 방법을 보호자가 직접 해보고 확인하였습니다.",
             "약 보관 방법을 안내하였습니다."], size=8.4, leading=12, marker="□ "),
], IW), pad_top=4, pad_left=5))
s.append(gap())

cal_w = [18 * mm] + [(IW - 18 * mm) / 7] * 7
cal_head = [P("", size=8)] + [P("%d일차" % i, size=8, bold=True) for i in range(1, 8)]
cal = fields([cal_head,
              [P("아침", size=8.4, bold=True)] + [""] * 7,
              [P("저녁", size=8.4, bold=True)] + [""] * 7],
             cal_w, [5.6 * mm, 7 * mm, 7 * mm])
s.append(sec("투약 체크 달력", cal, note="투여 후 표시하세요", pad_top=5, pad_left=5))
s.append(gap())

s.append(sec("가정 관리", bullets([
    "활동 제한 :  □ 산책 제한   □ 계단 · 점프 금지   □ 목줄 산책만        기간 : ________",
    "넥카라 · 수술복 :  □ 착용 필요 ( 기간 : ________ )   □ 해당 없음",
    "절개 부위 :  □ 물 닿지 않게   □ 소독 : ____________        목욕 가능 시점 : ________",
    "식이 · 급수 : ______________________________________________________________",
    "배뇨 · 배변 · 식욕 · 활력에 변화가 있으면 기록해 주세요.",
], size=8.4, leading=13.4), pad_top=5))
s.append(gap())

lw, vw2 = 24 * mm, 46 * mm
s.append(sec("재진 및\n응급 연락", fields([
    [P("다음 내원일"), P("20____. ____. ____.    ____시"), P("재진 목적"),
     P("□ 경과 확인  □ 봉합사 제거  □ 재검사")],
    [P("즉시 연락할 증상"), "", None, None],
    [P("병원 연락처"), "", P("야간 · 휴일"), ""],
], [lw + 4 * mm, vw2, lw, IW - lw * 2 - vw2 - 4 * mm], [8 * mm, 12 * mm, 8 * mm],
    valign_top=(1,)), pad_top=5, pad_left=5))
s.append(Spacer(1, 3.5 * mm))
s.append(closing(
    "위 내용을 안내문과 함께 읽으며 설명하였고, 보호자가 이를 이해하였음을 확인합니다. "
    "마취 후에는 회복기에 상태가 변할 수 있으므로 퇴원 후 몇 시간 동안 특히 주의 깊게 지켜봐 주십시오."))
s.append(Spacer(1, 3 * mm))
s.append(sign_row(["보호자", "설명자"]))
build("02_입원응급/퇴원안내문_한국동물병원협회.pdf", "퇴원 안내문", s)


# ═══════════════════════════════════════════════════════════════════
# 4. 마취 전 평가 · 모니터링 체크리스트  (원내 기록용)
# ═══════════════════════════════════════════════════════════════════
G[0] = 3 * mm
s = title_block("마취 전 평가 · 모니터링 체크리스트",
                "본 기록지는 마취 전 준비와 마취 중 경과, 회복기 관리를 원내에서 기록하기 위한 서식입니다.",
                title_size=19)
s.append(info_table([
    ("반려동물", [[P("이름 / 차트번호"), "", P("종 / 품종"), ""],
                [P("성별 / 중성화"), "", P("연령 / 체중"), ""]]),
    ("수의사", [[P("동물병원명"), "", P("담당 수의사"), ""]]),
], widths=IN_W, heights=[6.9 * mm] * 3))
s.append(gap())

lw = 26 * mm
s.append(sec("환자 평가", stack([
    fields([
    [P("병력 · 현재 투약"), "", None, None],
    [P("신체검사 요약"), "", None, None],
    [P("사전 혈액검사"), P("□ CBC    □ 혈액화학    □ 전해질    □ 응고계    □ 기타 :"), None, None],
], [lw, (IW - lw) / 3, (IW - lw) / 3, (IW - lw) / 3],
    [10 * mm, 10 * mm, 7 * mm], valign_top=(0, 1)),
    Spacer(1, 2 * mm),
    asa_table(IW - 24 * mm),
], IW), pad_top=5, pad_left=5))
s.append(gap())

s.append(sec("마취 전 준비", bullets([
    "금식 확인 — 음식 ______ 시간 · 물 ______ 시간   (병원 프로토콜 기준)",
    "IV 카테터 장착      □ 기관튜브 3종 준비 ( ____ / ____ / ____ )      □ 응급약물 용량 사전 계산 · 비치",
    "마취 회로 · 산소 · 흡인기 점검      □ 항불안 처치 필요 여부 평가 (겁 많음 · 공격성)",
    "보호자 설명 및 수술등중대진료(마취) 동의서 작성 완료",
], size=8.4, leading=12.4, marker="□ "), pad_top=4))
s.append(gap())

mon_w = [16 * mm, 14 * mm, 14 * mm, 16 * mm, 16 * mm, 18 * mm, 16 * mm]
mon_w.append(IW - sum(mon_w))
s.append(sec("마취 중\n모니터링 기록", stack([
    rec_table(["시각", "HR", "RR", "SpO₂", "EtCO₂", "혈압", "체온", "마취심도 · 처치 · 비고"],
              mon_w, 8, row_h=6.2 * mm, head_h=5.6 * mm),
    Spacer(1, 1.4 * mm),
    bullets(["저체온과 저혈압은 가장 흔한 마취 중 합병증입니다. 조기 인지와 가온 · 수액 대응 프로토콜을 준비하십시오."],
            size=8, leading=11.4, marker="※ "),
], IW), note="15분 간격 권장", pad_top=4, pad_left=5))
s.append(gap())

s.append(sec("회복기 관리", bullets([
    "발관 시각 : ________      □ 체온 회복 확인 ( ________ ℃ )      □ 통증 평가 ( 도구 / 점수 : ____________ )",
    "의식 · 기립 확인      □ 퇴원 전 보호자 주의사항 전달",
], size=8.4, leading=12.4, marker="□ "), note="마취 관련 사망 위험이\n높은 구간 — 담당자 지정", pad_top=4))
s.append(Spacer(1, 4 * mm))
s.append(sign_row(["마취 담당", "회복기 담당"]))
build("06_진료기록/마취전평가체크리스트_한국동물병원협회.pdf", "마취 전 평가·모니터링 체크리스트", s)


# ═══════════════════════════════════════════════════════════════════
# 5. 영양 평가 · BCS / MCS 기록지  (원내 기록용)
# ═══════════════════════════════════════════════════════════════════
G[0] = 4.2 * mm
s = title_block("영양 평가 · BCS / MCS 기록지",
                "본 기록지는 모든 환자의 영양 상태를 내원 시마다 선별하고 기록하기 위한 서식입니다.",
                title_size=21)
s.append(info_table([
    ("반려동물", [[P("이름 / 차트번호"), "", P("종 / 품종"), ""],
                [P("연령"), "", P("중성화"), P("□ 예     □ 아니오")]]),
    ("수의사", [[P("동물병원명"), "", P("평가자"), ""]]),
], widths=IN_W, heights=[6.9 * mm] * 3))
s.append(gap())

lw = 28 * mm
vw = (IW - lw * 2) / 2
s.append(sec("식이 이력", fields([
    [P("주식 (제품명 · 형태)"), "", P("1일 급여량 / 횟수"), ""],
    [P("간식 · 사람 음식"), "", P("영양제 · 보조제"), ""],
    [P("식욕 변화"), P("□ 없음  □ 증가  □ 감소 (기간 : ______)"), P("음수량 변화"), P("□ 없음  □ 증가  □ 감소")],
], [lw, vw, lw, vw], [10 * mm] * 3), pad_top=6, pad_left=5))
s.append(gap())

bcs_w = [22 * mm] + [(IW - 22 * mm) / 9] * 9
bcs = Table([[P("BCS (9점)", size=8.4, bold=True)] + [P("□ %d" % i, size=8.4) for i in range(1, 10)]],
            colWidths=bcs_w, rowHeights=[8 * mm])
bcs.setStyle(TableStyle([
    ("GRID", (0, 0), (-1, -1), 0.5, LINE),
    ("BACKGROUND", (0, 0), (0, 0), "#EFEFEF"),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("ALIGN", (1, 0), (-1, 0), "CENTER"),
    ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
]))
lw2 = 26 * mm
s.append(sec("체중 및\n신체 평가", stack([
    fields([[P("금일 체중(kg)"), "", P("직전 체중 / 측정일"), "", P("변화율(%)"), ""]],
           [lw2, (IW - 78 * mm) / 3, 30 * mm, (IW - 78 * mm) / 3, 22 * mm, (IW - 78 * mm) / 3],
           [9 * mm]),
    Spacer(1, 1.4 * mm),
    bcs,
    bullets(["1–3 저체중 · 4–5 이상적 · 6–7 과체중 · 8–9 비만 (갈비뼈 촉진, 허리 라인, 복부 턱업으로 판정)"],
            size=7.8, leading=11.4, marker=""),
    Spacer(1, 1 * mm),
    fields([[P("MCS (근육상태)"), P("□ 정상        □ 경도 소실        □ 중등도 소실        □ 중증 소실"), None, None]],
           [lw2 + 4 * mm, (IW - lw2 - 4 * mm) / 3, (IW - lw2 - 4 * mm) / 3, (IW - lw2 - 4 * mm) / 3],
           [8 * mm]),
    bullets(["척추 · 견갑 · 측두부 · 골반 촉진으로 판정 — 비만 개체도 근소실이 동반될 수 있습니다 (특히 고령 · 만성질환)."],
            size=7.8, leading=11.4, marker=""),
], IW), pad_top=4, pad_left=5))
s.append(gap())

s.append(sec("위험요인\n스크리닝", bullets([
    "□ 질병(만성 포함)    □ 고령    □ 비만 / 저체중    □ 수제식 · 생식 · 비전형 식이    □ 피모 · 치아 이상    □ 체중 급변",
], size=8.4, leading=12.4, marker=""), note="하나라도 해당 시\n확장 평가", pad_top=4))
s.append(gap())

lw3 = 32 * mm
s.append(sec("평가 결과 및 계획", fields([
    [P("확장 평가 필요"), P("□ 불필요        □ 필요  ( 사유 : ________________________________ )"), None],
    [P("권장 사료 · 급여량"), "", None],
    [P("목표 체중 · 재평가 일정"), "", None],
    [P("보호자 상담 내용"), "", None],
], [lw3, (IW - lw3) / 2, (IW - lw3) / 2],
    [9 * mm, 15 * mm, 15 * mm, 26 * mm], valign_top=(1, 2, 3)), pad_top=6, pad_left=5))
s.append(Spacer(1, 4 * mm))
s.append(sign_row(["평가자"]))
build("06_진료기록/영양평가기록지_한국동물병원협회.pdf", "영양 평가·BCS/MCS 기록지", s)

print("생성 완료")
for root, _, files in sorted(os.walk(OUT)):
    for f in sorted(files):
        if f.endswith(".pdf"):
            print(" -", os.path.relpath(os.path.join(root, f), OUT))

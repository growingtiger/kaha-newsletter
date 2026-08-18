# -*- coding: utf-8 -*-
"""질환·처치별 동의서 PDF 생성 — data/procedures.json 을 읽어 한 건씩 만든다.

구성은 협회 사무국 표준 서식(form_style.py)을 그대로 따르고,
내용 길이에 맞춰 각 구획 높이를 자동으로 계산해 A4 한 장을 보장한다.
실행: python3 tools/make_procedure_forms.py
"""
import json
import os
import re
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Spacer, Table, TableStyle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from form_style import (W, P, TOP, BOTTOM, title_block, info_table, sec, bullets,
                        asa_table, closing, sign_row, build, set_form, AUDIT,
                        LABEL_BG, LINE, stack)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = "07_질환별동의서"
LB = 34 * mm
CW = W - LB
IW = CW - 16
AVAIL = A4[1] - TOP - BOTTOM

L, M = 28 * mm, 26 * mm
V = (W - L - 2 * M) / 2
IN_W = [L, M, V, M, V]


def dx_label(e):
    """진단명 옆에 영문명을 괄호로 병기한다.

    한글 쪽에 이미 영문 약어가 붙어 있으면 괄호가 두 번 겹치지 않도록 영문 안으로 합친다.
      '위확장 염전 (GDV)' + 'Gastric Dilatation-Volvulus'
      → '위확장 염전 (Gastric Dilatation-Volvulus, GDV)'
    괄호 안이 한글 설명일 때는(예: '중성화 (암컷)') 그대로 둔다.
    """
    dx, en = e["dx"], e.get("dx_en", "")
    if not en:
        return dx
    m = re.search(r"\s*\(([A-Za-z0-9]+)\)\s*$", dx)
    if m and m.group(1).lower() not in en.lower():
        dx, en = dx[:m.start()], "%s, %s" % (en, m.group(1))
    return "%s (%s)" % (dx, en)

LEGAL = "본 동의서는 「수의사법」 제13조의2 및 같은 법 시행규칙 제13조의2에 따라 작성되었습니다."
DECL = ("「수의사법」 제13조의2 및 같은 법 시행규칙 제13조의2에 따라 위와 같이 수의사로부터 진료의 필요성 · 방법 · "
        "내용과 전형적으로 예상되는 후유증 및 부작용에 관한 설명을 충분히 듣고 이해하였습니다. "
        "이에 위 진료의 시행에 동의하며, 시행 과정에서 필요한 수의학적 판단과 처리를 담당 수의사에게 위임합니다.")


def two_box(left_label, left_val, right_label, right_val, h=11 * mm):
    """진단명 · 수술 방법을 나란히 놓는 두 칸.

    영문명을 병기하면서 값이 길어졌다. 칸 폭에 맞춰 글자를 줄이되 읽을 수 있는
    크기(7.6pt)까지만 줄이고, 그래도 넘치면 두 줄로 둔다. 칸 높이는 두 줄이
    들어가도록 잡아 한 줄이든 두 줄이든 세로 가운데에 오게 한다.
    """
    from reportlab.pdfbase.pdfmetrics import stringWidth
    half = (W - 4) / 2
    lw = 26 * mm
    def vsize(val):
        avail = half - lw - 12
        s = 8.8
        while s > 7.6 and stringWidth(val, "Nanum", s) > avail:
            s -= 0.2
        return round(s, 1)
    def one(lbl, val):
        vs = vsize(val)
        t = Table([[P(lbl, bold=True, size=8.8), P(val, size=vs, leading=vs + 3.4)]],
                  colWidths=[lw, half - lw], rowHeights=[h])
        t.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.9, LINE),
            ("LINEAFTER", (0, 0), (0, 0), 0.6, LINE),
            ("BACKGROUND", (0, 0), (0, 0), LABEL_BG),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (0, 0), 5), ("LEFTPADDING", (1, 0), (1, 0), 7),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return t
    outer = Table([[one(left_label, left_val), "", one(right_label, right_val)]],
                  colWidths=[half, 4, half])
    outer.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return outer


def blank_lines(n, size=8.6, leading=12.6):
    return bullets([" "] * n, size=size, leading=leading, marker="· ")


def build_one(e, blanks=2, gap=2.4 * mm, lead=12.6, info_h=7.6 * mm, tail=0):
    """한 건의 story 를 만든다.

    blanks  각 구획에 남길 빈 줄 수
    info_h  보호자·반려동물·수의사 기입 칸의 행 높이 (남는 공간만큼 키운다)
    tail    동의 선언문 앞에 넣는 여백 — 남는 공간을 여기로 보내 서명줄을 맨 아래로 내린다
    """
    set_form(e["title"])
    s = title_block(e["title"], LEGAL, title_size=22 if len(e["title"]) < 20 else 18)
    s.append(info_table([
        ("보호자", [[P("성명"), "", P("연락처"), ""], [P("주소"), "", None, None]]),
        ("반려동물", [[P("이름"), "", P("종 / 품종"), ""],
                    [P("성별 / 중성화"), P("□ 암  □ 수       □ 중성화"), P("연령 / 체중"), ""],
                    [P("특이사항"), "", None, None]]),
        ("수의사", [[P("동물병원명"), "", P("수의사 성명"), ""],
                  [P("면허번호"), "", None, None]]),
    ], widths=IN_W, heights=[info_h] * 7))
    s.append(Spacer(1, gap))
    s.append(two_box("진 단 명", dx_label(e), "시행 방법", e["proc"]))
    s.append(Spacer(1, gap))

    def block(label, items, extra=None):
        rows = [bullets(items, size=8.6, leading=lead)]
        if extra is not None:
            rows += [Spacer(1, 1.6 * mm), extra]
        if blanks:
            rows.append(blank_lines(blanks, leading=lead))
        return sec(label, stack(rows, IW) if len(rows) > 1 else rows[0], pad_top=4)

    if e.get("about"):
        s.append(block("질환에 대한 설명", e["about"]))
        s.append(Spacer(1, gap))
    s.append(block("진료의 필요성 ·\n방법 및 내용", e["need"]))
    s.append(Spacer(1, gap))
    # ASA 등급표는 마취 동의서에만 둔다 (2026-08-18 원장 지시) — 여기서 빈 자리는
    # 질환 설명과 후유증 항목을 늘리는 데 쓴다.
    s.append(block("전형적으로\n발생이 예상되는\n후유증 또는 부작용", e["risk"]))
    s.append(Spacer(1, gap))
    s.append(block("진료 전후에\n보호자의\n준수 및 숙지 사항", e["care"]))
    s.append(Spacer(1, 3 * mm + tail))
    s.append(closing(DECL))
    s.append(Spacer(1, 2.6 * mm))
    s.append(sign_row(["보호자", "설명 수의사"]))
    return s


def height(story):
    return sum(f.wrap(W, AVAIL)[1] for f in story)


INFO_MIN = 7.6 * mm
INFO_MAX = 12 * mm
SAFETY = 5 * mm


def main():
    data = json.load(open(os.path.join(BASE, "data", "procedures.json"), encoding="utf-8"))
    made, tight = 0, []
    for e in data:
        # 1) 내용이 들어가는 조합을 찾는다 (빈 줄 → 간격 → 줄간격 순으로 줄임)
        for blanks, gap, lead in ((2, 2.4, 12.6), (1, 2.4, 12.6), (1, 2.0, 12.0),
                                  (0, 2.0, 12.0), (0, 1.6, 11.4)):
            story = build_one(e, blanks, gap * mm, lead)
            h = height(story)
            if h <= AVAIL - SAFETY:
                break

        # 2) 공간이 남으면 각 구획의 빈 줄을 늘려 병원이 적을 자리를 넓힌다
        while blanks < 4:
            trial = build_one(e, blanks + 1, gap * mm, lead)
            th = height(trial)
            if th > AVAIL - SAFETY - 12 * mm:
                break
            blanks += 1
            story, h = trial, th

        # 3) 그래도 남는 공간의 절반은 기입 칸을 키우는 데 쓴다 (볼펜으로 쓰기 편하도록)
        room = AVAIL - SAFETY - h
        info_h = min(INFO_MAX, INFO_MIN + max(0, room * 0.5) / 7)
        story = build_one(e, blanks, gap * mm, lead, info_h)
        h = height(story)

        # 4) 그러고도 남는 공간은 서명 앞으로 보내 서명줄을 맨 아래에 둔다
        tail = max(0, AVAIL - SAFETY - h)
        if tail > 0.5 * mm:
            story = build_one(e, blanks, gap * mm, lead, info_h, tail)
            h = height(story)

        if h > AVAIL - 1 * mm:
            tight.append((e["title"], (h - AVAIL) / mm))
        build(os.path.join(ROOT, e["dir"], e["file"] + ".pdf"), e["title"], story)
        made += 1
    print("질환별 동의서 PDF %d건 생성" % made)
    over = [a for a in AUDIT if a[2] > a[3] + 1]
    if over:
        print("  ⚠ 칸 넘침 %d건" % len(over))
        for a in over[:5]:
            print("     [%s] %s" % (a[0][:16], a[1][:40]))
    if tight:
        print("  ⚠ 한 장 초과 위험 %d건" % len(tight))
        for t in tight[:5]:
            print("     %s (%+.1fmm)" % t)
    if not over and not tight:
        print("  ✓ 전 건 A4 한 장 · 칸 넘침 없음 · 서명줄 하단 정렬")


if __name__ == "__main__":
    main()

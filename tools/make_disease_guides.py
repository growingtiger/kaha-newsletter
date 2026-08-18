# -*- coding: utf-8 -*-
"""질환 안내문 PDF 생성 — data/diseases.json 을 읽어 한 건씩 만든다.

보호자에게 건네는 설명 자료다. 동의서와 달리 서명은 '설명을 들었다'는
확인 용도이며, 병원이 개체별 내용을 적을 메모 칸을 둔다.
구성은 협회 사무국 표준 서식(form_style.py)을 따르고, 내용 길이에 맞춰
구획 높이를 자동 계산해 A4 한 장을 보장한다.
실행: python3 tools/make_disease_guides.py
"""
import json
import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Spacer, Table, TableStyle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from form_style import (W, P, TOP, BOTTOM, title_block, info_table, sec, bullets,
                        closing, sign_row, build, set_form, AUDIT, LABEL_BG, LINE, stack)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = "08_질환안내문"
LB = 34 * mm
IW = W - LB - 16
AVAIL = A4[1] - TOP - BOTTOM
SAFETY = 5 * mm

L, M = 28 * mm, 26 * mm
V = (W - L - 2 * M) / 2
IN_W = [L, M, V, M, V]

SUB = "이 안내문은 보호자께 반려동물의 질환을 설명해 드리기 위한 자료입니다."
FOOT = ("이 안내문은 일반적인 설명이며, 실제 경과와 치료 방침은 개체 상태에 따라 달라집니다. "
        "궁금한 점은 언제든 담당 수의사에게 물어봐 주십시오.")


def name_box(name, eng, h=9 * mm):
    half = (W - 4) / 2
    lw = 26 * mm
    def one(lbl, val):
        t = Table([[P(lbl, bold=True, size=8.8), P(val, size=8.8)]],
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
    outer = Table([[one("진 단 명", name), "", one("영문 · 이명", eng)]],
                  colWidths=[half, 4, half])
    outer.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return outer


def build_one(e, memo=3, gap=2.4 * mm, lead=12.4, info_h=7.6 * mm, tail=0):
    set_form(e["name"] + " 안내문")
    title = e["name"] + " 안내문"
    s = title_block(title, SUB, title_size=22 if len(title) < 18 else 18)
    s.append(info_table([
        ("보호자", [[P("성명"), "", P("연락처"), ""]]),
        ("반려동물", [[P("이름"), "", P("종 / 품종"), ""],
                    [P("연령 / 체중"), "", P("진단일"), ""]]),
        ("수의사", [[P("동물병원명"), "", P("담당 수의사"), ""]]),
    ], widths=IN_W, heights=[info_h] * 4))
    s.append(Spacer(1, gap))
    s.append(name_box(e["name"], e.get("eng", "")))
    s.append(Spacer(1, gap))

    def block(label, items, size=8.6):
        return sec(label, bullets(items, size=size, leading=lead), pad_top=4)

    s.append(block("어떤 질환인가요", e["what"]))
    s.append(Spacer(1, gap))
    s.append(block("이런 증상이\n나타납니다", e["sign"]))
    s.append(Spacer(1, gap))
    s.append(block("어떻게 진단하고\n치료하나요", e["tx"]))
    s.append(Spacer(1, gap))
    s.append(block("집에서 이렇게\n관리해 주세요", e["home"]))
    s.append(Spacer(1, gap))
    s.append(block("이럴 때는\n바로 연락 주세요", e["warn"]))
    s.append(Spacer(1, gap))
    s.append(sec("담당 수의사\n메모", bullets([" "] * memo, size=8.6, leading=lead), pad_top=4))
    s.append(Spacer(1, 3 * mm + tail))
    s.append(closing(FOOT))
    s.append(Spacer(1, 2.6 * mm))
    s.append(sign_row(["보호자", "설명자"]))
    return s


def height(story):
    return sum(f.wrap(W, AVAIL)[1] for f in story)


INFO_MIN, INFO_MAX = 7.6 * mm, 12 * mm


def main():
    data = json.load(open(os.path.join(BASE, "data", "diseases.json"), encoding="utf-8"))
    made, tight = 0, []
    for e in data:
        for memo, gap, lead in ((3, 2.4, 12.4), (2, 2.4, 12.4), (2, 2.0, 11.8),
                                (1, 2.0, 11.8), (1, 1.6, 11.2), (0, 1.6, 11.2)):
            story = build_one(e, memo, gap * mm, lead)
            h = height(story)
            if h <= AVAIL - SAFETY:
                break
        while memo < 5:
            trial = build_one(e, memo + 1, gap * mm, lead)
            th = height(trial)
            if th > AVAIL - SAFETY - 10 * mm:
                break
            memo += 1
            story, h = trial, th
        room = AVAIL - SAFETY - h
        info_h = min(INFO_MAX, INFO_MIN + max(0, room * 0.5) / 4)
        story = build_one(e, memo, gap * mm, lead, info_h)
        h = height(story)
        tail = max(0, AVAIL - SAFETY - h)
        if tail > 0.5 * mm:
            story = build_one(e, memo, gap * mm, lead, info_h, tail)
            h = height(story)
        if h > AVAIL - 1 * mm:
            tight.append((e["name"], (h - AVAIL) / mm))
        build(os.path.join(ROOT, e["dir"], e["file"] + ".pdf"), e["name"] + " 안내문", story)
        made += 1
    print("질환 안내문 PDF %d건 생성" % made)
    over = [a for a in AUDIT if a[2] > a[3] + 1]
    if over:
        print("  ⚠ 칸 넘침 %d건" % len(over))
        for a in over[:5]:
            print("     [%s] %s" % (a[0][:16], a[1][:40]))
    if tight:
        print("  ⚠ 한 장 초과 %d건" % len(tight))
        for t in tight[:5]:
            print("     %s (%+.1fmm)" % t)
    if not over and not tight:
        print("  ✓ 전 건 A4 한 장 · 칸 넘침 없음")


if __name__ == "__main__":
    main()

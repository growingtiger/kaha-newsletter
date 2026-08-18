# -*- coding: utf-8 -*-
"""노무·행정 서식 PDF 생성 — data/admin_forms.json 을 읽어 한 건씩 만든다.

병원 내부에서 쓰는 서식(근로계약, 휴가 신청, 시말서 등)이라 구성이
서식마다 다르므로, 블록 목록으로 정의한다.

블록 종류
  fields  라벨 + 기입 칸 표      {"t":"fields","label":"...","rows":[[라벨, 값, 높이배수], ...]}
  text    자유 기술란            {"t":"text","label":"...","lines":6}
  checks  체크 항목 줄           {"t":"checks","label":"...","items":["□ ...", ...]}
  note    안내 문단              {"t":"note","label":"...","items":["...", ...]}
실행: python3 tools/make_admin_forms.py
"""
import json
import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import Spacer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from form_style import (W, P, TOP, BOTTOM, title_block, sec, bullets, fields,
                        closing, sign_row, build, set_form, AUDIT)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = "09_노무행정"
LB = 34 * mm
IW = W - LB - 16
AVAIL = A4[1] - TOP - BOTTOM
SAFETY = 5 * mm


def render(block, row_h, lead, scale=1.0):
    t = block["t"]
    if t == "fields":
        rows, heights = [], []
        lw = block.get("lw", 30) * mm
        for r in block["rows"]:
            label, val = r[0], r[1]
            mult = r[2] if len(r) > 2 else 1
            rows.append([P(label), P(val) if val else "", None, None])
            heights.append(row_h * mult)
        vw = (IW - lw) / 3
        return sec(block["label"],
                   fields(rows, [lw, vw, vw, vw], heights,
                          valign_top=tuple(i for i, r in enumerate(block["rows"])
                                           if len(r) > 2 and r[2] > 1.4)),
                   pad_top=4, pad_left=5)
    if t == "text":
        n = max(1, int(block.get("lines", 5) * scale))
        return sec(block["label"], bullets([" "] * n, size=8.6, leading=lead, marker=""),
                   pad_top=4)
    if t == "checks":
        return sec(block["label"], bullets(block["items"], size=8.6, leading=lead, marker=""),
                   pad_top=4)
    return sec(block["label"], bullets(block["items"], size=8.4, leading=lead), pad_top=4)


def build_one(e, row_h=8 * mm, gap=2.6 * mm, lead=12.6, scale=1.0, tail=0):
    set_form(e["title"])
    s = title_block(e["title"], e.get("sub", ""),
                    title_size=22 if len(e["title"]) < 18 else 18)
    for b in e["blocks"]:
        s.append(render(b, row_h, lead, scale))
        s.append(Spacer(1, gap))
    s.append(Spacer(1, 1 * mm + tail))
    if e.get("decl"):
        s.append(closing(e["decl"]))
        s.append(Spacer(1, 2.6 * mm))
    s.append(sign_row(e.get("sign", ["작성자"])))
    return s


def height(story):
    return sum(f.wrap(W, AVAIL)[1] for f in story)


def main():
    data = json.load(open(os.path.join(BASE, "data", "admin_forms.json"), encoding="utf-8"))
    made, tight = 0, []
    for e in data:
        for row_h, gap, lead, scale in ((8, 2.6, 12.6, 1.0), (7.4, 2.2, 12.0, 1.0),
                                        (7.0, 2.0, 11.6, 0.8), (6.6, 1.8, 11.2, 0.7),
                                        (6.2, 1.6, 10.8, 0.55)):
            story = build_one(e, row_h * mm, gap * mm, lead, scale)
            h = height(story)
            if h <= AVAIL - SAFETY:
                break
        # 남는 공간은 기입 칸을 키우는 데 먼저 쓰고, 나머지는 서명 앞으로
        for extra in (3.0, 2.0, 1.0, 0.0):
            trial = build_one(e, (row_h + extra) * mm, gap * mm, lead, scale)
            th = height(trial)
            if th <= AVAIL - SAFETY:
                story, h, row_h = trial, th, row_h + extra
                break
        tail = max(0, AVAIL - SAFETY - h)
        if tail > 0.5 * mm:
            story = build_one(e, row_h * mm, gap * mm, lead, scale, tail)
            h = height(story)
        if h > AVAIL - 1 * mm:
            tight.append((e["title"], (h - AVAIL) / mm))
        build(os.path.join(ROOT, e["dir"], e["file"] + ".pdf"), e["title"], story)
        made += 1
    print("노무·행정 서식 PDF %d건 생성" % made)
    over = [a for a in AUDIT if a[2] > a[3] + 1]
    if over:
        print("  ⚠ 칸 넘침 %d건" % len(over))
        for a in over[:5]:
            print("     [%s] %s" % (a[0][:16], a[1][:44]))
    if tight:
        print("  ⚠ 한 장 초과 %d건" % len(tight))
        for t in tight[:5]:
            print("     %s (%+.1fmm)" % t)
    if not over and not tight:
        print("  ✓ 전 건 A4 한 장 · 칸 넘침 없음")


if __name__ == "__main__":
    main()

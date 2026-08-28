# -*- coding: utf-8 -*-
"""official/ 에 실제로 놓인 파일을 data/official_forms.json 항목에 붙인다.

항목의 form_no 에 적힌 별지 번호로 짝을 찾는다. 파일이 있으면 「받는 곳 안내」가
「PDF 내려받기」로 바뀌고, 아직 없는 서식은 안내 그대로 남는다.
서식의 개정 표기는 PDF 첫 쪽에서 읽어 rev 에 넣는다.

실행: python3 tools/attach_official_files.py
"""
import json
import os
import re

import pypdfium2 as pdfium

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REV = re.compile(r"<\s*(신설|개정)\s*([0-9]{4}\s*\.\s*[0-9]{1,2}\s*\.\s*[0-9]{1,2})")
NO = re.compile(r"별지\s*제?\s*([0-9]+호(?:의\d)?)")
ASOF = "2026-08-19"


def rev_of(path):
    try:
        d = pdfium.PdfDocument(path)
        t = d[0].get_textpage().get_text_range()
        d.close()
    except Exception:
        return ""
    m = REV.search(t)
    if not m:
        return "개정 표기 없음"
    return "%s. 판" % m.group(2).replace(" ", "").rstrip(".")


def main():
    # official/ 에 있는 파일을 별지 번호로 색인한다
    byno = {}
    for root, _, names in os.walk(os.path.join(BASE, "official")):
        for n in names:
            if not n.lower().endswith(".pdf"):
                continue
            m = NO.search(n)
            if m:
                rel = os.path.relpath(os.path.join(root, n), BASE)
                byno[m.group(1)] = rel

    p = os.path.join(BASE, "data", "official_forms.json")
    rows = json.load(open(p, encoding="utf-8"))
    n = 0
    for e in rows:
        if e.get("files"):
            continue
        m = NO.search(e.get("form_no", ""))
        if not m or m.group(1) not in byno:
            continue
        rel = byno[m.group(1)]
        e["files"] = [{"label": "PDF", "path": rel}]
        e["rev"] = rev_of(os.path.join(BASE, rel))
        e["asof"] = ASOF
        e.pop("site", None)
        e.pop("path", None)
        e.pop("url", None)
        n += 1
        print("   붙임: %-28s %s  (%s)" % (e["title"], rel.split("/")[-1], e["rev"]))

    json.dump(rows, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(p, "a", encoding="utf-8").write("\n")
    got = sum(1 for e in rows if e.get("files"))
    print("파일 붙은 항목 %d건 / 안내만 %d건 (이번에 %d건 추가)"
          % (got, len(rows) - got, n))
    left = [e["title"] for e in rows if not e.get("files")]
    if left:
        print("아직 파일이 없는 서식:")
        for t in left:
            print("   -", t)


if __name__ == "__main__":
    main()

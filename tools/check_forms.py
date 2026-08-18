# -*- coding: utf-8 -*-
"""골든룰 검사 — 모든 PDF·워드 양식이 A4 한 장에 다 들어오는지 확인한다.

절대 규칙(2026-08-18 원장 지시): 인쇄했을 때 내용이 한 장을 벗어나면 안 된다.
이 스크립트가 실패하면 배포하지 않는다.

검사 항목
  1) PDF 페이지 수 = 1
  2) PDF 내용이 인쇄 가능 영역(종이 끝에서 SAFE_EDGE) 안에 있는지
  3) 워드 → PDF 변환 후 페이지 수 = 1
  4) 워드 원문의 모든 문구가 변환 결과에 남아 있는지 (칸에서 잘려 사라지지 않았는지)

실행: python3 tools/check_forms.py
"""
import glob
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

import pypdfium2 as pdfium

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMS = os.path.join(BASE, "forms")
MM = 72 / 25.4                      # 1mm in PDF points
A4_W, A4_H = 210 * MM, 297 * MM
SAFE_EDGE = 8 * MM                  # 종이 끝에서 이만큼 안쪽에 내용이 있어야 함
                                    # (가정용·사무용 프린터의 인쇄 불가 영역을 감안한 값)

fails = []


def content_bbox(page):
    """페이지에 그려진 모든 요소를 감싸는 사각형."""
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for obj in page.get_objects():
        try:
            l, b, r, t = obj.get_bounds()
        except Exception:
            continue
        x0, y0 = min(x0, l), min(y0, b)
        x1, y1 = max(x1, r), max(y1, t)
    return (x0, y0, x1, y1) if x1 > -1e9 else None


def check_pdf(path, label):
    doc = pdfium.PdfDocument(path)
    n = len(doc)
    name = os.path.basename(path)
    if n != 1:
        fails.append("%s %s — %d쪽 (1쪽이어야 함)" % (label, name, n))
        return None
    box = content_bbox(doc[0])
    if box is None:
        fails.append("%s %s — 내용 없음" % (label, name))
        return None
    x0, y0, x1, y1 = box
    over = []
    if x0 < SAFE_EDGE - 0.5:
        over.append("왼쪽 %.1fmm" % (x0 / MM))
    if y0 < SAFE_EDGE - 0.5:
        over.append("아래 %.1fmm" % (y0 / MM))
    if x1 > A4_W - SAFE_EDGE + 0.5:
        over.append("오른쪽 %.1fmm" % ((A4_W - x1) / MM))
    if y1 > A4_H - SAFE_EDGE + 0.5:
        over.append("위 %.1fmm" % ((A4_H - y1) / MM))
    if over:
        fails.append("%s %s — 인쇄 여백 부족: %s" % (label, name, ", ".join(over)))
    return (x0 / MM, y0 / MM, (A4_W - x1) / MM, (A4_H - y1) / MM)


def docx_texts(path):
    """워드 문서의 문단별 문구 목록 (짧은 조각·기호는 제외)."""
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    body = xml.split("<w:body>")[-1]
    out = []
    for para in re.findall(r"<w:p[ >].*?</w:p>", body, re.S):
        txt = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", para))
        txt = html.unescape(txt)          # &apos; 등 XML 실체참조를 되돌린다
        txt = re.sub(r"\s+", "", txt)
        if len(txt) >= 12:
            out.append(txt)
    return out


def convert_all(paths, tmp):
    """워드를 한 번에 묶어 변환한다 (파일이 많을 때 훨씬 빠르다)."""
    for i in range(0, len(paths), 25):
        subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", "--outdir", tmp]
                       + paths[i:i + 25],
                       check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def check_docx(path, tmp):
    name = os.path.basename(path)
    out = os.path.join(tmp, os.path.splitext(name)[0] + ".pdf")
    if not os.path.exists(out):
        fails.append("워드 %s — PDF 변환 실패(검사 불가)" % name)
        return
    doc = pdfium.PdfDocument(out)
    if len(doc) != 1:
        fails.append("워드 %s — %d쪽 (1쪽이어야 함)" % (name, len(doc)))
        return
    rendered = re.sub(r"\s+", "", doc[0].get_textpage().get_text_range())
    missing = [t for t in docx_texts(path) if t not in rendered]
    if missing:
        fails.append("워드 %s — 칸에서 잘려 사라진 문구 %d건: %s"
                     % (name, len(missing), " / ".join(m[:34] + "…" for m in missing[:2])))


# ── 칸 높이 대비 글자가 넘치지 않는지 (워드 잘림 방지) ────────────────
# 워드는 사용자 PC의 폰트로 다시 그린다. 칸 높이가 EXACT로 고정돼 있으므로
# 글자가 예상보다 한 줄 더 늘어나면 그 줄은 잘려서 인쇄되지 않는다.
# 각 칸에 필요한 높이를 직접 계산해 고정 높이와 비교한다.
import xml.etree.ElementTree as ET

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
MARGIN_SLACK = 1.06        # 폰트가 6% 넓어져도 견디는지 함께 확인


def _em_width(text, half_pt):
    """글자 폭 추정(twips). 한글·전각 1em, 그 외 0.5em."""
    em = half_pt / 2.0 * 20
    return sum(em if ord(c) > 0x1100 else em * 0.5 for c in text)


def _para_height(p, avail_w, scale):
    """문단 높이. 줄바꿈(<w:br/>)으로 나눈 각 조각이 각각 몇 줄을 차지하는지 센다."""
    import math
    sz = p.find("./%spPr/%srPr/%ssz" % (W, W, W))
    if sz is None:
        sz = p.find("./%sr/%srPr/%ssz" % (W, W, W))
    size = int(sz.get(W + "val")) if sz is not None else 17
    sp = p.find("./%spPr/%sspacing" % (W, W))
    line = int(sp.get(W + "line")) if sp is not None and sp.get(W + "line") else 240

    # 문서 순서대로 훑으며 <w:br/> 에서 조각을 끊는다
    segments, cur = [], ""
    for node in p.iter():
        if node.tag == W + "br":
            segments.append(cur)
            cur = ""
        elif node.tag == W + "t":
            cur += node.text or ""
    segments.append(cur)

    lines = 0
    for seg in segments:
        if not seg:
            lines += 1
            continue
        need = _em_width(seg, size) * scale
        lines += max(1, int(math.ceil(need / max(avail_w, 1))))
    return line * max(1, lines)


def _cell_height(tc, scale):
    w = tc.find("./%stcPr/%stcW" % (W, W))
    width = int(w.get(W + "w")) if w is not None else 1000
    mar = tc.find("./%stcPr/%stcMar" % (W, W))
    def m(side, default):
        if mar is None:
            return default
        e = mar.find("%s%s" % (W, side))
        return int(e.get(W + "w")) if e is not None else default
    avail_w = width - m("left", 90) - m("right", 70)
    total = m("top", 20) + m("bottom", 20)
    for child in tc:
        if child.tag == W + "p":
            total += _para_height(child, avail_w, scale)
        elif child.tag == W + "tbl":
            total += _table_height(child, scale)
    return total


def _table_height(tbl, scale):
    h = 0
    for tr in tbl.findall("./%str" % W):
        th = tr.find("./%strPr/%strHeight" % (W, W))
        h += int(th.get(W + "val")) if th is not None else 240
    return h


def check_cell_fit(path):
    """고정 높이 칸에 글자가 다 들어가는지 확인. (잘림, 여유부족) 목록을 돌려준다."""
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    clipped, tight = [], []
    for tr in root.iter(W + "tr"):
        th = tr.find("./%strPr/%strHeight" % (W, W))
        if th is None or th.get(W + "hRule") != "exact":
            continue
        row_h = int(th.get(W + "val"))
        for tc in tr.findall("./%stc" % W):
            txt = "".join(t.text or "" for t in tc.iter(W + "t")).strip()
            if not txt:
                continue
            need = _cell_height(tc, 1.0)
            if need > row_h:
                clipped.append((txt, need, row_h))
            elif _cell_height(tc, MARGIN_SLACK) > row_h:
                tight.append((txt, need, row_h))
    return clipped, tight


def main():
    pdfs = sorted(glob.glob(os.path.join(FORMS, "**", "*.pdf"), recursive=True))
    docxs = sorted(glob.glob(os.path.join(FORMS, "**", "*.docx"), recursive=True))
    print("골든룰 검사 — A4 한 장 (PDF %d개 · 워드 %d개)\n" % (len(pdfs), len(docxs)))

    print("PDF")
    quiet = len(pdfs) > 20
    for p in pdfs:
        m = check_pdf(p, "PDF")
        nm = os.path.basename(p).replace("_한국동물병원협회.pdf", "")
        if m and not quiet:
            print("  %-22s 1쪽 · 여백 좌 %.0f 우 %.0f 상 %.0f 하 %.0fmm" % (nm, m[0], m[2], m[3], m[1]))
    if quiet:
        print("  %d개 검사 — 전부 1쪽 · 여백 8mm 이상" % len(pdfs))

    print("\n워드 (LibreOffice 변환 대조)")
    tmp = tempfile.mkdtemp()
    try:
        convert_all(docxs, tmp)
        for p in docxs:
            check_docx(p, tmp)
            nm = os.path.basename(p).replace("_한국동물병원협회.docx", "")
            clipped, tight = check_cell_fit(p)
            quiet = len(docxs) > 20
            if clipped:
                fails.append("워드 %s — 칸보다 글자가 큰 곳 %d건(잘림): %s"
                             % (os.path.basename(p), len(clipped),
                                " / ".join(c[0][:30] + "…" for c in clipped[:2])))
                print("  %-22s ✗ 칸 넘침 %d건" % (nm, len(clipped)))
            elif tight:
                fails.append("워드 %s — 폰트가 조금만 넓어져도 잘릴 칸 %d건: %s"
                             % (os.path.basename(p), len(tight),
                                " / ".join(t[0][:30] + "…" for t in tight[:2])))
                print("  %-22s ⚠ 여유 부족 %d건" % (nm, len(tight)))
            elif not quiet:
                print("  %-22s 검사 완료 (칸 여유 확보)" % nm)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print()
    if fails:
        print("✗ 골든룰 위반 %d건" % len(fails))
        for f in fails:
            print("   -", f)
        sys.exit(1)
    print("✓ 전 파일 A4 한 장 · 잘린 문구 없음 · 인쇄 여백 확보")


if __name__ == "__main__":
    main()

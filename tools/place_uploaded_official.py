# -*- coding: utf-8 -*-
"""원장이 올려 준 공식 서식 PDF를 서식 번호로 알아보고 official/ 에 배치한다.

파일명이 업로드 과정에서 뭉개지므로 **PDF 첫 쪽에 박힌 서식 표기**를 읽어
어떤 서식인지 판단한다. 사람이 파일명을 보고 옮기다 잘못 넣는 일을 막는다.

실행: python3 tools/place_uploaded_official.py <업로드_폴더>
"""
import os
import re
import shutil
import sys

import pypdfium2 as pdfium

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (법령, 별지 번호) → (넣을 분류, 저장 이름)
KNOWN = {
    ("수의사법", "4호의2"): ("07_법정서식", "진단서_별지제4호의2서식"),
    ("수의사법", "5호"):    ("07_법정서식", "폐사진단서_별지제5호서식"),
    ("수의사법", "6호"):    ("07_법정서식", "출산증명서_별지제6호서식"),
    ("수의사법", "7호"):    ("07_법정서식", "사산증명서_별지제7호서식"),
    ("수의사법", "8호"):    ("07_법정서식", "예방접종증명서_별지제8호서식"),
    ("수의사법", "9호"):    ("07_법정서식", "검안서_별지제9호서식"),
    ("수의사법", "10호"):   ("07_법정서식", "처방전_별지제10호서식"),
    ("수의사법", "11호"):   ("07_법정서식", "수술등중대진료동의서_별지제11호서식"),
    ("수의사법", "11호의2"): ("07_법정서식", "수의사실태취업상황신고서_별지제11호의2서식"),
    ("수의사법", "12호"):   ("07_법정서식", "동물병원개설신고서_별지제12호서식"),
    ("수의사법", "14호"):   ("07_법정서식", "동물병원개설신고확인증_별지제14호서식"),
    ("수의사법", "15호"):   ("07_법정서식", "동물병원개설변경신고서_별지제15호서식"),
    ("수의사법", "17호"):   ("07_법정서식", "동물병원휴업폐업신고서_별지제17호서식"),
    ("동물보호법", "1호"):  ("06_동물등록", "동물등록신청서_별지제1호서식"),
    ("동물보호법", "3호"):  ("06_동물등록", "동물등록증재발급신청서_별지제3호서식"),
    ("동물보호법", "4호"):  ("06_동물등록", "동물등록변경신고서_별지제4호서식"),
}

HEAD = re.compile(r"(수의사법|동물보호법)\s*시행규칙\s*\[별지\s*제?\s*([0-9]+호(?:의\d)?)")
BARE = re.compile(r"\[별지\s*제?\s*([0-9]+호(?:의\d)?)")
REV = re.compile(r"<\s*(신설|개정)\s*([0-9]{4}\s*\.\s*[0-9]{1,2}\s*\.\s*[0-9]{1,2})")


def read_head(path):
    d = pdfium.PdfDocument(path)
    t = d[0].get_textpage().get_text_range()
    d.close()
    return t


def identify(text):
    m = HEAD.search(text)
    if m:
        return m.group(1), m.group(2).replace("호의", "호의")
    # 「[별지 제4호의2] 진단서」처럼 법령명이 빠진 것 — 서식명으로 판단
    m = BARE.search(text)
    if m and "진 단 서" in text:
        return "수의사법", m.group(1)
    return None, None


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if not src or not os.path.isdir(src):
        raise SystemExit("사용법: python3 tools/place_uploaded_official.py <업로드_폴더>")

    placed, skipped, unknown = [], [], []
    for name in sorted(os.listdir(src)):
        if not name.lower().endswith(".pdf"):
            continue
        p = os.path.join(src, name)
        try:
            t = read_head(p)
        except Exception:
            continue
        law, no = identify(t)
        key = (law, no)
        if key not in KNOWN:
            if law:
                unknown.append("%s 별지 제%s호" % (law, no))
            continue
        cat, stem = KNOWN[key]
        rev = REV.search(t)
        revtxt = ("%s %s" % (rev.group(1), rev.group(2).replace(" ", ""))) if rev else "표기 없음"
        outdir = os.path.join(BASE, "official", cat)
        os.makedirs(outdir, exist_ok=True)
        dst = os.path.join(outdir, stem + ".pdf")
        if os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(p):
            skipped.append(stem)
            continue
        shutil.copy2(p, dst)
        os.chmod(dst, 0o644)
        placed.append((stem, revtxt))

    print("배치 %d건" % len(placed))
    for s, r in placed:
        print("   %-46s %s" % (s, r))
    if skipped:
        print("이미 있어 건너뜀 %d건" % len(skipped))
    if unknown:
        print("표에 없는 서식 %d건: %s" % (len(unknown), ", ".join(sorted(set(unknown)))))


if __name__ == "__main__":
    main()

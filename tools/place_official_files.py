# -*- coding: utf-8 -*-
"""정부·유관기관이 배포하는 서식 원본 파일을 official/ 에 배치한다.

원장이 농림축산검역본부·대한수의사회에서 직접 내려받아 전달한 파일이다.
협회가 만든 문서가 아니므로 forms/ 에 두지 않는다 — forms/ 는 전체 내려받기
압축 파일이 훑는 곳이라, 여기에 두면 협회 배포물에 섞여 들어간다.

파일명은 대괄호·괄호·공백을 없애 주소에서 문제가 되지 않게 바꾼다.
실행: python3 tools/place_official_files.py <내려받은_폴더>
"""
import os
import re
import shutil
import sys
import unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "official")

# (원본 파일명, 넣을 분류, 저장할 이름) — 원본 파일명은 확장자 없이 적는다
PLAN = [
    # ── 검역 · 출국 ──
    ("[별지 25] 예방접종 및 건강증명서(지정검역물의 검역방법 및 기준)",
     "01_검역출국", "예방접종및건강증명서_별지제25호서식"),

    # ── 마약류 관리 ──
    ("[별지 제24호서식] 의료용 마약류 저장시설 점검부(마약류 관리에 관한 법률 시행규칙)",
     "02_마약류", "의료용마약류저장시설점검부_별지제24호서식"),
    ("[별지 제25호서식] 사고마약류 발생 보고서(마약류 관리에 관한 법률 시행규칙)",
     "02_마약류", "사고마약류발생보고서_별지제25호서식"),
    ("[별지 제26호서식] 사고 마약류 등의 폐기 신청서(마약류 관리에 관한 법률 시행규칙)",
     "02_마약류", "사고마약류폐기신청서_별지제26호서식"),
    ("동물병원 마약류 취급·보고 시 유의사항(서식 포함)_260408",
     "02_마약류", "동물병원마약류취급보고유의사항_2026-04-08"),

    # ── 의약품 취급 ──
    ("[제16호의2서식] 인체용 의약품 출납대장(동물용 의약품등 취급규칙)",
     "03_의약품", "인체용의약품출납대장_제16호의2서식"),
    ("인체용 의약품 출납 대장 작성 가이드라인",
     "03_의약품", "인체용의약품출납대장_작성가이드라인"),
    ("동물병원내 인체용의약품 사용 시 유의사항",
     "03_의약품", "동물병원내_인체용의약품_사용유의사항"),
    ("동물병원내 동물용의약품 취급 시 유의사항",
     "03_의약품", "동물병원내_동물용의약품_취급유의사항"),
    ("동물병원의 국내 미허가 동물용의약품등 사용 시 유의사항_231011001",
     "03_의약품", "국내미허가_동물용의약품_사용유의사항_2023-10-11"),
    ("처방전 발급 거부의 정당한사유 관련 가이드라인",
     "03_의약품", "처방전_발급거부_정당한사유_가이드라인"),

    # ── 대한수의사회 권고 양식 ──
    ("[대한수의사회]진료비용 게시 권고 양식(24.12.20.개정)",
     "04_대한수의사회", "진료비용게시_권고양식_2024-12-20개정"),
    ("[대한수의사회]진료비용 게시 대상 진료행위 세부내용 산정 기준 참고 해설(24.12.20.개정)",
     "04_대한수의사회", "진료비용게시_산정기준_참고해설_2024-12-20개정"),
    ("[대한수의사회 권고 양식]수술등중대진료동의서_진료비용 동의 추가(230102)",
     "04_대한수의사회", "수술등중대진료동의서_진료비용동의추가_2023-01-02"),
    ("[대한수의사회 권고 양식]진찰등진료비용게시양식_행위 산정 해설안 추가(230102)",
     "04_대한수의사회", "진찰등진료비용게시양식_2023-01-02"),
    ("[대한수의사회]길고양이 중성화 수술 가이드라인_231228",
     "04_대한수의사회", "길고양이중성화수술_가이드라인_2023-12-28"),
    ("대한수의사회 승인양식 모음",
     "04_대한수의사회", "대한수의사회_승인양식모음"),

    # ── 운영 가이드라인 ──
    ("동물병원 관련 필수교육 안내_240219",
     "05_운영안내", "동물병원_필수교육안내_2024-02-19"),
    ("동물병원 방문진료(왕진) 관련 가이드라인(20.9.3)",
     "05_운영안내", "동물병원_방문진료_왕진_가이드라인_2020-09-03"),
    ("동물병원 진료부 및 처방내역공개 관련 가이드라인",
     "05_운영안내", "동물병원_진료부_처방내역공개_가이드라인"),
    ("(20230921)동물병원 진료비 부가가치세 확대 관련 가이드라인",
     "05_운영안내", "동물병원_진료비_부가가치세확대_가이드라인_2023-09-21"),
    ("첨부1.동물병원 진료비 부가세 면제 확대 안내문",
     "05_운영안내", "동물병원_진료비_부가세면제확대_안내문"),
    ("전체 동물병원의 적정 개설(운영 가이드라인 등)",
     "05_운영안내", "동물병원_적정개설_운영가이드라인"),
]

KEEP_EXT = (".pdf", ".hwp", ".hwpx", ".jpg", ".png")


def index(src):
    """내려받은 폴더를 훑어 (확장자 없는 이름) → [파일경로] 로 모은다."""
    found = {}
    for root, _, names in os.walk(src):
        if "_풀림" in root:
            continue
        for n in names:
            stem, ext = os.path.splitext(n)
            if ext.lower() not in KEEP_EXT:
                continue
            stem = unicodedata.normalize("NFC", stem)
            # "... (1)" 같은 중복본만 떼어 낸다. 앞의 공백을 반드시 요구해야
            # "(230102)" 처럼 파일명에 든 날짜·판번호를 잘라먹지 않는다.
            stem = re.sub(r" \((\d{1,2})\)$", "", stem)
            found.setdefault(stem, []).append(os.path.join(root, n))
    return found


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    if not src or not os.path.isdir(src):
        raise SystemExit("사용법: python3 tools/place_official_files.py <내려받은_폴더>")
    found = index(src)

    placed, missing = [], []
    for stem, cat, newname in PLAN:
        stem = unicodedata.normalize("NFC", stem)
        srcs = found.get(stem)
        if not srcs:
            missing.append(stem)
            continue
        outdir = os.path.join(OUT, cat)
        os.makedirs(outdir, exist_ok=True)
        for s in sorted(set(srcs)):
            ext = os.path.splitext(s)[1].lower()
            dst = os.path.join(outdir, newname + ext)
            if os.path.exists(dst) and os.path.getsize(dst) == os.path.getsize(s):
                continue
            shutil.copy2(s, dst)
            placed.append(os.path.relpath(dst, BASE))

    print("정부·유관기관 서식 배치 — %d개 파일" % len(placed))
    for p in sorted(placed):
        print("   ", p)
    if missing:
        print("  ⚠ 원본을 찾지 못한 항목 %d건" % len(missing))
        for m in missing:
            print("     -", m)


if __name__ == "__main__":
    main()

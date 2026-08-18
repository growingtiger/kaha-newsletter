# -*- coding: utf-8 -*-
"""양식 전체를 한 번에 내려받을 수 있는 압축 파일을 만든다.

회원병원이 문서를 컴퓨터에 받아 두고 쓰는 경우를 위한 것이다.
분류 폴더 구조를 그대로 유지하고, 안에 목록을 적은 안내문을 함께 넣는다.

**반드시 문서를 다시 만든 뒤 마지막에 실행한다.** 그러지 않으면 낱개로 받는
파일과 압축 파일의 내용이 어긋난다. (tools/build_all.sh 가 순서를 지켜 준다)

실행: python3 tools/make_forms_zip.py
"""
import json
import os
import zipfile

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMS = os.path.join(BASE, "forms")
OUT_DIR = os.path.join(BASE, "downloads")
OUT_NAME = "KAHA_양식모음_전체_한국동물병원협회.zip"

HEAD = """한국동물병원협회(KAHA) 회원병원 양식 모음
{date} 기준 · 양식 {count}종 (PDF + 워드 각 1개)

- PDF : 그대로 인쇄해서 쓰시는 용도입니다.
- 워드: 병원 사정에 맞게 고쳐 쓰시는 용도입니다.
- 모든 문서는 A4 한 장에 맞춰 만들었습니다.

문의 · 최신본 확인: 사단법인 한국동물병원협회

────────────────────────────────────────
수록 목록
────────────────────────────────────────
"""


def build():
    manifest = json.load(open(os.path.join(BASE, "forms.json"), encoding="utf-8"))
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, OUT_NAME)

    # 안내문 본문 — 분류별 목록
    lines = []
    for g in manifest["groups"]:
        lines.append("")
        lines.append("[%s]" % g["label"])
        for c in g["cats"]:
            lines.append("  %s (%d종)" % (c["label"], len(c["items"])))
            for it in c["items"]:
                lines.append("    - %s" % it["name"])

    # mtime 을 고정해 내용이 같으면 파일도 같게 만든다 (쓸데없는 재커밋 방지)
    date = os.environ.get("KAHA_BUILD_DATE", "")
    if not date:
        newest = max(os.path.getmtime(os.path.join(r, f))
                     for r, _, fs in os.walk(FORMS) for f in fs)
        import datetime
        date = datetime.date.fromtimestamp(newest).isoformat()

    readme = (HEAD.format(date=date, count=manifest["count"]) + "\n".join(lines) + "\n")

    files = []
    for root, _, names in os.walk(FORMS):
        for n in sorted(names):
            if n.endswith((".pdf", ".docx")):
                full = os.path.join(root, n)
                files.append((full, os.path.relpath(full, BASE)))
    files.sort(key=lambda x: x[1])

    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        info = zipfile.ZipInfo("KAHA_양식모음_안내.txt", (2026, 1, 1, 0, 0, 0))
        info.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(info, readme.encode("utf-8"))
        for full, rel in files:
            info = zipfile.ZipInfo(rel, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            with open(full, "rb") as f:
                z.writestr(info, f.read())

    size = os.path.getsize(out)
    print("압축 파일 생성 — %s" % OUT_NAME)
    print("  문서 %d개 · %.1f MB" % (len(files), size / 1024 / 1024))
    return {"path": "downloads/" + OUT_NAME, "bytes": size,
            "files": len(files), "date": date}


if __name__ == "__main__":
    info = build()
    # 화면에서 크기를 보여줄 수 있도록 forms.json 에 적어 둔다
    mp = os.path.join(BASE, "forms.json")
    m = json.load(open(mp, encoding="utf-8"))
    m["bundle"] = info
    with open(mp, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print("  forms.json 에 기록: %s" % info["path"])

# -*- coding: utf-8 -*-
"""질환별 동의서에 '질환에 대한 설명'(about)을 넣고 후유증 항목을 늘린다.

ASA 등급표를 마취 동의서로 옮기면서 생긴 자리를 내용으로 채우기 위한 스크립트.
내용은 tools/content/proc_about_*.py 에 나누어 두었다.
실행: python3 tools/apply_proc_about.py
"""
import json
import os
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "tools", "content"))

from proc_about_1 import D as D1          # noqa: E402
from proc_about_2 import D as D2          # noqa: E402
from proc_about_3 import D as D3          # noqa: E402
from proc_about_4 import D as D4          # noqa: E402
from proc_risk_fix import D as RISK_FIX   # noqa: E402
from proc_risk_fix2 import D as RISK_FIX2  # noqa: E402

CONTENT = {}
for part in (D1, D2, D3, D4):
    for k in part:
        if k in CONTENT:
            raise SystemExit("내용이 두 번 정의되었습니다: " + k)
    CONTENT.update(part)

# 기존 목록과 내용이 겹치던 항목은 다른 것으로 바꿔 쓴다
for _fix in (RISK_FIX, RISK_FIX2):
    for _k, _v in _fix.items():
        if _k not in CONTENT:
            raise SystemExit("교정 대상이 본문에 없습니다: " + _k)
        CONTENT[_k]["risk_add"] = _v


def main():
    path = os.path.join(BASE, "data", "procedures.json")
    rows = json.load(open(path, encoding="utf-8"))

    missing = []
    for e in rows:
        key = e["file"].replace("동의서_한국동물병원협회", "")
        c = CONTENT.get(key)
        if not c:
            missing.append(key)
            continue
        e["about"] = list(c["about"])
        # 이미 넣어 둔 항목이 있으면 다시 넣지 않는다 (여러 번 실행해도 같은 결과)
        for line in c["risk_add"]:
            if line not in e["risk"]:
                e["risk"].append(line)
    if missing:
        raise SystemExit("설명이 없는 양식 %d건: %s" % (len(missing), ", ".join(missing[:5])))

    json.dump(rows, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    open(path, "a", encoding="utf-8").write("\n")

    n_about = sum(1 for e in rows if e.get("about"))
    lens = sorted({len(e["risk"]) for e in rows})
    print("질환 설명 %d건 · 후유증 항목 %s개" % (n_about, "~".join(map(str, lens))))


if __name__ == "__main__":
    main()

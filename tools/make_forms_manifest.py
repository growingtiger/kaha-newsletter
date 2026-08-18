# -*- coding: utf-8 -*-
"""forms/ 를 훑어 양식 모음 화면이 읽는 forms.json 매니페스트를 만든다.

파일을 새로 추가하면 이 스크립트만 다시 돌리면 되고, 설명(desc)은
FORMS 표에 채워 둔다. 표에 없는 파일도 목록에는 나오되 설명이 비어 있으므로,
새 양식을 만들 때 여기에 한 줄 추가하는 것을 잊지 말 것.
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMS = os.path.join(BASE, "forms")

CATEGORIES = [
    ("01_수술마취", "수술 · 마취", "전신마취를 동반하는 수술과 시술 동의서"),
    ("02_입원응급", "입원 · 응급", "입원, 응급진료, 퇴원 단계에서 쓰는 서식"),
    ("03_임종사후", "임종 · 사후", "안락사와 사후 처리에 관한 동의서"),
    ("04_병원운영", "병원 운영", "개인정보, 초상권, 위임 등 진료 외 법적 서식"),
    ("05_부가서비스", "부가 서비스", "미용, 호텔링 등 진료 외 서비스 동의서"),
    ("06_진료기록", "진료 기록", "원내에서 쓰는 평가지 · 체크리스트"),
]

# 파일명(확장자 제외) → 표시 이름과 한 줄 설명
DESC = {
    "마취동의서_한국동물병원협회": (
        "수술등중대진료(마취) 동의서",
        "수의사법 제13조의2에 따른 법정 서면동의. ASA 등급표 포함."),
    "입원동의서_한국동물병원협회": (
        "입원 동의서",
        "입원 사유·비용·경과 보고·응급 상황 처리 방식을 합의합니다."),
    "퇴원안내문_한국동물병원협회": (
        "퇴원 안내문",
        "가정 투약과 관리, 재진 일정을 설명하고 그 사실을 남깁니다."),
    "마취전평가체크리스트_한국동물병원협회": (
        "마취 전 평가 · 모니터링 체크리스트",
        "마취 전 준비부터 회복기까지 원내 기록용 체크리스트."),
    "영양평가기록지_한국동물병원협회": (
        "영양 평가 · BCS / MCS 기록지",
        "모든 내원 환자의 영양 상태를 선별하고 기록합니다."),
}


def build():
    cats = []
    for folder, label, blurb in CATEGORIES:
        d = os.path.join(FORMS, folder)
        if not os.path.isdir(d):
            continue
        stems = sorted({os.path.splitext(f)[0] for f in os.listdir(d)
                        if f.endswith((".pdf", ".docx"))})
        items = []
        for stem in stems:
            name, desc = DESC.get(stem, (stem.replace("_한국동물병원협회", ""), ""))
            item = {"name": name, "desc": desc, "file": stem}
            for ext in ("pdf", "docx"):
                if os.path.exists(os.path.join(d, stem + "." + ext)):
                    item[ext] = "forms/%s/%s.%s" % (folder, stem, ext)
            items.append(item)
        if items:
            cats.append({"folder": folder, "label": label, "blurb": blurb, "items": items})
    return {"categories": cats,
            "count": sum(len(c["items"]) for c in cats)}


if __name__ == "__main__":
    data = build()
    with open(os.path.join(BASE, "forms.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("forms.json 생성 — 분류 %d개, 양식 %d종" % (len(data["categories"]), data["count"]))
    for c in data["categories"]:
        print("  %s: %s" % (c["label"], ", ".join(i["name"] for i in c["items"])))

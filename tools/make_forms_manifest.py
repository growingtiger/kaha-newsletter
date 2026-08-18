# -*- coding: utf-8 -*-
"""forms/ 를 훑어 양식 모음 화면이 읽는 forms.json 매니페스트를 만든다.

기본 서식은 아래 BASIC 표의 설명을 쓰고, 질환·처치별 동의서는
data/procedures.json 에서 진단명·시행 방법·검색어를 가져온다.
새 양식을 추가하면 이 스크립트만 다시 돌리면 된다.
"""
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORMS = os.path.join(BASE, "forms")
PROC_ROOT = "07_질환별동의서"
GUIDE_ROOT = "08_질환안내문"
ADMIN_ROOT = "09_노무행정"

BASIC_CATS = [
    ("01_수술마취", "수술 · 마취", "전신마취를 동반하는 수술과 시술 동의서"),
    ("02_입원응급", "입원 · 응급", "입원, 응급진료, 퇴원 단계에서 쓰는 서식"),
    ("03_임종사후", "임종 · 사후", "안락사와 사후 처리에 관한 동의서"),
    ("04_병원운영", "병원 운영", "개인정보, 초상권, 위임 등 진료 외 법적 서식"),
    ("05_부가서비스", "부가 서비스", "미용, 호텔링 등 진료 외 서비스 동의서"),
    ("06_진료기록", "진료 기록", "원내에서 쓰는 평가지 · 체크리스트"),
]

BASIC_DESC = {
    "마취동의서_한국동물병원협회": ("수술등중대진료(마취) 동의서",
        "수의사법 제13조의2에 따른 법정 서면동의. ASA 등급표 포함.", "마취 수술 동의 ASA 법정"),
    "입원동의서_한국동물병원협회": ("입원 동의서",
        "입원 사유·비용·경과 보고·응급 상황 처리 방식을 합의합니다.", "입원 비용 면회 응급"),
    "퇴원안내문_한국동물병원협회": ("퇴원 안내문",
        "가정 투약과 관리, 재진 일정을 설명하고 그 사실을 남깁니다.", "퇴원 투약 재진 안내"),
    "마취전평가체크리스트_한국동물병원협회": ("마취 전 평가 · 모니터링 체크리스트",
        "마취 전 준비부터 회복기까지 원내 기록용 체크리스트.", "마취 모니터링 체크리스트 기록"),
    "영양평가기록지_한국동물병원협회": ("영양 평가 · BCS / MCS 기록지",
        "모든 내원 환자의 영양 상태를 선별하고 기록합니다.", "영양 BCS MCS 체중 기록"),
}

PROC_CAT_LABEL = {
    "01_안과": "안과", "02_정형외과": "정형외과", "03_신경외과": "신경외과",
    "04_소화기": "소화기", "05_비뇨생식기": "비뇨생식기", "06_호흡기": "호흡기",
    "07_순환기": "순환기", "08_종양": "종양", "09_피부연부조직": "피부 · 연부조직",
    "10_치과": "치과", "11_이과": "이과", "12_응급중환자": "응급 · 중환자",
    "13_영상검사": "영상 · 검사", "14_내과처치": "내과 처치",
    "15_예방건강관리": "예방 · 건강관리", "16_임종완화": "임종 · 완화",
    "17_부가서비스": "부가 서비스",
}


GUIDE_CAT_LABEL = {
    "01_신장비뇨기": "신장 · 비뇨기", "02_내분비": "내분비", "03_심장": "심장",
    "04_소화기": "소화기", "05_간담췌": "간 · 담 · 췌", "06_호흡기": "호흡기",
    "07_피부": "피부", "08_안과": "안과", "09_근골격": "근골격", "10_신경": "신경",
    "11_종양": "종양", "12_감염": "감염", "13_고양이": "고양이", "14_노령": "노령",
    "15_행동": "행동", "16_응급": "응급", "17_생활관리": "생활 관리",
}

ADMIN_CAT_LABEL = {
    "01_채용근로계약": "채용 · 근로계약", "02_근태휴가": "근태 · 휴가",
    "03_인사관리": "인사 관리", "04_퇴직": "퇴직",
    "05_병원운영": "병원 운영", "06_안전보건": "안전 · 보건",
}


def files_in(rel):
    d = os.path.join(FORMS, rel)
    if not os.path.isdir(d):
        return []
    return sorted({os.path.splitext(f)[0] for f in os.listdir(d)
                   if f.endswith((".pdf", ".docx"))})


def item(rel, stem, name, desc, kw):
    it = {"name": name, "desc": desc, "kw": kw}
    for ext in ("pdf", "docx"):
        if os.path.exists(os.path.join(FORMS, rel, stem + "." + ext)):
            it[ext] = "forms/%s/%s.%s" % (rel, stem, ext)
    return it


def build():
    groups = []

    basic = []
    for folder, label, blurb in BASIC_CATS:
        items = []
        for stem in files_in(folder):
            name, desc, kw = BASIC_DESC.get(
                stem, (stem.replace("_한국동물병원협회", ""), "", ""))
            items.append(item(folder, stem, name, desc, kw))
        if items:
            basic.append({"folder": folder, "label": label, "blurb": blurb, "items": items})
    if basic:
        groups.append({"key": "basic", "label": "기본 서식",
                       "blurb": "모든 병원에서 공통으로 쓰는 동의서와 기록지입니다.",
                       "cats": basic})

    def add_group(key, label, blurb, root, path_json, labels, name_key, desc_fn):
        jp = os.path.join(BASE, "data", path_json)
        if not os.path.exists(jp):
            return
        rows = json.load(open(jp, encoding="utf-8"))
        by_dir = {}
        for e in rows:
            by_dir.setdefault(e["dir"], []).append(e)
        cats = []
        for folder in sorted(by_dir):
            items = []
            for e in sorted(by_dir[folder], key=lambda x: x[name_key]):
                rel = "%s/%s" % (root, folder)
                items.append(item(rel, e["file"], desc_fn(e)[0],
                                  desc_fn(e)[1], e.get("kw", "")))
            cats.append({"folder": folder, "label": labels.get(folder, folder),
                         "blurb": "", "items": items})
        if cats:
            groups.append({"key": key, "label": label, "blurb": blurb, "cats": cats})

    add_group("proc", "질환 · 처치별 동의서",
              "진단명과 시행 방법이 미리 채워진 동의서입니다. 빈 줄에 병원별 항목을 더해 쓰십시오.",
              PROC_ROOT, "procedures.json", PROC_CAT_LABEL, "title",
              lambda e: (e["title"], "진단명 " + e["dx"]))

    add_group("guide", "질환 안내문 (보호자 설명용)",
              "보호자에게 건네는 설명 자료입니다. 증상·치료·가정 관리·응급 신호를 한 장에 담았습니다.",
              GUIDE_ROOT, "diseases.json", GUIDE_CAT_LABEL, "name",
              lambda e: (e["name"] + " 안내문", e.get("eng", "")))

    add_group("admin", "노무 · 병원 행정 서식",
              "근로계약, 근태·휴가, 인사, 퇴직, 병원 운영, 안전보건 서식입니다.",
              ADMIN_ROOT, "admin_forms.json", ADMIN_CAT_LABEL, "title",
              lambda e: (e["title"], e.get("sub", "")))

    n = sum(len(c["items"]) for g in groups for c in g["cats"])
    return {"groups": groups, "count": n}


if __name__ == "__main__":
    data = build()
    with open(os.path.join(BASE, "forms.json"), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
        f.write("\n")
    print("forms.json 생성 — 양식 %d종" % data["count"])
    for g in data["groups"]:
        print("  [%s] 분류 %d개 · %d종" % (g["label"], len(g["cats"]),
                                       sum(len(c["items"]) for c in g["cats"])))

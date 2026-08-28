# -*- coding: utf-8 -*-
"""인스타그램 카드뉴스(1080×1080) 생성 — 발행 안내 전용 1장(2026-08-23 개편).

인스타그램은 회원병원뿐 아니라 보호자 등 일반 대중도 볼 수 있으므로,
카드에는 조문·수치 등 소식지 세부 내용을 싣지 않는다. "오늘 이런 주제로
발행되었다"는 안내와 협회 홈페이지 링크만 한 장에 담는다. 세부 내용은
홈페이지에서 확인하도록 유도한다.

tools/cards_data.json의 호별 데이터(제목·부제)를 읽어 cards/<날짜>/ 아래에
안내 카드 1장, caption.txt를 만든다.
디자인은 소식지·양식과 같은 브랜드 팔레트(KAHA 블루 #035293)를 쓴다.
필요: Pillow, 시스템 폰트 fonts-nanum.
"""
import datetime
import json
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "tools", "cards_data.json")
LOGO_PATH = os.path.join(BASE, "assets", "kaha-logo.png")
OUT_ROOT = os.path.join(BASE, "cards")
SITE_URL = "https://kaha.or.kr/"

SIZE = 1080
CONTENT_MAX_Y = 946        # 하단 푸터 영역 침범 방지 한계선
OVERFLOW = []              # 넘친 카드 기록 (생성 후 일괄 보고)
BLUE = (3, 82, 147)
BLUE_DK = (2, 58, 104)
BLUE_LT = (213, 228, 242)
BLUE_BG = (237, 243, 250)
INK = (35, 25, 22)
GREY = (107, 118, 131)
WHITE = (255, 255, 255)

FONT_DIR = os.path.join(BASE, "assets", "fonts")
NANUM = "/usr/share/fonts/truetype/nanum"
WEIGHTS = {
    "regular": "Pretendard-Regular.otf",
    "medium": "Pretendard-Medium.otf",
    "semibold": "Pretendard-SemiBold.otf",
    "bold": "Pretendard-Bold.otf",
    "extrabold": "Pretendard-ExtraBold.otf",
}
NANUM_FALLBACK = {"regular": "NanumGothic.ttf", "medium": "NanumGothic.ttf",
                  "semibold": "NanumGothicBold.ttf", "bold": "NanumGothicBold.ttf",
                  "extrabold": "NanumGothicBold.ttf"}

def F(weight, size):
    p = os.path.join(FONT_DIR, WEIGHTS[weight])
    if not os.path.exists(p):
        p = os.path.join(NANUM, NANUM_FALLBACK[weight])
    return ImageFont.truetype(p, size)

THEMES = {1: "월요일 · 진료 가이드라인", 2: "화요일 · 노무·인사",
          3: "수요일 · 서식·양식", 4: "목요일 · 경영·세무", 5: "금요일 · 법규·정책"}
DOW_SHORT = {1: "월", 2: "화", 3: "수", 4: "목", 5: "금"}
THEME_SHORT = {1: "진료 가이드라인", 2: "노무·인사", 3: "서식·양식",
               4: "경영·세무", 5: "법규·정책"}

logo_src = Image.open(LOGO_PATH).convert("RGBA")

def logo(h):
    w = int(h * logo_src.width / logo_src.height)
    return logo_src.resize((w, h), Image.LANCZOS)

def wrap(draw, text, font, maxw):
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=font) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

def draw_lines(draw, lines, x, y, font, fill, leading, center=False):
    for ln in lines:
        xx = x
        if center:
            w = draw.textlength(ln, font=font)
            xx = (SIZE - w) / 2
        draw.text((xx, y), ln, font=font, fill=fill)
        y += leading
    return y

def base_card():
    img = Image.new("RGB", (SIZE, SIZE), WHITE)
    return img, ImageDraw.Draw(img)

def footer(img, draw):
    draw.rectangle([0, SIZE - 14, SIZE, SIZE], fill=BLUE)
    draw.text((80, SIZE - 74), "KAHA 회원병원 실무 소식지", font=F("semibold", 26), fill=GREY)

def chip(draw, x, y, text, font, pad=18):
    w = draw.textlength(text, font=font)
    h = font.size + pad
    draw.rounded_rectangle([x, y, x + w + pad * 2, y + h + 6], radius=(h + 6) // 2, fill=BLUE)
    draw.text((x + pad, y + (h + 6 - font.size) // 2 - 2), text, font=font, fill=WHITE)
    return y + h + 6

def caption_for(date, data, dow):
    theme = THEME_SHORT[dow]
    md = "%d/%d" % (int(date[5:7]), int(date[8:10]))
    return (
        "[KAHA 회원병원 실무 소식지] %s (%s %s · %s)\n\n"
        "오늘 소식지 주제: %s\n\n"
        "회원병원 실무 소식지 전문은 협회 홈페이지에서 확인하실 수 있습니다.\n"
        "%s\n\n"
        "#KAHA #한국동물병원협회 #수의사 #동물병원 #동물병원실무"
    ) % (data["title"], md, DOW_SHORT[dow], theme, data["subtitle"], SITE_URL)

def make_set(date, data):
    outdir = os.path.join(OUT_ROOT, date)
    os.makedirs(outdir, exist_ok=True)
    dow = datetime.date(*map(int, date.split("-"))).isoweekday()
    theme = THEMES.get(dow, "")

    # ── 1장: 발행 안내 + 홈페이지 유도 (세부 내용 없음) ──
    img, d = base_card()
    img.paste(logo(64), (80, 80), logo(64))
    d.rectangle([80, 184, SIZE - 80, 190], fill=BLUE)
    chip(d, 80, 250, theme, F("semibold", 32))
    d.text((80, 336), "오늘의 회원병원 실무 소식지가 발행되었습니다",
           font=F("bold", 32), fill=BLUE_DK)
    tf = F("extrabold", 58)
    y = draw_lines(d, wrap(d, data["title"], tf, 920), 80, 400, tf, INK, 78)
    sf = F("regular", 36)
    y = draw_lines(d, wrap(d, data["subtitle"], sf, 920), 80, y + 12, sf, GREY, 50)

    y += 56
    d.rectangle([80, y, SIZE - 80, y + 3], fill=BLUE_LT)
    y += 54

    d.text((80, y), "자세한 내용은 협회 홈페이지에서 확인하세요",
           font=F("bold", 38), fill=BLUE_DK)
    y += 74
    box_w, box_h = 560, 88
    d.rounded_rectangle([80, y, 80 + box_w, y + box_h], radius=box_h // 2, fill=BLUE)
    uf = F("bold", 38)
    d.text((80 + 40, y + (box_h - uf.size) / 2 - 4), SITE_URL, font=uf, fill=WHITE)
    y += box_h + 40
    df = F("regular", 30)
    y = draw_lines(d, wrap(d, "회원병원을 위한 실무 소식지 전문과 지난 호 전체는 협회 홈페이지에서 볼 수 있습니다.", df, 920),
                   80, y, df, GREY, 44)

    if y > CONTENT_MAX_Y:
        OVERFLOW.append("%s cover: y=%d (한계 %d)" % (date, y, CONTENT_MAX_Y))
    footer(img, d)
    img.save(os.path.join(outdir, "1-cover.png"))

    for stale in ("2-point1.png", "2-info.png", "3-point2.png", "4-point3.png", "5-outro.png"):
        p = os.path.join(outdir, stale)
        if os.path.exists(p):
            os.remove(p)

    with open(os.path.join(outdir, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(caption_for(date, data, dow) + "\n")

if __name__ == "__main__":
    import sys
    data = json.load(open(DATA, encoding="utf-8"))
    dates = sys.argv[1:] or sorted(data.keys())
    for date in dates:
        make_set(date, data[date])
        print("생성:", date)
    if OVERFLOW:
        print("\n⚠ 넘침 경고 %d건:" % len(OVERFLOW))
        for o in OVERFLOW:
            print("  -", o)
        raise SystemExit(1)
    print("넘침 없음 — 전 카드 안전 영역 내")

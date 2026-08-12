# -*- coding: utf-8 -*-
"""인스타그램 카드뉴스(1080×1080) 생성.

tools/cards_data.json의 호별 데이터(제목·부제·포인트 3개[머리글, 본문, 근거]·캡션)를 읽어
cards/<날짜>/ 아래에 표지·포인트 3장·요약 카드와 caption.txt를 만든다.
- 표지: 제목 + 이번 호 핵심 3줄 미리보기
- 포인트 카드: 번호 칩 + 머리글 + 본문 + 근거/출처 줄
- 마무리: 오늘의 핵심 정리(3줄 재수록) + 안내
디자인은 소식지·양식과 같은 브랜드 팔레트(KAHA 블루 #035293)를 쓴다.
필요: Pillow, 시스템 폰트 fonts-nanum.
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "tools", "cards_data.json")
LOGO_PATH = os.path.join(BASE, "assets", "kaha-logo.png")
OUT_ROOT = os.path.join(BASE, "cards")

SIZE = 1080
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

def draw_lines(draw, lines, x, y, font, fill, leading):
    for ln in lines:
        draw.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y

def base_card():
    img = Image.new("RGB", (SIZE, SIZE), WHITE)
    return img, ImageDraw.Draw(img)

def footer(img, draw, date, page=None, total=None):
    draw.rectangle([0, SIZE - 14, SIZE, SIZE], fill=BLUE)
    draw.text((80, SIZE - 74), "KAHA 회원병원 실무 소식지", font=F("semibold", 26), fill=GREY)
    w = draw.textlength(date, font=F("regular", 26))
    draw.text((SIZE - 80 - w, SIZE - 74), date, font=F("regular", 26), fill=GREY)
    if page is not None:
        cx = SIZE // 2 - (total - 1) * 18
        for i in range(total):
            r = 7
            fill = BLUE if (i + 1) == page else BLUE_LT
            draw.ellipse([cx - r, SIZE - 66 - r, cx + r, SIZE - 66 + r], fill=fill)
            cx += 36

def chip(draw, x, y, text, font, pad=18):
    w = draw.textlength(text, font=font)
    h = font.size + pad
    draw.rounded_rectangle([x, y, x + w + pad * 2, y + h + 6], radius=(h + 6) // 2, fill=BLUE)
    draw.text((x + pad, y + (h + 6 - font.size) // 2 - 2), text, font=font, fill=WHITE)
    return y + h + 6

def make_set(date, data):
    outdir = os.path.join(OUT_ROOT, date)
    os.makedirs(outdir, exist_ok=True)
    import datetime
    dow = datetime.date(*map(int, date.split("-"))).isoweekday()
    theme = THEMES.get(dow, "")
    points = data["points"]
    total = 2 + len(points)

    # ── 1. 표지: 제목 + 이번 호 핵심 미리보기 ──
    img, d = base_card()
    img.paste(logo(64), (80, 80), logo(64))
    d.rectangle([80, 184, SIZE - 80, 190], fill=BLUE)
    chip(d, 80, 250, theme, F("semibold", 32))
    tf = F("extrabold", 66)
    y = draw_lines(d, wrap(d, data["title"], tf, 920), 80, 356, tf, INK, 88)
    sf = F("regular", 40)
    y = draw_lines(d, wrap(d, data["subtitle"], sf, 920), 80, y + 10, sf, GREY, 56)
    y = max(y + 34, 610)
    d.text((80, y), "이번 호 핵심", font=F("bold", 30), fill=BLUE)
    y += 54
    bf = F("semibold", 36)
    for head, _, _ in points:
        d.ellipse([84, y + 16, 100, y + 32], fill=BLUE)
        for ln in wrap(d, head, bf, 860):
            d.text((124, y), ln, font=bf, fill=INK)
            y += 54
        y += 12
    hint = "넘겨서 자세히 보기  →"
    hw = d.textlength(hint, font=F("semibold", 30))
    d.text((SIZE - 80 - hw, 908), hint, font=F("semibold", 30), fill=BLUE)
    footer(img, d, date, page=1, total=total)
    img.save(os.path.join(outdir, "1-cover.png"))

    # ── 2~4. 포인트 카드: 번호 칩 + 머리글 + 본문 + 근거 줄 ──
    for i, point in enumerate(points, start=1):
        head, body = point[0], point[1]
        detail = point[2] if len(point) > 2 else None
        img, d = base_card()
        img.paste(logo(48), (80, 72), logo(48))
        tw = d.textlength(theme, font=F("regular", 28))
        d.text((SIZE - 80 - tw, 84), theme, font=F("regular", 28), fill=GREY)
        d.rectangle([80, 160, SIZE - 80, 164], fill=BLUE_LT)
        # 번호 칩
        num = "%02d" % i
        nf = F("bold", 42)
        d.rounded_rectangle([80, 208, 196, 280], radius=16, fill=BLUE)
        nw = d.textlength(num, font=nf)
        d.text((80 + (116 - nw) / 2, 220), num, font=nf, fill=WHITE)
        # 머리글
        hf = F("bold", 56)
        y = draw_lines(d, wrap(d, head, hf, 920), 80, 318, hf, BLUE_DK, 76)
        # 본문
        bf2 = F("regular", 40)
        y = draw_lines(d, wrap(d, body, bf2, 920), 80, y + 22, bf2, INK, 62)
        # 근거/출처 줄
        if detail:
            y += 30
            df = F("regular", 32)
            dlines = wrap(d, detail, df, 880)
            bar_h = len(dlines) * 46 + 8
            d.rectangle([80, y, 88, y + bar_h], fill=BLUE)
            draw_lines(d, dlines, 112, y + 4, df, GREY, 46)
        footer(img, d, date, page=i + 1, total=total)
        img.save(os.path.join(outdir, "%d-point%d.png" % (i + 1, i)))

    # ── 5. 마무리: 오늘의 핵심 정리 ──
    img, d = base_card()
    img.paste(logo(64), (80, 80), logo(64))
    d.rectangle([80, 184, SIZE - 80, 190], fill=BLUE)
    d.text((80, 244), "오늘의 핵심 정리", font=F("extrabold", 48), fill=BLUE_DK)
    y = 356
    kf = F("semibold", 38)
    vf = F("regular", 30)
    for idx, point in enumerate(points, start=1):
        d.ellipse([80, y + 2, 124, y + 46], fill=BLUE)
        d.line([(91, y + 25), (100, y + 34), (114, y + 14)], fill=WHITE, width=5, joint="curve")
        yy = y
        for ln in wrap(d, point[0], kf, 820):
            d.text((148, yy), ln, font=kf, fill=INK)
            yy += 54
        if len(point) > 2:
            for ln in wrap(d, point[2], vf, 820):
                d.text((148, yy), ln, font=vf, fill=GREY)
                yy += 44
        y = yy + 30
    d.rectangle([80, y + 6, SIZE - 80, y + 9], fill=BLUE_LT)
    y += 44
    cf = F("bold", 40)
    d.text((80, y), "전체 내용 · 양식 PDF · 워드 파일은 소식지에서", font=cf, fill=INK)
    d.text((80, y + 62), "프로필 링크 · 매 평일 발행 · 한국동물병원협회 정책기획위원회",
           font=F("regular", 30), fill=GREY)
    footer(img, d, date, page=total, total=total)
    img.save(os.path.join(outdir, "%d-outro.png" % total))

    with open(os.path.join(outdir, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(data["caption"] + "\n")

if __name__ == "__main__":
    import sys
    data = json.load(open(DATA, encoding="utf-8"))
    dates = sys.argv[1:] or sorted(data.keys())
    for date in dates:
        make_set(date, data[date])
        print("생성:", date)

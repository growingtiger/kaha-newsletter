# -*- coding: utf-8 -*-
"""인스타그램 카드뉴스(1080×1080) 생성.

tools/cards_data.json의 호별 데이터(제목·포인트 3개·캡션)를 읽어
cards/<날짜>/ 아래에 표지·포인트 3장·마무리 카드와 caption.txt를 만든다.
디자인은 소식지·양식 PDF와 같은 브랜드 팔레트(KAHA 블루 #035293)를 쓴다.
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

FD = "/usr/share/fonts/truetype/nanum"
def F(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)

THEMES = {0: None, 1: "월요일 · 진료 가이드라인", 2: "화요일 · 노무·인사",
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
    draw.text((80, SIZE - 74), "KAHA 회원병원 실무 소식지", font=F("NanumSquareB.ttf", 26), fill=GREY)
    dtxt = date
    w = draw.textlength(dtxt, font=F("NanumSquareR.ttf", 26))
    draw.text((SIZE - 80 - w, SIZE - 74), dtxt, font=F("NanumSquareR.ttf", 26), fill=GREY)
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
    total = 2 + len(data["points"])

    # ── 표지 ──
    img, d = base_card()
    img.paste(logo(64), (80, 80), logo(64))
    d.rectangle([80, 184, SIZE - 80, 190], fill=BLUE)
    chip(d, 80, 268, theme, F("NanumSquareB.ttf", 34))
    tf = F("NanumSquareB.ttf", 76)
    y = draw_lines(d, wrap(d, data["title"], tf, 920), 80, 396, tf, INK, 100)
    sf = F("NanumSquareR.ttf", 42)
    draw_lines(d, wrap(d, data["subtitle"], sf, 920), 80, y + 18, sf, GREY, 60)
    hint = "넘겨서 핵심 보기  →"
    hw = d.textlength(hint, font=F("NanumSquareB.ttf", 32))
    d.text((SIZE - 80 - hw, 880), hint, font=F("NanumSquareB.ttf", 32), fill=BLUE)
    footer(img, d, date, page=1, total=total)
    img.save(os.path.join(outdir, "1-cover.png"))

    # ── 포인트 카드 ──
    for i, (head, body) in enumerate(data["points"], start=1):
        img, d = base_card()
        img.paste(logo(48), (80, 72), logo(48))
        ttxt = theme
        tw = d.textlength(ttxt, font=F("NanumSquareR.ttf", 28))
        d.text((SIZE - 80 - tw, 84), ttxt, font=F("NanumSquareR.ttf", 28), fill=GREY)
        d.rectangle([80, 160, SIZE - 80, 164], fill=BLUE_LT)
        d.text((74, 210), "%02d" % i, font=F("NanumSquareB.ttf", 170), fill=BLUE_LT)
        hf = F("NanumSquareB.ttf", 62)
        y = draw_lines(d, wrap(d, head, hf, 920), 80, 430, hf, BLUE_DK, 84)
        bf = F("NanumSquareR.ttf", 42)
        draw_lines(d, wrap(d, body, bf, 920), 80, y + 26, bf, INK, 66)
        footer(img, d, date, page=i + 1, total=total)
        img.save(os.path.join(outdir, "%d-point%d.png" % (i + 1, i)))

    # ── 마무리 카드 ──
    img, d = base_card()
    lg = logo(96)
    img.paste(lg, ((SIZE - lg.width) // 2, 330), lg)
    cf = F("NanumSquareB.ttf", 56)
    for j, ln in enumerate(["전체 내용과 양식 PDF는", "소식지에서 확인하세요"]):
        w = d.textlength(ln, font=cf)
        d.text(((SIZE - w) // 2, 520 + j * 84), ln, font=cf, fill=INK)
    sub = "프로필 링크 · 매 평일 발행"
    sf2 = F("NanumSquareR.ttf", 38)
    w = d.textlength(sub, font=sf2)
    d.text(((SIZE - w) // 2, 720), sub, font=sf2, fill=GREY)
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

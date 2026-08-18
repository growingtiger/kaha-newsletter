// 질환 안내문 · 노무행정 서식 워드(.docx) 생성.
// PDF(make_disease_guides.py / make_admin_forms.py)와 같은 구성이며,
// 내용 길이에 맞춰 구획 높이를 자동 계산해 A4 한 장을 보장한다.
// 실행: node tools/make_guide_admin_docx.js
const fs = require("fs");
const path = require("path");
const S = require("./form_style_docx");
const {
  TOTAL, USABLE, AlignmentType, para, cell, plainCell, table, gap,
  titleBlock, infoTable, sec, bulletLines, fieldTable, closing, signRow, buildDoc,
} = S;

const BASE = path.dirname(__dirname);
const mm = (v) => Math.round(v * 56.7);
const LB = 1928;
const IW = TOTAL - LB - 240;

const L = mm(26), M = mm(30);
const V = Math.floor((TOTAL - L - 2 * M) / 2);
const IN_W = [L, M, V, M, TOTAL - L - 2 * M - V];


// 구획 높이 = 내용과 라벨 중 더 큰 쪽. 라벨이 여러 줄이면 라벨이 기준이 된다.
function secH(label, contentH) {
  const labelLines = String(label).split("\n").length;
  return Math.max(contentH, labelLines * 250) + 150;
}

function totalHeight(body) {
  return body.reduce((s, el) => s + (typeof el.__h === "number" ? el.__h : 0), 0) + 120;
}

// ── 질환 안내문 ────────────────────────────────────────────────────
const G_SUB = "이 안내문은 보호자께 반려동물의 질환을 설명해 드리기 위한 자료입니다.";
const G_FOOT = "이 안내문은 일반적인 설명이며, 실제 경과와 치료 방침은 개체 상태에 따라 달라집니다. 궁금한 점은 언제든 담당 수의사에게 물어봐 주십시오.";

function twoBox(a, b, h) {
  const half = Math.floor(TOTAL / 2) - 40;
  const lw = mm(24);
  return table([lw, half - lw, 80, lw, TOTAL - half - lw - 80], [[
    cell("진 단 명", { w: lw, label: true, size: 16 }),
    cell(a, { w: half - lw, size: 16 }),
    plainCell([para("", { size: 2 })], { w: 80 }),
    cell("영문 · 이명", { w: lw, label: true, size: 15 }),
    cell(b, { w: TOTAL - half - lw - 80, size: 15 }),
  ]], h);
}

function guideDoc(e, o) {
  const { memo, g, lineH, infoH, tail } = o;
  const bh = (label, items) => secH(label, items.length * lineH);
  const title = e.name + " 안내문";
  return [].concat(
    titleBlock(title, G_SUB, title.length < 16 ? 40 : 32),
    [
      infoTable([
        ["보호자", [["성명", "", "연락처", ""]]],
        ["반려동물", [["이름", "", "종 / 품종", ""], ["연령 / 체중", "", "진단일", ""]]],
        ["수의사", [["동물병원명", "", "담당 수의사", ""]]],
      ], IN_W, infoH),
      gap(g), twoBox(e.name, e.eng, mm(9)), gap(g),
      sec("어떤 질환인가요", bulletLines(e.what, { size: 16, lineH }), { height: bh("어떤 질환인가요", e.what) }), gap(g),
      sec("이런 증상이\n나타납니다", bulletLines(e.sign, { size: 16, lineH }), { height: bh("이런 증상이\n나타납니다", e.sign) }), gap(g),
      sec("어떻게 진단하고\n치료하나요", bulletLines(e.tx, { size: 16, lineH }), { height: bh("어떻게 진단하고\n치료하나요", e.tx) }), gap(g),
      sec("집에서 이렇게\n관리해 주세요", bulletLines(e.home, { size: 16, lineH }), { height: bh("집에서 이렇게\n관리해 주세요", e.home) }), gap(g),
      sec("이럴 때는\n바로 연락 주세요", bulletLines(e.warn, { size: 16, lineH }), { height: bh("이럴 때는\n바로 연락 주세요", e.warn) }), gap(g),
      sec("담당 수의사\n메모", bulletLines(Array(memo).fill(" "), { size: 16, lineH }),
        { height: secH("담당 수의사\n메모", memo * lineH) }),
      gap(150 + tail),
      table([TOTAL], [[plainCell(closing(G_FOOT),
        { w: TOTAL, margins: { top: 0, bottom: 0, left: 0, right: 0 } })]], mm(11)),
      gap(150),
      signRow(["보호자", "설명자"]),
    ]);
}

// ── 노무·행정 서식 ─────────────────────────────────────────────────
function renderBlock(b, rowH, lineH, scale) {
  if (b.t === "fields") {
    const lw = mm(b.lw || 30);
    const vw = Math.floor((IW - lw) / 3);
    const rows = b.rows.map((r) => [
      { text: r[0], label: true }, r[1] || "", null, null,
    ]);
    const hs = b.rows.map((r) => Math.round(rowH * (r[2] || 1)));
    return sec(b.label, [fieldTable(rows, [lw, vw, vw, IW - lw - 2 * vw], hs)],
      { height: secH(b.label, hs.reduce((a, c) => a + c, 0) - 20) });
  }
  if (b.t === "text") {
    const n = Math.max(1, Math.round((b.lines || 5) * scale));
    return sec(b.label, bulletLines(Array(n).fill(" "), { size: 16, lineH, marker: "" }),
      { height: secH(b.label, n * lineH) });
  }
  const items = b.items;
  const marker = b.t === "checks" ? "" : "· ";
  return sec(b.label, bulletLines(items, { size: 16, lineH, marker }),
    { height: secH(b.label, items.length * lineH) });
}

function adminDoc(e, o) {
  const { rowH, g, lineH, scale, tail } = o;
  const body = [].concat(
    titleBlock(e.title, e.sub || "", e.title.length < 14 ? 40 : 32),
    e.blocks.flatMap((b) => [renderBlock(b, rowH, lineH, scale), gap(g)]),
    [gap(60 + tail)],
    e.decl ? [table([TOTAL], [[plainCell(closing(e.decl),
      { w: TOTAL, margins: { top: 0, bottom: 0, left: 0, right: 0 } })]], mm(9)), gap(140)] : [],
    [signRow(e.sign || ["작성자"])]);
  return body;
}

(async () => {
  let made = 0;
  const failed = [];

  const guides = JSON.parse(fs.readFileSync(path.join(BASE, "data", "diseases.json"), "utf8"));
  const gOpts = [
    { memo: 3, g: 136, lineH: 250 }, { memo: 2, g: 136, lineH: 250 },
    { memo: 2, g: 110, lineH: 235 }, { memo: 1, g: 110, lineH: 225 },
    { memo: 0, g: 90, lineH: 215 },
  ];
  for (const e of guides) {
    let o = Object.assign({ infoH: mm(7.6), tail: 0 }, gOpts[gOpts.length - 1]);
    for (const t of gOpts) {
      const cand = Object.assign({ infoH: mm(7.6), tail: 0 }, t);
      if (totalHeight(guideDoc(e, cand)) <= USABLE) { o = cand; break; }
    }
    while (o.memo < 5) {
      const t = Object.assign({}, o, { memo: o.memo + 1 });
      if (totalHeight(guideDoc(e, t)) > USABLE - mm(10)) break;
      o = t;
    }
    let room = USABLE - totalHeight(guideDoc(e, o));
    o.infoH = Math.min(mm(12), mm(7.6) + Math.max(0, Math.floor(room * 0.5 / 4)));
    room = USABLE - totalHeight(guideDoc(e, o));
    if (room > 30) o.tail = room - 20;
    try {
      await buildDoc(e.name + " 안내문", guideDoc(e, o),
        path.join("08_질환안내문", e.dir, e.file + ".docx"));
      made += 1;
    } catch (err) { failed.push(e.name + " — " + err.message.split("\n")[0]); }
  }

  const admins = JSON.parse(fs.readFileSync(path.join(BASE, "data", "admin_forms.json"), "utf8"));
  const aOpts = [
    { rowH: mm(8), g: 148, lineH: 250, scale: 1.0 },
    { rowH: mm(7.4), g: 125, lineH: 240, scale: 1.0 },
    { rowH: mm(7), g: 110, lineH: 230, scale: 0.8 },
    { rowH: mm(6.6), g: 100, lineH: 220, scale: 0.7 },
    { rowH: mm(6.2), g: 90, lineH: 210, scale: 0.55 },
    { rowH: mm(6), g: 80, lineH: 200, scale: 0.45 },
  ];
  for (const e of admins) {
    let o = Object.assign({ tail: 0 }, aOpts[aOpts.length - 1]);
    for (const t of aOpts) {
      const cand = Object.assign({ tail: 0 }, t);
      if (totalHeight(adminDoc(e, cand)) <= USABLE) { o = cand; break; }
    }
    for (const extra of [mm(3), mm(2), mm(1), 0]) {
      const t = Object.assign({}, o, { rowH: o.rowH + extra });
      if (totalHeight(adminDoc(e, t)) <= USABLE) { o = t; break; }
    }
    const room = USABLE - totalHeight(adminDoc(e, o));
    if (room > 30) o.tail = room - 20;
    try {
      await buildDoc(e.title, adminDoc(e, o),
        path.join("09_노무행정", e.dir, e.file + ".docx"));
      made += 1;
    } catch (err) { failed.push(e.title + " — " + err.message.split("\n")[0]); }
  }

  console.log(`질환 안내문 · 노무행정 워드 ${made}건 생성`);
  if (failed.length) {
    console.log(`  ⚠ 실패 ${failed.length}건`);
    failed.slice(0, 6).forEach((f) => console.log("     " + f));
    process.exit(1);
  }
})();

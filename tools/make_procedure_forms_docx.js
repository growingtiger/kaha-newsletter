// 질환·처치별 동의서 워드(.docx) 생성 — data/procedures.json 을 읽어 한 건씩 만든다.
// PDF(tools/make_procedure_forms.py)와 같은 구성이며, 내용 길이에 맞춰 구획 높이를
// 자동 계산해 A4 한 장을 보장한다. 실행: node tools/make_procedure_forms_docx.js
const fs = require("fs");
const path = require("path");
const S = require("./form_style_docx");
const {
  TOTAL, USABLE, LABEL_BG, AlignmentType, para, cell, plainCell, table, gap,
  titleBlock, infoTable, sec, bulletLines, asaTable, closing, signRow, buildDoc,
} = S;

const BASE = path.dirname(__dirname);
const ROOT = "07_질환별동의서";
const mm = (v) => Math.round(v * 56.7);
const LB = 1928;
const CW = TOTAL - LB;
const IW = CW - 240;

const L = mm(26), M = mm(30);
const V = Math.floor((TOTAL - L - 2 * M) / 2);
const IN_W = [L, M, V, M, TOTAL - L - 2 * M - V];

const LEGAL = "본 동의서는 「수의사법」 제13조의2 및 같은 법 시행규칙 제13조의3에 따라 작성되었습니다.";
const DECL = "「수의사법」 제13조의2 및 같은 법 시행규칙 제13조의3에 따라 위와 같이 수의사로부터 진료의 필요성 · 방법 · 내용과 전형적으로 예상되는 후유증 및 부작용에 관한 설명을 충분히 듣고 이해하였습니다. 이에 위 진료의 시행에 동의하며, 시행 과정에서 필요한 수의학적 판단과 처리를 담당 수의사에게 위임합니다.";

/** 진단명 · 시행 방법을 나란히 놓는 두 칸 */
function twoBox(dx, proc, h) {
  const half = Math.floor(TOTAL / 2) - 40;
  const lw = mm(24);
  return table([lw, half - lw, 80, lw, TOTAL - half - lw - 80], [[
    cell("진 단 명", { w: lw, label: true, size: 16 }),
    cell(dx, { w: half - lw, size: 16 }),
    plainCell([para("", { size: 2 })], { w: 80 }),
    cell("시행 방법", { w: lw, label: true, size: 16 }),
    cell(proc, { w: TOTAL - half - lw - 80, size: 16 }),
  ]], h);
}

const LINE_H = 250;
function blockHeight(items, blanks, hasAsa, lineH) {
  // 여백 90 + 여유 60. ASA 표를 넣는 구획은 사이 문단(112)까지 더한다.
  let h = items.length * lineH + blanks * lineH + 150;
  if (hasAsa) h += 112 + 6 * mm(4.8) + 40;
  return h;
}

function makeDoc(e, opt) {
  const { blanks, g, lineH, infoH = mm(7.6), tail = 0 } = opt;
  const kids = [];
  const body = [].concat(
    titleBlock(e.title, LEGAL, e.title.length < 18 ? 40 : 32),
    [
      infoTable([
        ["보호자", [["성명", "", "연락처", ""], ["주소", "", null, null]]],
        ["반려동물", [["이름", "", "종 / 품종", ""], ["성별 / 중성화", "", "연령 / 체중", ""],
                     ["특이사항", "", null, null]]],
        ["수의사", [["동물병원명", "", "수의사 성명", ""]]],
      ], IN_W, infoH),
      gap(g),
      twoBox(e.dx, e.proc, mm(9)),
      gap(g),
      sec("진료의 필요성 ·\n방법 및 내용",
        bulletLines(e.need.concat(Array(blanks).fill(" ")), { size: 16, lineH }),
        { height: blockHeight(e.need, blanks, false, lineH) }),
      gap(g),
      sec("전형적으로\n발생이 예상되는\n후유증 또는 부작용",
        bulletLines(e.risk, { size: 16, lineH })
          .concat(e.anes ? [para("", { size: 8 }), asaTable(IW, mm(4.8))] : [])
          .concat(bulletLines(Array(blanks).fill(" "), { size: 16, lineH })),
        { height: blockHeight(e.risk, blanks, e.anes, lineH) }),
      gap(g),
      sec("진료 전후에\n보호자의\n준수 및 숙지 사항",
        bulletLines(e.care.concat(Array(blanks).fill(" ")), { size: 16, lineH }),
        { height: blockHeight(e.care, blanks, false, lineH) }),
      gap(180 + tail),
      table([TOTAL], [[plainCell(closing(DECL, "*기타 내용이 발생할 경우 별지를 포함합니다."),
        { w: TOTAL, margins: { top: 0, bottom: 0, left: 0, right: 0 } })]], mm(17)),
      gap(150),
      signRow(["보호자", "설명 수의사"]),
    ]);
  return body;
}

function totalHeight(body) {
  return body.reduce((s, el) => s + (typeof el.__h === "number" ? el.__h : 0), 0) + 120;
}

const INFO_MIN = mm(7.6), INFO_MAX = mm(12);

(async () => {
  const data = JSON.parse(fs.readFileSync(path.join(BASE, "data", "procedures.json"), "utf8"));
  const opts = [
    { blanks: 2, g: 136, lineH: 250 },
    { blanks: 1, g: 136, lineH: 250 },
    { blanks: 1, g: 110, lineH: 235 },
    { blanks: 0, g: 110, lineH: 235 },
    { blanks: 0, g: 90, lineH: 225 },
  ];
  let made = 0;
  const failed = [];
  for (const e of data) {
    // 1) 내용이 들어가는 조합을 찾는다
    let opt = opts[opts.length - 1];
    for (const o of opts) {
      if (totalHeight(makeDoc(e, o)) <= USABLE) { opt = o; break; }
    }
    opt = Object.assign({}, opt);

    // 2) 공간이 남으면 빈 줄을 늘려 적을 자리를 넓힌다
    while (opt.blanks < 4) {
      const t = Object.assign({}, opt, { blanks: opt.blanks + 1 });
      if (totalHeight(makeDoc(e, t)) > USABLE - mm(12)) break;
      opt = t;
    }

    // 3) 남는 공간의 절반은 기입 칸 높이로 (볼펜으로 쓰기 편하도록)
    let room = USABLE - totalHeight(makeDoc(e, opt));
    opt.infoH = Math.min(INFO_MAX, INFO_MIN + Math.max(0, Math.floor(room * 0.5 / 6)));

    // 4) 그러고도 남는 공간은 서명 앞으로 — 서명줄을 맨 아래에 둔다
    room = USABLE - totalHeight(makeDoc(e, opt));
    if (room > 30) opt.tail = room - 20;

    const rel = path.join(ROOT, e.dir, e.file + ".docx");
    try {
      await buildDoc(e.title, makeDoc(e, opt), rel);
      made += 1;
    } catch (err) {
      failed.push(e.title + " — " + err.message.split("\n")[0]);
    }
  }
  console.log(`질환별 동의서 워드 ${made}건 생성`);
  if (failed.length) {
    console.log(`  ⚠ 실패 ${failed.length}건`);
    failed.slice(0, 5).forEach((f) => console.log("     " + f));
    process.exit(1);
  }
})();

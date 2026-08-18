// KAHA 표준 서식 스타일 (워드) — tools/form_style.py 와 같은 구성을 만든다.
// 협회 사무국 제작 양식(미용 마취 동의서)이 기준이며, 새 양식은 이 모듈의
// 요소만 조합해 만든다.
//
// A4 1장 보장: 본문의 모든 요소에 고정 높이(EXACT)를 주고, 합계가 한 장에
// 들어가는지 buildDoc 에서 검사한다. 높이가 없는 요소가 있으면 실패시킨다.
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, BorderStyle, VerticalAlign, LineRuleType,
  HeightRule, Header, Footer, PageBorderDisplay, PageBorderOffsetFrom, PageBorderZOrder,
  HorizontalPositionRelativeFrom, VerticalPositionRelativeFrom, TextWrappingType,
} = require("docx");

const BASE = path.dirname(__dirname);
const OUT = path.join(BASE, "forms");
const LOGO = fs.readFileSync(path.join(BASE, "assets", "kaha-logo.png"));
const EMBLEM = fs.readFileSync(path.join(BASE, "assets", "kaha-emblem.png"));
const WATERMARK = fs.readFileSync(path.join(BASE, "assets", "kaha-watermark.png"));

// ── 팔레트 (사무국 양식 기준) ─────────────────────────────────────
const NAVY = "1B3A5C";
const INK = "333333";
const LABEL_BG = "EFEFEF";
const LINE = "BFBFBF";
const SOFT = "767676";

const FONT = { ascii: "Malgun Gothic", hAnsi: "Malgun Gothic", eastAsia: "Malgun Gothic" };

// ── 페이지 규격 (twips) ──────────────────────────────────────────
const PAGE_W = 11906, PAGE_H = 16838;      // A4
const MARGIN_LR = 964;                      // 17mm
const MARGIN_TOP = 851;                     // 15mm
const MARGIN_BOTTOM = 1701;                 // 30mm — 하단 협회 표기 자리
const FOOTER_OFFSET = 794;                  // 14mm — 표기가 종이 끝에서 떨어진 거리
const SAFETY = 340;
const TOTAL = PAGE_W - MARGIN_LR * 2;       // 본문 폭 9978
const USABLE = PAGE_H - MARGIN_TOP - MARGIN_BOTTOM - SAFETY;

const thin = { style: BorderStyle.SINGLE, size: 4, color: LINE };
const BORDERS = { top: thin, bottom: thin, left: thin, right: thin };
const NO_BORDER = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const NONE_ALL = { top: NO_BORDER, bottom: NO_BORDER, left: NO_BORDER, right: NO_BORDER };

function H(el, twips) { el.__h = twips; return el; }

function assertOnePage(name, children) {
  let total = 0;
  const unknown = [];
  children.forEach((el, i) => {
    if (el && typeof el.__h === "number") total += el.__h;
    else unknown.push(i);
  });
  if (unknown.length) {
    throw new Error(`${name}: 높이 미지정 요소 ${unknown.length}개 (위치 ${unknown.join(", ")}) — A4 1장을 보장할 수 없음`);
  }
  if (total > USABLE) {
    throw new Error(`${name}: 본문 ${total} > 허용 ${USABLE} twips (${((total - USABLE) / 56.7).toFixed(1)}mm 초과)`);
  }
  console.log(`  ${name.padEnd(26)} ${total} / ${USABLE} twips  (여유 ${((USABLE - total) / 56.7).toFixed(1)}mm)`);
}

function run(text, { bold = false, size = 17, color = INK } = {}) {
  return new TextRun({ text, bold, size, color, font: FONT, snapToGrid: false });
}

function para(text, opts = {}, pOpts = {}) {
  const sz = opts.size || 17;
  const lines = String(text).split("\n");
  const children = [];
  lines.forEach((ln, i) => {
    if (i) children.push(new TextRun({ break: 1 }));
    children.push(run(ln, opts));
  });
  return new Paragraph({
    children,
    spacing: { before: 0, after: 0, line: Math.round(sz * 14), lineRule: LineRuleType.EXACT },
    ...pOpts,
  });
}

function centered(text, opts = {}) {
  return para(text, opts, { alignment: AlignmentType.CENTER });
}

/** 일반 셀 — 값을 적는 칸 */
function cell(text, { w, label = false, bold = false, size = 17, color = INK, span, fill,
                     align, valignTop = false, lines = 0 } = {}) {
  const children = [];
  if (text !== "" && text !== undefined && text !== null) {
    children.push(para(text, { bold: bold || label, size, color },
      align ? { alignment: align } : {}));
  }
  for (let i = 0; i < lines; i++) {
    children.push(new Paragraph({ children: [], spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.EXACT } }));
  }
  if (!children.length) {
    children.push(new Paragraph({ children: [], spacing: { before: 0, after: 0, line: 240, lineRule: LineRuleType.EXACT } }));
  }
  return new TableCell({
    children,
    width: { size: w, type: WidthType.DXA },
    columnSpan: span,
    borders: BORDERS,
    verticalAlign: valignTop ? VerticalAlign.TOP : VerticalAlign.CENTER,
    shading: fill ? { type: ShadingType.CLEAR, fill } : label ? { type: ShadingType.CLEAR, fill: LABEL_BG } : undefined,
    margins: { top: 20, bottom: 20, left: 90, right: 70 },
  });
}

/** 칸 안이 표로 끝나면 워드가 기본 높이(240 twips)의 빈 문단을 스스로 붙인다.
 *  그 높이는 통제할 수 없어 칸을 넘치게 하므로, 아주 낮은 빈 문단을 직접 넣어 막는다. */
function sealCell(children) {
  const last = children[children.length - 1];
  if (last && last.constructor && last.constructor.name === "Table") {
    return children.concat([new Paragraph({
      children: [], spacing: { before: 0, after: 0, line: 20, lineRule: LineRuleType.EXACT },
    })]);
  }
  return children;
}

function plainCell(children, { w, fill, span, rowSpan, borders = NONE_ALL, margins, valignTop } = {}) {
  return new TableCell({
    children: sealCell(children), width: { size: w, type: WidthType.DXA }, columnSpan: span, rowSpan, borders,
    verticalAlign: valignTop ? VerticalAlign.TOP : VerticalAlign.CENTER,
    shading: fill ? { type: ShadingType.CLEAR, fill } : undefined,
    margins: margins || { top: 20, bottom: 20, left: 90, right: 70 },
  });
}

function table(columnWidths, rows, heights) {
  if (heights === undefined) throw new Error("table(): 행 높이는 필수입니다 (A4 1장 보장).");
  const h = (i) => (Array.isArray(heights) ? heights[i] : heights);
  const t = new Table({
    columnWidths,
    width: { size: columnWidths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    rows: rows.map((cells, i) => new TableRow({
      children: cells, height: { value: h(i), rule: HeightRule.EXACT },
    })),
  });
  return H(t, rows.reduce((sum, _, i) => sum + h(i), 0));
}

function gap(h = 136) {
  return H(new Paragraph({ children: [], spacing: { before: 0, after: 0, line: h, lineRule: LineRuleType.EXACT } }), h);
}

// ── 표준 구성 요소 ───────────────────────────────────────────────

/** 원형 엠블럼 + 큰 제목 + 근거 법령 한 줄 */
function titleBlock(title, legal, titleSize = 44) {
  const E = 850;
  return [
    table([E, TOTAL - E], [[
      plainCell([new Paragraph({
        children: [new ImageRun({ type: "png", data: EMBLEM, transformation: { width: 46, height: 46 } })],
        spacing: { before: 0, after: 0, line: 800, lineRule: LineRuleType.EXACT },
      })], { w: E, margins: { top: 0, bottom: 0, left: 0, right: 160 } }),
      plainCell([para(title, { bold: true, size: titleSize, color: NAVY })],
        { w: TOTAL - E, margins: { top: 0, bottom: 0, left: 0, right: 0 } }),
    ]], 800),
    H(para(legal, { size: 16 }, { spacing: { before: 100, after: 0, line: 240, lineRule: LineRuleType.EXACT } }), 340),
    gap(150),
  ];
}

/** 인적사항 표 — groups = [[그룹명, [[셀…]…]]…], 행 안의 null 은 왼쪽과 가로 병합 */
function infoTable(groups, widths, rowH) {
  const rows = [];
  groups.forEach(([gname, grows]) => {
    grows.forEach((cells, i) => {
      const out = [];
      if (i === 0) {
        out.push(new TableCell({
          children: [centered(gname, { bold: true, size: 17 })],
          width: { size: widths[0], type: WidthType.DXA },
          rowSpan: grows.length, borders: BORDERS,
          verticalAlign: VerticalAlign.CENTER,
          shading: { type: ShadingType.CLEAR, fill: LABEL_BG },
          margins: { top: 20, bottom: 20, left: 40, right: 40 },
        }));
      }
      let c = 0;
      while (c < cells.length) {
        if (cells[c] === null) { c += 1; continue; }
        let span = 1;
        while (c + span < cells.length && cells[c + span] === null) span += 1;
        const w = widths.slice(c + 1, c + 1 + span).reduce((a, b) => a + b, 0);
        out.push(cell(cells[c], { w, span: span > 1 ? span : undefined, label: c % 2 === 0 }));
        c += span;
      }
      rows.push(out);
    });
  });
  return table(widths, rows, rowH);
}

/** 좌측 회색 라벨 + 우측 내용의 구획 상자 */
function sec(label, contentChildren, { note = "", labelW = 1928, height, valignTop = false } = {}) {
  const labelKids = [centered(label, { bold: true, size: 17 })];
  if (note) labelKids.push(centered(note, { size: 13, color: SOFT }));
  return table([labelW, TOTAL - labelW], [[
    plainCell(labelKids, { w: labelW, fill: LABEL_BG, borders: { ...BORDERS },
      margins: { top: 20, bottom: 20, left: 40, right: 40 } }),
    plainCell(contentChildren, { w: TOTAL - labelW, borders: { ...BORDERS }, valignTop,
      margins: { top: 40, bottom: 40, left: 140, right: 100 } }),
  ]], height);
}

/** · 또는 □ 로 시작하는 안내 문단 묶음 */
function bulletLines(lines, { size = 16, marker = "· ", lineH, hanging } = {}) {
  // 줄이 넘어가면 머리기호 폭만큼 들여써서 둘째 줄 글머리를 맞춘다
  const ind = hanging !== undefined ? hanging : (marker ? Math.round(size * 11) : 0);
  return lines.map((t) => new Paragraph({
    children: [run(marker + t, { size })],
    indent: ind ? { left: ind, hanging: ind } : undefined,
    spacing: { before: 0, after: 0, line: lineH || Math.round(size * 15), lineRule: LineRuleType.EXACT },
  }));
}

/** 구획 안의 기입 칸 표 (테두리 있는 격자) */
function fieldTable(rows, widths, heights) {
  const body = rows.map((cells) => {
    const out = [];
    let c = 0;
    while (c < cells.length) {
      if (cells[c] === null) { c += 1; continue; }
      let span = 1;
      while (c + span < cells.length && cells[c + span] === null) span += 1;
      const w = widths.slice(c, c + span).reduce((a, b) => a + b, 0);
      const conf = typeof cells[c] === "object" && cells[c] !== null && !Array.isArray(cells[c])
        ? cells[c] : { text: cells[c] };
      out.push(cell(conf.text, {
        w, span: span > 1 ? span : undefined, label: conf.label, size: conf.size || 16,
        valignTop: conf.top, align: conf.align,
      }));
      c += span;
    }
    return out;
  });
  return table(widths, body, heights);
}

/** 기록용 빈 표 */
function recTable(headers, widths, nRows, rowH, headH, size = 14) {
  const head = headers.map((h, i) => cell(h, { w: widths[i], bold: true, size, fill: LABEL_BG,
                                              align: AlignmentType.CENTER }));
  const rows = [head];
  for (let r = 0; r < nRows; r++) rows.push(widths.map((w) => cell("", { w })));
  return table(widths, rows, [headH].concat(Array(nRows).fill(rowH)));
}

const ASA_ROWS = [
  ["Ⅰ", "정상적이고 건강한 개체", "0.1"],
  ["Ⅱ", "활동을 제한하지 않는 가벼운 전신적 질환", "1"],
  ["Ⅲ", "활동이 가능한 중증의 전신적 질환", "10"],
  ["Ⅳ", "지속적으로 생명을 위협하며, 활동이 불가능한 전신적 질환", "30"],
  ["Ⅴ", "수술과 관계없이 24시간 이내에 사망할 수 있는 빈사 상태", "50"],
];

function asaTable(totalW, rowH = 278) {
  // 체크 · 등급 · 정의 · 사망률 — 해당 등급에 표시할 수 있게 체크칸을 둔다
  const w = [Math.round(totalW * 0.075), Math.round(totalW * 0.105), 0, Math.round(totalW * 0.12)];
  w[2] = totalW - w[0] - w[1] - w[3];
  const mk = (cells, fill) => cells.map((t, i) =>
    cell(t, { w: w[i], size: 14, bold: !!fill, fill, align: AlignmentType.CENTER }));
  const rows = [mk(["체크", "ASA 등급", "정 의", "사망률(%)"], LABEL_BG)]
    .concat(ASA_ROWS.map((r) => mk(["\u25A1"].concat(r))));
  return table(w, rows, rowH);
}

/** 가운데 정렬 동의 선언문 */
function closing(text, note = "") {
  const kids = [centered(text, { size: 16 })];
  if (note) kids.push(centered(note, { size: 16 }));
  return kids;
}

/** 서명줄 — 점선 상자 */
function signRow(roles) {
  const dotted = { style: BorderStyle.DOTTED, size: 4, color: "9A9A9A" };
  // 서명자가 셋 이상이면 폭이 모자라므로 날짜 칸과 안내 문구를 줄인다
  const many = roles.length >= 3;
  const dateW = many ? 2270 : 3180;
  const labelW = many ? 950 : 1100;
  let noteW = many ? 700 : 1250;
  let lineW = Math.floor((TOTAL - dateW - roles.length * (labelW + noteW)) / roles.length);
  if (lineW < 900) { noteW = 0; lineW = Math.floor((TOTAL - dateW - roles.length * labelW) / roles.length); }
  const underline = { top: NO_BORDER, left: NO_BORDER, right: NO_BORDER,
                      bottom: { style: BorderStyle.SINGLE, size: 4, color: "9A9A9A" } };
  const dUnit = 620;
  const dUnit2 = many ? 420 : dUnit;
  const dW = [400, dUnit2, 300, dUnit2, 300, dUnit2, 300, many ? 50 : 280];
  const dTxt = ["20", "", "년", "", "월", "", "일", ""];
  const dCells = dW.map((w, i) => new TableCell({
    children: [para(dTxt[i], { size: 17 })],
    width: { size: w, type: WidthType.DXA },
    borders: (i % 2 === 1 && i < 6) ? underline : NONE_ALL,
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 0, bottom: 0, left: 20, right: 20 },
  }));
  const dateTbl = new Table({
    columnWidths: dW, width: { size: dateW, type: WidthType.DXA },
    rows: [new TableRow({ children: dCells, height: { value: 470, rule: HeightRule.EXACT } })],
  });
  const cells = [plainCell([dateTbl], { w: dateW, margins: { top: 0, bottom: 0, left: 0, right: 0 } })];
  const widths = [dateW];
  roles.forEach((r) => {
    cells.push(plainCell([para(r, { size: 17, bold: true })], { w: labelW,
      margins: { top: 0, bottom: 0, left: 60, right: 60 } }));
    cells.push(new TableCell({
      children: [para("", { size: 17 })], width: { size: lineW, type: WidthType.DXA },
      borders: { top: dotted, bottom: dotted, left: dotted, right: dotted },
      verticalAlign: VerticalAlign.CENTER,
      margins: { top: 20, bottom: 20, left: 60, right: 60 },
    }));
    if (noteW) {
      cells.push(plainCell([para(many ? "(서명)" : "(서명 또는 인)", { size: 13, color: SOFT })],
        { w: noteW, margins: { top: 0, bottom: 0, left: 40, right: 0 } }));
      widths.push(labelW, lineW, noteW);
    } else {
      widths.push(labelW, lineW);
    }
  });
  return table(widths, [cells], 570);
}

// ── 문서 조립 ────────────────────────────────────────────────────
function watermarkHeader() {
  return new Header({
    children: [new Paragraph({
      children: [new ImageRun({
        type: "png", data: WATERMARK,
        transformation: { width: 334, height: 334 },
        floating: {
          horizontalPosition: { relative: HorizontalPositionRelativeFrom.PAGE, offset: 1330000 },
          verticalPosition: { relative: VerticalPositionRelativeFrom.PAGE, offset: 2540000 },
          behindDocument: true, allowOverlap: true,
          wrap: { type: TextWrappingType.NONE },
        },
      })],
      spacing: { before: 0, after: 0, line: 20, lineRule: LineRuleType.EXACT },
    })],
  });
}

function markFooter() {
  const L = 2400;
  const t = new Table({
    columnWidths: [2600, L, TOTAL - 2600 - L],
    width: { size: TOTAL, type: WidthType.DXA },
    rows: [new TableRow({
      children: [
        plainCell([para("", { size: 2 })], { w: 2600 }),
        plainCell([new Paragraph({
          children: [new ImageRun({ type: "png", data: LOGO, transformation: { width: 122, height: 24 } })],
          spacing: { before: 0, after: 0, line: 400, lineRule: LineRuleType.EXACT },
        })], { w: L, margins: { top: 0, bottom: 0, left: 0, right: 100 } }),
        plainCell([
          para("* 본 병원은 한국동물병원협회(KAHA) 회원병원입니다.", { size: 14 }),
          para("● Korean Animal Hospital Association (KAHA)", { size: 14 }),
        ], { w: TOTAL - 2600 - L, margins: { top: 0, bottom: 0, left: 0, right: 0 } }),
      ],
      height: { value: 430, rule: HeightRule.EXACT },
    })],
  });
  return new Footer({ children: [t, new Paragraph({ children: [], spacing: { before: 0, after: 0, line: 20, lineRule: LineRuleType.EXACT } })] });
}

function buildDoc(name, children, filename) {
  const body = children.concat([gap(120)]);
  assertOnePage(name, body);
  const navy = { style: BorderStyle.SINGLE, size: 18, color: NAVY, space: 27 };  // 종이 끝에서 약 9.5mm
  const doc = new Document({
    styles: { default: { document: { run: { font: FONT, size: 17, color: INK } } } },
    sections: [{
      properties: {
        page: {
          size: { width: PAGE_W, height: PAGE_H },
          margin: { top: MARGIN_TOP, bottom: MARGIN_BOTTOM, left: MARGIN_LR, right: MARGIN_LR,
                    header: 340, footer: FOOTER_OFFSET },
          borders: {
            pageBorders: { display: PageBorderDisplay.ALL_PAGES,
                           offsetFrom: PageBorderOffsetFrom.PAGE,
                           zOrder: PageBorderZOrder.BACK },
            pageBorderTop: navy, pageBorderBottom: navy,
            pageBorderLeft: navy, pageBorderRight: navy,
          },
        },
      },
      headers: { default: watermarkHeader() },
      footers: { default: markFooter() },
      children: body,
    }],
  });
  const dest = path.join(OUT, filename);
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  return Packer.toBuffer(doc).then((b) => fs.writeFileSync(dest, b));
}

module.exports = {
  TOTAL, USABLE, LABEL_BG, LINE, NAVY, INK, SOFT, AlignmentType,
  H, run, para, centered, cell, plainCell, table, gap,
  titleBlock, infoTable, sec, bulletLines, fieldTable, recTable, asaTable,
  closing, signRow, buildDoc,
};

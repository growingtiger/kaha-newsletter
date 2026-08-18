// KAHA 회원병원 실무 소식지 제공 양식 — 수정 가능한 워드(.docx) 버전 생성.
// PDF(tools/make_forms.py)와 같은 구성·브랜드 팔레트(KAHA 블루 #035293)를 따른다.
// 실행: node tools/make_forms_docx.js  (필요 패키지: docx)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, BorderStyle, VerticalAlign, LineRuleType,
  HeightRule,
} = require("docx");

const BASE = path.dirname(__dirname);
const OUT = path.join(BASE, "forms");
const LOGO = fs.readFileSync(path.join(BASE, "assets", "kaha-logo.png"));

const BLUE = "035293";
const BLUE_DK = "023A68";
const BLUE_BG = "EDF3FA";
const INK = "231916";
const GREY = "6B7683";
const LINE = "B9CCDE";

const FONT = { ascii: "Malgun Gothic", hAnsi: "Malgun Gothic", eastAsia: "Malgun Gothic" };
const TOTAL = 10090; // A4 - 좌우 여백

// ── A4 1장 보장 ────────────────────────────────────────────────────
// 워드는 사용자 PC의 폰트·문서 그리드에 따라 줄 높이가 달라지므로,
// 본문의 모든 요소에 고정 높이(EXACT)를 주고 그 합이 한 장에 들어가는지
// 빌드 단계에서 검사한다. 높이가 지정되지 않은 요소가 하나라도 있으면
// 실패시킨다 — 자동 높이 요소는 사용자 환경에서 늘어나 장을 넘긴다.
const PAGE_H = 16838;        // A4 세로 (twips)
const PAGE_MARGIN_TB = 540;  // 위·아래 여백
const SAFETY = 340;          // 표 테두리·반올림 오차 여유 (약 6mm)
const USABLE = PAGE_H - PAGE_MARGIN_TB * 2 - SAFETY;

const border = { style: BorderStyle.SINGLE, size: 4, color: LINE };
const BORDERS = { top: border, bottom: border, left: border, right: border };

/** 요소에 고정 높이를 기록한다(1장 검사용). */
function H(el, twips) {
  el.__h = twips;
  return el;
}

/** 본문 높이 합계가 A4 한 장을 넘지 않는지 검사. 넘거나 미지정 요소가 있으면 실패. */
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
    throw new Error(`${name}: 본문 높이 ${total} twips > 허용 ${USABLE} twips (${Math.round((total - USABLE) / 56.7 * 10) / 10}mm 초과) — 행 높이를 줄일 것`);
  }
  console.log(`  ${name.padEnd(28)} ${total} / ${USABLE} twips  (여유 ${Math.round((USABLE - total) / 56.7 * 10) / 10}mm)`);
}

function run(text, { bold = false, size = 18, color = INK } = {}) {
  // snapToGrid=false: 한국어 워드의 문서 그리드가 줄 높이를 밀어 올리는 것을 막는다.
  return new TextRun({ text, bold, size, color, font: FONT, snapToGrid: false });
}

function para(text, opts = {}, pOpts = {}) {
  const sz = opts.size || 18;
  return new Paragraph({
    children: [run(text, opts)],
    spacing: { before: 0, after: 0, line: Math.round(sz * 14), lineRule: LineRuleType.EXACT },
    ...pOpts,
  });
}

function cell(text, { w, label = false, bold = false, size = 18, color = INK, span, fill, empty = 0 } = {}) {
  const children = [];
  if (text !== "") children.push(para(text, { bold: bold || label, size, color: fill === BLUE ? "FFFFFF" : color }));
  for (let i = 0; i < empty; i++) children.push(new Paragraph({ children: [], spacing: { before: 0, after: 0, line: 252, lineRule: LineRuleType.EXACT } }));
  if (children.length === 0) children.push(new Paragraph({ children: [], spacing: { before: 0, after: 0, line: 252, lineRule: LineRuleType.EXACT } }));
  return new TableCell({
    children,
    width: { size: w, type: WidthType.DXA },
    columnSpan: span,
    borders: BORDERS,
    verticalAlign: VerticalAlign.CENTER,
    shading: fill ? { type: ShadingType.CLEAR, fill } : label ? { type: ShadingType.CLEAR, fill: BLUE_BG } : undefined,
    margins: { top: 36, bottom: 36, left: 90, right: 60 },
  });
}

function table(columnWidths, rows, heights) {
  if (heights === undefined) {
    throw new Error("table(): 행 높이를 반드시 지정해야 합니다 (A4 1장 보장). 숫자 또는 행별 배열.");
  }
  const h = (i) => (Array.isArray(heights) ? heights[i] : heights);
  const t = new Table({
    columnWidths,
    width: { size: TOTAL, type: WidthType.DXA },
    rows: rows.map((cells, i) => new TableRow({
      children: cells,
      height: { value: h(i), rule: HeightRule.EXACT },
    })),
  });
  return H(t, rows.reduce((sum, _, i) => sum + h(i), 0));
}

// ── 벳아너스 서식을 벤치마킹한 KAHA 동의서 전용 스타일 ─────────────
const NO_BORDER = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const NONE_ALL = { top: NO_BORDER, bottom: NO_BORDER, left: NO_BORDER, right: NO_BORDER };

function plainCell(children, { w, fill, span, rowSpan, borders = NONE_ALL, margins } = {}) {
  return new TableCell({
    children,
    width: { size: w, type: WidthType.DXA },
    columnSpan: span,
    rowSpan,
    borders,
    verticalAlign: VerticalAlign.CENTER,
    shading: fill ? { type: ShadingType.CLEAR, fill } : undefined,
    margins: margins || { top: 20, bottom: 20, left: 90, right: 60 },
  });
}

function centered(text, opts = {}) {
  return para(text, opts, { alignment: AlignmentType.CENTER });
}

/** 상단 브랜드 밴드 — 짙은 파랑 제목부 + 흰 바탕 공식 로고.
 *  formNo를 주면 아래에 서식번호 띠를 붙인다(내부 관리용 양식). */
function brandBand(title, legal, formNo) {
  const L = 6575, R = 3515;
  const band = [
    table([L, R], [[
      plainCell([
        para(title, { bold: true, size: 32, color: "FFFFFF" }),
        para(legal, { size: 14, color: "C8DCEF" }),
      ], { w: L, fill: BLUE_DK, margins: { top: 60, bottom: 60, left: 260, right: 160 } }),
      plainCell([new Paragraph({
        children: [new ImageRun({ type: "png", data: LOGO, transformation: { width: 176, height: 35 } })],
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 0, line: 760, lineRule: LineRuleType.EXACT },
      })], { w: R, fill: "FFFFFF", margins: { top: 0, bottom: 0, left: 0, right: 0 } }),
    ]], 935),
  ];
  if (!formNo) return band;
  return band.concat([
    table([TOTAL], [[
      plainCell([para(`서식번호 ${formNo} · 시행일자 2026. 8. · 작성 후 1년 보존`,
        { size: 14, color: "FFFFFF" }, { alignment: AlignmentType.RIGHT })],
        { w: TOTAL, fill: BLUE, margins: { top: 20, bottom: 20, left: 120, right: 260 } }),
    ]], 300),
  ]);
}

/** 가운데 정렬 구분 제목 — 양옆 가는 선 */
function divider(text) {
  const S = 3800, M = TOTAL - S * 2;
  const rule = { top: NO_BORDER, left: NO_BORDER, right: NO_BORDER,
                 bottom: { style: BorderStyle.SINGLE, size: 4, color: LINE } };
  return table([S, M, S], [[
    plainCell([para("", { size: 2 })], { w: S, borders: rule }),
    plainCell([centered(text, { bold: true, size: 21, color: BLUE_DK })], { w: M }),
    plainCell([para("", { size: 2 })], { w: S, borders: rule }),
  ]], 360);
}

/** 소제목 바 — 왼쪽 파란 강조선 + 연한 파랑 바탕 (KAHA 식별) */
function capBar(title, note = "") {
  const A = 130;
  const runs = [run(title, { bold: true, size: 19, color: BLUE_DK })];
  if (note) runs.push(run("  " + note, { size: 15, color: GREY }));
  return table([A, TOTAL - A], [[
    plainCell([para("", { size: 2 })], { w: A, fill: BLUE }),
    plainCell([new Paragraph({
      children: runs, alignment: AlignmentType.CENTER,
      spacing: { before: 0, after: 0, line: 266, lineRule: LineRuleType.EXACT },
    })], { w: TOTAL - A, fill: BLUE_BG }),
  ]], 340);
}

function sectionBar(title) {
  return table([TOTAL], [[cell(title, { w: TOTAL, bold: true, size: 19, fill: BLUE })]], 340);
}

function gap(h = 90) {
  return H(new Paragraph({ children: [], spacing: { before: 0, after: 0, line: h, lineRule: LineRuleType.EXACT } }), h);
}

/** 표 밖 주석 한 줄 — 고정 높이 상자에 담아 늘어나지 않게 한다. */
function noteRow(text, h = 300, opts = {}) {
  return table([TOTAL], [[plainCell([para(text, { size: 14, color: GREY, ...opts })],
    { w: TOTAL, margins: { top: 0, bottom: 0, left: 60, right: 60 } })]], h);
}

function header(title, subtitle) {
  const blueRule = { style: BorderStyle.SINGLE, size: 18, color: BLUE };
  return [
    table([TOTAL], [[plainCell([new Paragraph({
      children: [new ImageRun({ type: "png", data: LOGO, transformation: { width: 189, height: 38 } })],
      spacing: { before: 0, after: 0, line: 600, lineRule: LineRuleType.EXACT },
    })], { w: TOTAL, margins: { top: 0, bottom: 0, left: 0, right: 0 } })]], 620),
    table([TOTAL], [[plainCell([para(title, { bold: true, size: 34, color: BLUE_DK })],
      { w: TOTAL, borders: { ...NONE_ALL, bottom: blueRule },
        margins: { top: 0, bottom: 60, left: 0, right: 0 } })]], 580),
    table([TOTAL], [[plainCell([para(subtitle, { size: 15, color: GREY })],
      { w: TOTAL, margins: { top: 40, bottom: 0, left: 0, right: 0 } })]], 400),
  ];
}

function buildDoc(name, children) {
  // 마지막 요소는 반드시 문단이어야 한다 — 표로 끝나면 워드가 빈 문단을
  // 스스로 덧붙이고, 그 높이는 우리가 통제할 수 없어 장을 넘길 수 있다.
  const body = children.concat([gap(120)]);
  assertOnePage(name, body);
  return new Document({
    styles: { default: { document: { run: { font: FONT, size: 18, color: INK } } } },
    sections: [{
      properties: {
        page: {
          size: { width: 11906, height: PAGE_H },
          margin: { top: PAGE_MARGIN_TB, bottom: PAGE_MARGIN_TB, left: 900, right: 900 },
        },
      },
      children: body,
    }],
  });
}

const ASA_TEXT = "□ Ⅰ 건강  □ Ⅱ 경미한 전신질환  □ Ⅲ 중등도 전신질환  □ Ⅳ 생명 위협  □ Ⅴ 위중  □ E 응급";

// ═══ 1. 수술등중대진료(마취) 동의서 ════════════════════════════════
(function () {
  // ── 인적사항: 보호자 · 반려동물 · 수의사 (좌측 라벨 세로 병합) ──
  const LC = 1134, KC = 1361, VC = 3117;
  const IW = [LC, KC, VC, KC, VC];
  const blueBelow = { top: border, left: border, right: border,
                      bottom: { style: BorderStyle.SINGLE, size: 8, color: BLUE } };
  const gcell = (text, o = {}) => cell(text, { ...o, w: o.w });
  const group = (name, rows) => rows.map((r, i) => {
    const cells = i === 0
      ? [new TableCell({
          children: [centered(name, { bold: true, size: 19, color: BLUE_DK })],
          width: { size: LC, type: WidthType.DXA }, rowSpan: rows.length,
          borders: BORDERS, verticalAlign: VerticalAlign.CENTER,
          shading: { type: ShadingType.CLEAR, fill: BLUE_BG },
          margins: { top: 20, bottom: 20, left: 60, right: 60 },
        })]
      : [];
    return cells.concat(r);
  });
  const kv = (k, v, kw = KC, vw = VC, opts = {}) => [
    cell(k, { w: kw, label: true, size: 17 }), cell(v, { w: vw, size: 17, ...opts }),
  ];
  const infoRows = [].concat(
    group("보호자", [
      [...kv("성 명", ""), ...kv("생년월일", "")],
      [...kv("연 락 처", ""), ...kv("동물과의 관계", "□ 소유자     □ 대리인")],
      [cell("주 소", { w: KC, label: true, size: 17 }), cell("", { w: VC * 2 + KC, span: 3 })],
    ]),
    group("반려동물", [
      [...kv("이 름", ""), ...kv("종 / 품종", "")],
      [...kv("성별 / 중성화", ""), ...kv("연령 / 체중", "")],
      [cell("특이사항", { w: KC, label: true, size: 17 }), cell("", { w: VC * 2 + KC, span: 3 })],
    ]),
    group("수의사", [
      [...kv("동물병원명", ""), ...kv("면허번호", "")],
      [cell("성 명", { w: KC, label: true, size: 17 }), cell("", { w: VC + KC, span: 2 }),
       cell("(서명 또는 인)", { w: VC, size: 16, color: GREY })],
    ]),
  );

  // ── 후유증 8항목 (테두리 없는 4열) ──
  const RISK = [
    "1) 저혈압 · 저체온 · 고체온", "2) 약물 과민반응에 의한 쇼크",
    "3) 순환부전에 의한 쇼크", "4) 췌장염 · 신부전 및 폐수종",
    "5) 기저질환 발현 및 현증 악화", "6) 삽관에 의한 일시적 기침",
    "7) 출혈 · 감염 · 봉합 부위 벌어짐", "8) 드물게 심정지 및 사망",
  ];
  const RW = Math.floor(TOTAL / 4);
  const riskRow = (from) => RISK.slice(from, from + 4).map((t, i) =>
    plainCell([para(t, { size: 16 })], { w: i === 3 ? TOTAL - RW * 3 : RW }));

  // ── ASA 등급표 ──
  const AW = [907, 1134, 6349, 1700];
  const topLine = { style: BorderStyle.SINGLE, size: 8, color: BLUE };
  const thin = { style: BorderStyle.SINGLE, size: 3, color: LINE };
  const acell = (text, o = {}) => new TableCell({
    children: Array.isArray(text) ? text : [centered(text, { size: 16, ...(o.run || {}) })],
    width: { size: o.w, type: WidthType.DXA }, rowSpan: o.rowSpan,
    borders: o.borders || { top: thin, bottom: thin, left: NO_BORDER, right: NO_BORDER },
    verticalAlign: VerticalAlign.CENTER,
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill } : undefined,
    margins: { top: 10, bottom: 10, left: 40, right: 40 },
  });
  const headBorders = { top: topLine, bottom: topLine, left: NO_BORDER, right: NO_BORDER };
  const lastB = { top: thin, bottom: topLine, left: NO_BORDER, right: NO_BORDER };
  const ASA = [
    ["Ⅰ", "정상적이고 건강한 개체", "0.1"],
    ["Ⅱ", "활동을 제한하지 않는 가벼운 전신질환", "1"],
    ["Ⅲ", "활동이 가능한 중증의 전신질환", "10"],
    ["Ⅳ", "지속적으로 생명을 위협하며 활동이 불가능한 전신질환", "30"],
    ["Ⅴ", "수술과 관계없이 24시간 이내에 사망할 수 있는 빈사 상태", "50"],
  ];
  const asaRows = [
    ["체크", "ASA 등급", "정 의", "사망률(%)"].map((t, i) =>
      acell(t, { w: AW[i], fill: BLUE_BG, borders: headBorders, run: { bold: true, color: BLUE_DK } })),
  ].concat(ASA.map(([g, d, m], r) => {
    const b = r === ASA.length - 1 ? { borders: lastB } : {};
    return [acell("□", { w: AW[0], ...b }), acell(g, { w: AW[1], ...b }),
            acell(d, { w: AW[2], ...b }), acell(m, { w: AW[3], ...b })];
  }));

  const HALF = TOTAL / 2;
  const doc = buildDoc("수술등중대진료(마취) 동의서", [
    ...brandBand("수술등중대진료(마취) 동의서",
      "수의사법 제13조의2 및 같은 법 시행규칙 제13조의3에 따른 설명 · 서면동의"),
    gap(80),
    table(IW, infoRows, 420),
    gap(80),
    divider("설명 및 동의 사항"),
    gap(60),

    capBar("수술등중대진료의 필요성, 방법 및 내용"),
    table([1700, 3345, 1475, 3570], [
      [cell("진단명 (추정 포함)", { w: 1700, label: true, size: 17 }), cell("", { w: 3345 }),
       cell("예정 일시", { w: 1475, label: true, size: 17 }), cell("", { w: 3570 })],
      [cell("수술 / 처치명", { w: 1700, label: true, size: 17 }), cell("", { w: 3345 }),
       cell("마취 방식", { w: 1475, label: true, size: 17 }), cell("", { w: 3570 })],
    ], 420),
    table([1700, 8390], [
      [cell("필요성 · 현재 상태", { w: 1700, label: true, size: 17 }), cell("", { w: 8390 })],
      [cell("방법 및 내용", { w: 1700, label: true, size: 17 }), cell("", { w: 8390 })],
    ], 600),
    gap(70),

    capBar("수술등중대진료에 따라 전형적으로 발생이 예상되는 후유증 또는 부작용"),
    table([RW, RW, RW, TOTAL - RW * 3], [riskRow(0), riskRow(4)], 310),
    table(AW, asaRows, 348),
    gap(70),

    capBar("수술등중대진료 전후에 보호자가 준수 및 숙지하여야 할 사항", "— 해당 항목에 표시하여 주십시오"),
    table([TOTAL], [
      [cell("□  마취 시 수술 전 일정 시간의 금식과 금수가 필요합니다.  ( 음식 ______ 시간 · 물 ______ 시간 )", { w: TOTAL, size: 17 })],
      [cell("□  마취를 시행함에 있어 발생할 수 있는 부작용 · 합병증 또는 후유증에 대한 설명을 충분히 듣고 이해하였습니다.", { w: TOTAL, size: 17 })],
      [cell("□  마취 과정에 있어 불가항력적이거나 환자의 특이체질로 인한 우발사고의 가능성을 인정합니다.", { w: TOTAL, size: 17 })],
      [cell("□  수술 후 주의사항(넥카라 · 활동 제한 · 투약 등)을 준수하고, 응급상황에 연락 가능한 연락처를 유지합니다.", { w: TOTAL, size: 17 })],
    ], 370),
    table([HALF, HALF], [
      [cell("□  심폐소생술(CPR) :  □ 시행 원함   □ 원하지 않음(DNR)", { w: HALF, size: 17 }),
       cell("□  마취 및 수술비 설명을 들었음  ( 예상 : _________ 원 )", { w: HALF, size: 17 })],
      [cell("□  수술 중 상태에 따라 범위가 변경될 수 있음을 설명받음", { w: HALF, size: 17 }),
       cell("변경 시 :  □ 사전 연락 요망   □ 수의사 판단에 위임", { w: HALF, size: 17 })],
    ], 370),
    gap(90),

    table([TOTAL], [[new TableCell({
      children: [para("「수의사법」 제13조의2 및 같은 법 시행규칙 제13조의3에 따라 위와 같이 수의사로부터 수술등중대진료에 관한 설명을 들었으며, 그 필요성 · 방법 · 내용과 전형적으로 예상되는 후유증 및 부작용을 충분히 이해하였습니다. 이에 위 수술등중대진료 및 마취의 시행에 동의하며, 관련한 수의학적 처치를 담당 수의사에게 위임합니다.",
        { size: 17 })],
      width: { size: TOTAL, type: WidthType.DXA },
      borders: {
        top: { style: BorderStyle.SINGLE, size: 8, color: BLUE },
        bottom: { style: BorderStyle.SINGLE, size: 8, color: BLUE },
        left: { style: BorderStyle.SINGLE, size: 8, color: BLUE },
        right: { style: BorderStyle.SINGLE, size: 8, color: BLUE },
      },
      shading: { type: ShadingType.CLEAR, fill: BLUE_BG },
      margins: { top: 90, bottom: 90, left: 150, right: 150 },
    })]], 1140),
    gap(90),
    table([737, 2155, 737, 2665, 1134, 2662], [[
      cell("작성일", { w: 737, label: true, size: 17 }), cell("20____년  ____월  ____일", { w: 2155, size: 17 }),
      cell("보호자", { w: 737, label: true, size: 17 }), cell("성명 : __________ (서명 또는 인)", { w: 2665, size: 17 }),
      cell("설명 수의사", { w: 1134, label: true, size: 17 }), cell("성명 : __________ (서명 또는 인)", { w: 2662, size: 17 }),
    ]], 600),
  ]);
  Packer.toBuffer(doc).then((b) => fs.writeFileSync(path.join(OUT, "01_수술마취/마취동의서_한국동물병원협회.docx"), b));
})();

// ═══ 2. 마취 전 평가·모니터링 체크리스트 ═══════════════════════════
(function () {
  const c2 = [2000, 8090];
  const mon = [1100, 950, 950, 1050, 1050, 1250, 1050, 2690];
  const monHead = ["시각", "HR", "RR", "SpO2", "EtCO2", "혈압", "체온", "마취심도 · 처치 · 비고"];
  const monRows = [monHead.map((t, i) => cell(t, { w: mon[i], bold: true, size: 16, color: BLUE_DK, fill: BLUE_BG }))];
  for (let r = 0; r < 10; r++) monRows.push(mon.map((w) => cell("", { w })));
  const doc = buildDoc("마취 전 평가·모니터링 체크리스트", [
    ...header("마취 전 평가 · 모니터링 체크리스트",
      "마취 전 준비 · 마취 중 모니터링 · 회복기 관리 기록"),
    sectionBar("환자 정보"),
    table([2000, 2100, 1400, 2100, 1200, 1290], [[
      cell("동물명 / 차트번호", { w: 2000, label: true }), cell("", { w: 2100 }),
      cell("종 / 품종", { w: 1400, label: true }), cell("", { w: 2100 }),
      cell("체중(kg)", { w: 1200, label: true }), cell("", { w: 1290 }),
    ]], 431),
    table(c2, [
      [cell("병력 · 현재 투약", { w: c2[0], label: true }), cell("", { w: c2[1] })],
      [cell("신체검사 요약", { w: c2[0], label: true }), cell("", { w: c2[1] })],
      [cell("사전 혈액검사", { w: c2[0], label: true }), cell("□ CBC     □ 혈액화학     □ 전해질     □ 응고계     □ 기타 :", { w: c2[1] })],
      [cell("ASA 분류", { w: c2[0], label: true }), cell(ASA_TEXT, { w: c2[1], size: 16 })],
    ], 431),
    gap(),
    sectionBar("마취 전 준비"),
    table([TOTAL], [
      [cell("□  금식 확인 — 음식 ______ 시간 · 물 ______ 시간   (병원 프로토콜 기준)", { w: TOTAL })],
      [cell("□  IV 카테터 장착      □  기관튜브 3종 준비 ( ____ / ____ / ____ )      □  응급약물 용량 사전 계산 · 비치", { w: TOTAL })],
      [cell("□  마취 회로 · 산소 · 흡인기 점검      □  항불안 처치 필요 여부 평가 (겁 많음 · 공격성)", { w: TOTAL })],
      [cell("□  보호자 설명 및 수술등중대진료(마취) 동의서 작성 완료", { w: TOTAL })],
    ], 380),
    gap(),
    sectionBar("마취 중 모니터링 기록  (15분 간격 권장)"),
    table(mon, monRows, 340),
    noteRow("※ 저체온과 저혈압은 가장 흔한 마취 중 합병증입니다. 조기 인지와 가온 · 수액 대응 프로토콜을 준비하십시오.", 300),
    gap(),
    sectionBar("회복기 관리  (마취 관련 사망 위험이 높은 구간 — 담당자 지정)"),
    table([TOTAL], [
      [cell("□  발관 시각 : ________       □  체온 회복 확인 ( ________ ℃ )       □  통증 평가 ( 도구 / 점수 : ____________ )", { w: TOTAL })],
      [cell("□  의식 · 기립 확인       □  퇴원 전 보호자 주의사항 전달", { w: TOTAL })],
    ], 380),
    gap(),
    table([1400, 3645, 1500, 3545], [[
      cell("마취 담당", { w: 1400, label: true }), cell("성명 : __________ (서명)", { w: 3645 }),
      cell("회복기 담당", { w: 1500, label: true }), cell("성명 : __________ (서명)", { w: 3545 }),
    ]], 560),
  ]);
  Packer.toBuffer(doc).then((b) => fs.writeFileSync(path.join(OUT, "06_진료기록/마취전평가체크리스트_한국동물병원협회.docx"), b));
})();

// ═══ 3. 영양 평가·BCS/MCS 기록지 ═══════════════════════════════════
(function () {
  const c2 = [2300, 7790];
  const bcs = [1600].concat(Array(9).fill(Math.floor((TOTAL - 1600) / 9)));
  bcs[9] += TOTAL - bcs.reduce((a, b) => a + b, 0);
  const bcsRow = [cell("BCS (9점)", { w: bcs[0], bold: true, size: 16, color: BLUE_DK, fill: BLUE_BG })]
    .concat(Array.from({ length: 9 }, (_, i) => cell(`□ ${i + 1}`, { w: bcs[i + 1], size: 16 })));
  const doc = buildDoc("영양 평가·BCS/MCS 기록지", [
    ...header("영양 평가 · BCS / MCS 기록지",
      "모든 환자 · 모든 내원 시 영양 상태 선별 및 기록"),
    sectionBar("환자 정보"),
    table([1900, 1750, 1300, 1650, 900, 1000, 900, 690 + 2000 - 2000], [[
      cell("동물명 / 차트번호", { w: 1900, label: true }), cell("", { w: 1750 }),
      cell("종 / 품종", { w: 1300, label: true }), cell("", { w: 1650 }),
      cell("연령", { w: 900, label: true }), cell("", { w: 1000 }),
      cell("중성화", { w: 900, label: true }), cell("□ 예  □ 아니오", { w: 690 }),
    ]], 431),
    gap(),
    sectionBar("1. 식이 이력"),
    table([2000, 3400, 2000, 2690], [
      [cell("주식 (제품명 · 형태)", { w: 2000, label: true }), cell("", { w: 3400 }), cell("1일 급여량 / 횟수", { w: 2000, label: true }), cell("", { w: 2690 })],
      [cell("간식 · 사람 음식", { w: 2000, label: true }), cell("", { w: 3400 }), cell("영양제 · 보조제", { w: 2000, label: true }), cell("", { w: 2690 })],
      [cell("식욕 변화", { w: 2000, label: true }), cell("□ 없음  □ 증가  □ 감소 (기간: ______)", { w: 3400, size: 16 }),
       cell("음수량 변화", { w: 2000, label: true }), cell("□ 없음  □ 증가  □ 감소", { w: 2690, size: 16 })],
    ], 431),
    gap(),
    sectionBar("2. 체중 및 신체 평가"),
    table([1800, 1800, 2100, 2100, 1200, 1090], [[
      cell("금일 체중(kg)", { w: 1800, label: true }), cell("", { w: 1800 }),
      cell("직전 체중 / 측정일", { w: 2100, label: true }), cell("", { w: 2100 }),
      cell("변화율(%)", { w: 1200, label: true }), cell("", { w: 1090 }),
    ]], 431),
    table(bcs, [bcsRow], 431),
    noteRow("1–3 저체중 · 4–5 이상적 · 6–7 과체중 · 8–9 비만  (갈비뼈 촉진, 허리 라인, 복부 턱업으로 판정)", 300),
    table([2000, 8090], [[
      cell("MCS (근육상태)", { w: 2000, label: true }),
      cell("□ 정상      □ 경도 소실      □ 중등도 소실      □ 중증 소실", { w: 8090 }),
    ]], 431),
    noteRow("척추 · 견갑 · 측두부 · 골반 촉진으로 판정 — 비만 개체도 근소실이 동반될 수 있습니다 (특히 고령 · 만성질환).", 300),
    gap(),
    sectionBar("3. 위험요인 스크리닝  (하나라도 해당 시 확장 평가)"),
    table([TOTAL], [[cell("□ 질병(만성 포함)     □ 고령     □ 비만 / 저체중     □ 수제식 · 생식 · 비전형 식이     □ 피모 · 치아 이상     □ 체중 급변", { w: TOTAL })]], 431),
    gap(),
    sectionBar("4. 평가 결과 및 계획"),
    table(c2, [
      [cell("확장 평가 필요", { w: c2[0], label: true }), cell("□ 불필요       □ 필요  ( 사유 : ______________________________ )", { w: c2[1] })],
      [cell("권장 사료 · 급여량", { w: c2[0], label: true }), cell("", { w: c2[1], empty: 1 })],
      [cell("목표 체중 · 재평가 일정", { w: c2[0], label: true }), cell("", { w: c2[1], empty: 1 })],
      [cell("보호자 상담 내용", { w: c2[0], label: true }), cell("", { w: c2[1], empty: 3 })],
    ], [431, 800, 800, 1300]),
    gap(),
    table([1200, 3200, 1200, 4490], [[
      cell("평가일", { w: 1200, label: true }), cell("20____년  ____월  ____일", { w: 3200 }),
      cell("평가자", { w: 1200, label: true }), cell("성명 : ______________ (서명)", { w: 4490 }),
    ]], 560),
  ]);
  Packer.toBuffer(doc).then((b) => fs.writeFileSync(path.join(OUT, "06_진료기록/영양평가기록지_한국동물병원협회.docx"), b));
})();

// ═══ 4. 입원 동의서 ═════════════════════════════════
(function () {
  const c4 = [1700, 3350, 1700, 3340];
  const c8 = [900, 1300, 1150, 1150, 1150, 1400, 900, 2140];
  const doc = buildDoc("입원 동의서", [
    ...header("입원 동의서",
      "입원 진료의 설명 · 비용 · 경과 보고 · 응급 상황 처리에 관한 동의"),
    sectionBar("동물 · 보호자 정보"),
    table(c4, [
      [cell("동 물 명", { w: c4[0], label: true }), cell("", { w: c4[1] }), cell("보호자 성명", { w: c4[2], label: true }), cell("", { w: c4[3] })],
      [cell("종 / 품종", { w: c4[0], label: true }), cell("", { w: c4[1] }), cell("연 락 처", { w: c4[2], label: true }), cell("", { w: c4[3] })],
      [cell("성별 / 중성화", { w: c4[0], label: true }), cell("", { w: c4[1] }), cell("제2연락처", { w: c4[2], label: true }), cell("", { w: c4[3] })],
    ], 431),
    table(c8, [[
      cell("연령", { w: c8[0], label: true }), cell("", { w: c8[1] }),
      cell("체중(kg)", { w: c8[2], label: true }), cell("", { w: c8[3] }),
      cell("차트번호", { w: c8[4], label: true }), cell("", { w: c8[5] }),
      cell("관계", { w: c8[6], label: true }), cell("□ 소유자  □ 대리인", { w: c8[7], size: 16 }),
    ]], 431),
    gap(),
    sectionBar("1. 입원 사유 및 예상 기간"),
    table([1600, 3400, 1500, 3590], [[
      cell("추정 진단명", { w: 1600, label: true }), cell("", { w: 3400 }),
      cell("입원 목적", { w: 1500, label: true }), cell("", { w: 3590 }),
    ]], 431),
    table([1900, 8190], [[
      cell("예상 입원 기간", { w: 1900, label: true }),
      cell("약 ______ 일        ( 20____. ____. ____.  ～  20____. ____. ____. )", { w: 8190 }),
    ]], 431),
    gap(),
    sectionBar("2. 비용 안내   ※ 1일 입원비는 병원 게시 금액과 동일해야 합니다"),
    table([1600, 2700, 1600, 4190], [[
      cell("1일 입원비", { w: 1600, label: true }), cell("____________ 원", { w: 2700 }),
      cell("예상 총액", { w: 1600, label: true }), cell("____________ 원 (변동 가능)", { w: 4190 }),
    ]], 431),
    table([1900, 8190], [
      [cell("입원비 포함 항목", { w: 1900, label: true }), cell("", { w: 8190 })],
      [cell("별도 청구 항목", { w: 1900, label: true }), cell("□ 검사    □ 처치    □ 약제    □ 수혈    □ 기타 :", { w: 8190 })],
    ], 431),
    table([TOTAL], [[cell("□  예상액의 ______ % 또는 ____________ 원을 초과할 것으로 예상되면 진행 전에 보호자에게 연락합니다.", { w: TOTAL })]], 380),
    gap(),
    sectionBar("3. 경과 보고 및 연락"),
    table([1500, 3300, 1500, 3790], [[
      cell("정기 보고", { w: 1500, label: true }), cell("□ 1일 1회   □ 1일 2회   □ 기타", { w: 3300, size: 16 }),
      cell("보고 방법", { w: 1500, label: true }), cell("□ 전화  □ 문자·메신저  □ 면회 시 구두", { w: 3790, size: 16 }),
    ]], 431),
    table([TOTAL], [[cell("□  상태 급변 시 즉시 연락   /   연락 불통 시 :  □ 수의사 판단으로 필요한 처치 시행   □ 응급처치만 시행 후 재시도", { w: TOTAL })]], 380),
    gap(),
    sectionBar("4. 면회 · 반입물품 · 야간 관리"),
    table([1800, 2900, 1800, 3590], [[
      cell("면회 가능 시간", { w: 1800, label: true }), cell("", { w: 2900 }),
      cell("면회 제한 사유", { w: 1800, label: true }), cell("□ 감염  □ 중환자  □ 기타", { w: 3590, size: 16 }),
    ]], 431),
    table([1600, 8490], [
      [cell("반입물품", { w: 1600, label: true }), cell("(사료 · 약 · 담요 등 :                              )  ※ 분실 시 병원이 책임지지 않을 수 있습니다.", { w: 8490, size: 16 })],
      [cell("야간·휴일 관리", { w: 1600, label: true }), cell("□ 야간 수의사 상주   □ 야간 간호인력 상주   □ 야간 무인 관리 ( ____시 최종 처치 → ____시 확인 )", { w: 8490, size: 16 })],
    ], 431),
    gap(),
    sectionBar("5. 응급 상황 및 사망 시 처리"),
    table([TOTAL], [
      [cell("□  심정지 시 심폐소생술(CPR) :  □ 시행   □ 시행하지 않음(DNR)        □  생명 유지에 필요한 응급처치는 연락 전 시행에 동의", { w: TOTAL })],
      [cell("□  사망 시 :  □ 사체 인도 희망   □ 병원 위탁 처리   □ 동물장묘업 등록 시설 이용 안내 희망", { w: TOTAL })],
    ], 380),
    gap(),
    sectionBar("6. 입원 중 중대진료가 필요해지는 경우"),
    table([TOTAL], [[cell("전신마취를 동반하는 내부장기 · 뼈 · 관절 수술 또는 전신마취를 동반하는 수혈이 필요해지면, 수의사법 제13조의2에 따라 별도의 수술등중대진료 동의서를 작성합니다. 본 입원 동의서가 이를 대신하지 않습니다.", { w: TOTAL, size: 17 })]], 560),
    gap(),
    table([TOTAL], [[cell("본인은 위 내용에 대하여 설명을 듣고 이해하였으며, 입원 및 위 조건에 동의합니다.", { w: TOTAL, bold: true, size: 19, fill: BLUE_BG })]], 400),
    gap(),
    table([1000, 2400, 1100, 2600, 1400, 1590], [[
      cell("작성일", { w: 1000, label: true }), cell("20____년  ____월  ____일", { w: 2400 }),
      cell("보호자", { w: 1100, label: true }), cell("성명 : __________ (서명)", { w: 2600 }),
      cell("설명 수의사", { w: 1400, label: true }), cell("성명 : ______ (서명)", { w: 1590 }),
    ]], 560),
  ]);
  Packer.toBuffer(doc).then((b) => fs.writeFileSync(path.join(OUT, "02_입원응급/입원동의서_한국동물병원협회.docx"), b));
})();

// ═══ 5. 퇴원 안내문 ═════════════════════════════════
(function () {
  const med = [1500, 1650, 1150, 800, 1000, 1150, 1050, 1790];
  const medHead = ["약품명", "무엇 때문에", "1회 용량", "경로", "1일 횟수", "종료일", "식전/식후", "주의할 점"];
  const medRows = [medHead.map((t, i) => cell(t, { w: med[i], bold: true, size: 15, color: BLUE_DK, fill: BLUE_BG }))];
  for (let r = 0; r < 3; r++) medRows.push(med.map((w) => cell("", { w })));

  const calW = [1210].concat(Array(7).fill(Math.floor((TOTAL - 1210) / 7)));
  calW[7] += TOTAL - calW.reduce((a, b) => a + b, 0);
  const calHead = [cell("", { w: calW[0], fill: BLUE_BG })]
    .concat(Array.from({ length: 7 }, (_, i) => cell(`${i + 1}일차`, { w: calW[i + 1], bold: true, size: 15, color: BLUE_DK, fill: BLUE_BG })));
  const calRow = (label) => [cell(label, { w: calW[0], bold: true, size: 16, color: BLUE_DK, fill: BLUE_BG })]
    .concat(Array.from({ length: 7 }, (_, i) => cell("", { w: calW[i + 1] })));

  const doc = buildDoc("퇴원 안내문", [
    ...header("퇴원 안내문",
      "가정 투약 · 가정 관리 · 재진 및 응급 연락 안내"),
    sectionBar("환자 정보"),
    table([1500, 1900, 1700, 1900, 1300, 1790], [
      [cell("동 물 명", { w: 1500, label: true }), cell("", { w: 1900 }),
       cell("보호자 성명", { w: 1700, label: true }), cell("", { w: 1900 }),
       cell("체중(kg)", { w: 1300, label: true }), cell("", { w: 1790 })],
      [cell("차트번호", { w: 1500, label: true }), cell("", { w: 1900 }),
       cell("담당 수의사", { w: 1700, label: true }), cell("", { w: 1900 }),
       cell("퇴원 일시", { w: 1300, label: true }), cell("", { w: 1790 })],
    ], 431),
    table([2100, 7990], [
      [cell("진단명 / 시행한 처치", { w: 2100, label: true }), cell("", { w: 7990 })],
      [cell("퇴원 시점 상태 확인", { w: 2100, label: true }), cell("□ 각성  □ 반응 있음  □ 체온 회복  □ 통증 조절됨   (마취 시행 : □ 예  □ 아니오)", { w: 7990, size: 16 })],
    ], 431),
    gap(),
    sectionBar("1. 가정 투약 안내   ※ 원내 조제·투약분입니다. 처방전이 필요하시면 별도로 요청해 주십시오."),
    table(med, medRows, 400),
    table([TOTAL], [[cell("□  퇴원 전 경구약 투여 방법을 보호자가 직접 해보고 확인하였습니다.      □  약 보관 방법을 안내하였습니다.", { w: TOTAL })]], 380),
    gap(),
    sectionBar("2. 투약 체크 달력   (투여 후 표시하세요)"),
    table(calW, [calHead, calRow("아침"), calRow("저녁")], 400),
    gap(),
    sectionBar("3. 가정 관리   (담당 수의사가 환자에 맞게 기입합니다)"),
    table([1900, 8190], [
      [cell("활동 제한", { w: 1900, label: true }), cell("□ 산책 제한  □ 계단·점프 금지  □ 목줄 산책만    기간 : ________", { w: 8190, size: 16 })],
      [cell("넥카라 · 수술복", { w: 1900, label: true }), cell("□ 착용 필요    착용 기간 : ________          □ 해당 없음", { w: 8190, size: 16 })],
      [cell("절개 부위 관리", { w: 1900, label: true }), cell("□ 물 닿지 않게  □ 소독 : ____________    목욕 가능 시점 : ________", { w: 8190, size: 16 })],
      [cell("식이 · 급수", { w: 1900, label: true }), cell("", { w: 8190 })],
      [cell("관찰 사항", { w: 1900, label: true }), cell("배뇨 · 배변 · 식욕 · 활력 변화 시 기록해 주세요.", { w: 8190, size: 16 })],
    ], 400),
    gap(),
    sectionBar("4. 재진 및 응급 연락"),
    table([1700, 3200, 1500, 3690], [[
      cell("다음 내원일", { w: 1700, label: true }), cell("20____. ____. ____.  ____시", { w: 3200 }),
      cell("재진 목적", { w: 1500, label: true }), cell("□ 경과 확인  □ 봉합사 제거  □ 재검사", { w: 3690, size: 16 }),
    ]], 431),
    table([TOTAL], [
      [cell("아래 증상이 보이면 즉시 연락 주십시오 (담당 수의사 기입) :", { w: TOTAL })],
      [cell("", { w: TOTAL, empty: 2 })],
    ], [340, 700]),
    table([1700, 3200, 1500, 3690], [[
      cell("병원 연락처", { w: 1700, label: true }), cell("", { w: 3200 }),
      cell("야간 · 휴일", { w: 1500, label: true }), cell("", { w: 3690 }),
    ]], 431),
    noteRow("※ 마취 후에는 회복기에 상태가 변할 수 있습니다. 퇴원 후 몇 시간 동안 특히 주의 깊게 지켜봐 주십시오.", 300),
    gap(),
    table([TOTAL], [[cell("□  위 내용을 안내문과 함께 읽으며 설명하였고, 보호자가 이해하였음을 확인합니다.", { w: TOTAL })]], 380),
    gap(),
    table([1100, 2500, 1100, 2600, 1100, 1690], [[
      cell("설명일", { w: 1100, label: true }), cell("20____년 ____월 ____일", { w: 2500 }),
      cell("보호자", { w: 1100, label: true }), cell("성명 : __________ (서명)", { w: 2600 }),
      cell("설명자", { w: 1100, label: true }), cell("성명 : ______ (서명)", { w: 1690 }),
    ]], 560),
  ]);
  Packer.toBuffer(doc).then((b) => fs.writeFileSync(path.join(OUT, "02_입원응급/퇴원안내문_한국동물병원협회.docx"), b));
})();

console.log("워드 양식 5종 생성 요청 완료");

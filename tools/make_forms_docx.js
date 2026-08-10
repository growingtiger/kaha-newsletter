// KAHA 회원병원 실무 소식지 제공 양식 — 수정 가능한 워드(.docx) 버전 생성.
// PDF(tools/make_forms.py)와 같은 구성·브랜드 팔레트(KAHA 블루 #035293)를 따른다.
// 실행: node tools/make_forms_docx.js  (필요 패키지: docx)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell,
  WidthType, ShadingType, AlignmentType, BorderStyle, VerticalAlign,
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

const border = { style: BorderStyle.SINGLE, size: 4, color: LINE };
const BORDERS = { top: border, bottom: border, left: border, right: border };

function run(text, { bold = false, size = 18, color = INK } = {}) {
  return new TextRun({ text, bold, size, color, font: FONT });
}

function para(text, opts = {}, pOpts = {}) {
  return new Paragraph({ children: [run(text, opts)], spacing: { before: 10, after: 10 }, ...pOpts });
}

function cell(text, { w, label = false, bold = false, size = 18, color = INK, span, fill, empty = 0 } = {}) {
  const children = [];
  if (text !== "") children.push(para(text, { bold: bold || label, size, color: fill === BLUE ? "FFFFFF" : color }));
  for (let i = 0; i < empty; i++) children.push(new Paragraph({ children: [], spacing: { before: 10, after: 10 } }));
  if (children.length === 0) children.push(new Paragraph({ children: [] }));
  return new TableCell({
    children,
    width: { size: w, type: WidthType.DXA },
    columnSpan: span,
    borders: BORDERS,
    verticalAlign: VerticalAlign.CENTER,
    shading: fill ? { type: ShadingType.CLEAR, fill } : label ? { type: ShadingType.CLEAR, fill: BLUE_BG } : undefined,
    margins: { top: 50, bottom: 50, left: 90, right: 60 },
  });
}

function table(columnWidths, rows) {
  return new Table({
    columnWidths,
    width: { size: TOTAL, type: WidthType.DXA },
    rows: rows.map((cells) => new TableRow({ children: cells })),
  });
}

function sectionBar(title) {
  return table([TOTAL], [[cell(title, { w: TOTAL, bold: true, size: 19, fill: BLUE })]]);
}

function gap(h = 60) {
  return new Paragraph({ children: [], spacing: { before: 0, after: h } });
}

function header(title, subtitle) {
  return [
    new Paragraph({
      children: [new ImageRun({ type: "png", data: LOGO, transformation: { width: 189, height: 38 } })],
      spacing: { after: 80 },
    }),
    new Paragraph({
      children: [run(title, { bold: true, size: 34, color: BLUE_DK })],
      spacing: { after: 40 },
      border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: BLUE, space: 6 } },
    }),
    new Paragraph({ children: [run(subtitle, { size: 15, color: GREY })], spacing: { after: 120 } }),
  ];
}

function footerPara(formNo) {
  return new Paragraph({
    children: [run(`사단법인 한국동물병원협회 · 회원병원 실무 소식지 제공 양식 (${formNo}) — 병원 실정에 맞게 수정 후 사용하십시오.`, { size: 14, color: GREY })],
    spacing: { before: 160 },
    border: { top: { style: BorderStyle.SINGLE, size: 8, color: BLUE, space: 4 } },
  });
}

function buildDoc(children) {
  return new Document({
    styles: { default: { document: { run: { font: FONT, size: 18, color: INK } } } },
    sections: [{
      properties: { page: { margin: { top: 700, bottom: 700, left: 900, right: 900 } } },
      children,
    }],
  });
}

const ASA_TEXT = "□ Ⅰ 건강  □ Ⅱ 경미한 전신질환  □ Ⅲ 중등도 전신질환  □ Ⅳ 생명 위협  □ Ⅴ 위중  □ E 응급";
const CEPSAF = "※ 등급별 마취 관련 사망 위험(영국 CEPSAF 연구, Brodbelt 등 2008) — 건강 개체(ASA Ⅰ–Ⅱ): 개 0.05% · 고양이 0.11% / 질환 동반(ASA Ⅲ–Ⅴ): 개 1.33% · 고양이 1.40%";

// ═══ 1. 수술·마취 동의서 ═══════════════════════════════════════════
(function () {
  const c4 = [1750, 3300, 1750, 3290];
  const c6 = [1750, 1900, 1300, 1450, 1300, 2390];
  const c2 = [2000, 8090];
  const cs = [1000, 2400, 1100, 2600, 1400, 1590];
  const doc = buildDoc([
    ...header("수술·마취 동의서",
      "수의사법 제13조의2(수술등중대진료 설명·서면동의)에 따른 동의서 — 전신마취 동반 내부장기·뼈·관절 수술 및 수혈 / 작성 후 1년 보존 / 서식번호 KAHA-F-2601"),
    sectionBar("동물·보호자 정보"),
    table(c4, [
      [cell("동 물 명", { w: c4[0], label: true }), cell("", { w: c4[1] }), cell("보호자 성명", { w: c4[2], label: true }), cell("", { w: c4[3] })],
      [cell("종 / 품종", { w: c4[0], label: true }), cell("", { w: c4[1] }), cell("연 락 처", { w: c4[2], label: true }), cell("", { w: c4[3] })],
      [cell("성별 / 중성화", { w: c4[0], label: true }), cell("", { w: c4[1] }), cell("동물과의 관계", { w: c4[2], label: true }), cell("□ 소유자      □ 대리인", { w: c4[3] })],
    ]),
    table(c6, [[
      cell("연령(생년월일)", { w: c6[0], label: true }), cell("", { w: c6[1] }),
      cell("체중(kg)", { w: c6[2], label: true }), cell("", { w: c6[3] }),
      cell("차트번호", { w: c6[4], label: true }), cell("", { w: c6[5] }),
    ]]),
    gap(),
    sectionBar("1. 진단명 및 현재 상태"),
    table(c2, [
      [cell("진단명 (추정 포함)", { w: c2[0], label: true }), cell("", { w: c2[1] })],
      [cell("현재 상태 요약", { w: c2[0], label: true }), cell("", { w: c2[1], empty: 1 })],
      [cell("ASA 신체상태 분류", { w: c2[0], label: true }), cell(ASA_TEXT, { w: c2[1], size: 16 })],
    ]),
    para(CEPSAF, { size: 14, color: GREY }),
    gap(),
    sectionBar("2. 예정 진료의 필요성 · 방법 · 내용"),
    table([2000, 3900, 1500, 2690], [
      [cell("수술 / 처치명", { w: 2000, label: true }), cell("", { w: 3900 }), cell("예정 일시", { w: 1500, label: true }), cell("", { w: 2690 })],
      [cell("집도 수의사", { w: 2000, label: true }), cell("", { w: 3900 }), cell("마취 방식", { w: 1500, label: true }), cell("", { w: 2690 })],
    ]),
    table(c2, [
      [cell("필 요 성", { w: c2[0], label: true }), cell("", { w: c2[1] })],
      [cell("방법 및 내용", { w: c2[0], label: true }), cell("", { w: c2[1], empty: 1 })],
    ]),
    gap(),
    sectionBar("3. 전형적으로 발생이 예상되는 후유증 · 부작용"),
    table([TOTAL], [
      [cell("□  마취 관련 : 저혈압, 저체온, 부정맥, 드물게 심정지 등", { w: TOTAL })],
      [cell("□  수술 관련 : 출혈, 감염, 봉합 부위 벌어짐, 재수술 가능성 등", { w: TOTAL })],
      [cell("□  개체 상태에 따른 추가 위험 :", { w: TOTAL })],
      [cell("※  위 내용은 전형적으로 예상되는 사항이며, 예측하지 못한 상황이 발생할 수 있음을 설명받았습니다.", { w: TOTAL, size: 16, color: GREY })],
    ]),
    gap(),
    sectionBar("4. 보호자 준수사항"),
    table([TOTAL], [
      [cell("□  수술 전 금식 : 음식 ________ 시간  ·  물 ________ 시간", { w: TOTAL })],
      [cell("□  수술 후 주의사항(넥카라 · 활동 제한 · 투약 등) 준수     □  응급상황 연락 가능한 연락처 유지", { w: TOTAL })],
    ]),
    gap(),
    sectionBar("5. 추가 확인"),
    table([TOTAL], [
      [cell("□  수술 중 상태에 따라 범위가 변경될 수 있음을 설명받음   ( 변경 시 :  □ 사전 연락 요망   □ 수의사 판단에 위임 )", { w: TOTAL })],
      [cell("□  예상 진료비용 안내를 받음   ( 예상 범위 : ____________________ 원 )", { w: TOTAL })],
      [cell("□  심폐소생술(CPR) :  □ 시행   □ 시행하지 않음(DNR)", { w: TOTAL })],
    ]),
    gap(),
    table([TOTAL], [[cell("본인은 위 내용에 대하여 충분한 설명을 듣고 이해하였으며, 수술 및 마취 시행에 동의합니다.", { w: TOTAL, bold: true, size: 19, fill: BLUE_BG })]]),
    gap(),
    table(cs, [[
      cell("작성일", { w: cs[0], label: true }), cell("20____년  ____월  ____일", { w: cs[1] }),
      cell("보호자", { w: cs[2], label: true }), cell("성명 : __________ (서명)", { w: cs[3] }),
      cell("설명 수의사", { w: cs[4], label: true }), cell("성명 : ______ (서명)", { w: cs[5] }),
    ]]),
    footerPara("KAHA-F-2601"),
  ]);
  Packer.toBuffer(doc).then((b) => fs.writeFileSync(path.join(OUT, "surgery-anesthesia-consent.docx"), b));
})();

// ═══ 2. 마취 전 평가·모니터링 체크리스트 ═══════════════════════════
(function () {
  const c2 = [2000, 8090];
  const mon = [1100, 950, 950, 1050, 1050, 1250, 1050, 2690];
  const monHead = ["시각", "HR", "RR", "SpO2", "EtCO2", "혈압", "체온", "마취심도 · 처치 · 비고"];
  const monRows = [monHead.map((t, i) => cell(t, { w: mon[i], bold: true, size: 16, color: BLUE_DK, fill: BLUE_BG }))];
  for (let r = 0; r < 9; r++) monRows.push(mon.map((w) => cell("", { w })));
  const doc = buildDoc([
    ...header("마취 전 평가 · 모니터링 체크리스트",
      "2020 AAHA Anesthesia and Monitoring Guidelines for Dogs and Cats 기반 (aaha.org 전문 무료 공개, 참고용) / 서식번호 KAHA-F-2602"),
    sectionBar("환자 정보"),
    table([2000, 2100, 1400, 2100, 1200, 1290], [[
      cell("동물명 / 차트번호", { w: 2000, label: true }), cell("", { w: 2100 }),
      cell("종 / 품종", { w: 1400, label: true }), cell("", { w: 2100 }),
      cell("체중(kg)", { w: 1200, label: true }), cell("", { w: 1290 }),
    ]]),
    table(c2, [
      [cell("병력 · 현재 투약", { w: c2[0], label: true }), cell("", { w: c2[1] })],
      [cell("신체검사 요약", { w: c2[0], label: true }), cell("", { w: c2[1] })],
      [cell("사전 혈액검사", { w: c2[0], label: true }), cell("□ CBC     □ 혈액화학     □ 전해질     □ 응고계     □ 기타 :", { w: c2[1] })],
      [cell("ASA 분류", { w: c2[0], label: true }), cell(ASA_TEXT, { w: c2[1], size: 16 })],
    ]),
    para(CEPSAF, { size: 14, color: GREY }),
    gap(),
    sectionBar("마취 전 준비"),
    table([TOTAL], [
      [cell("□  금식 확인 — 음식 ______ 시간 · 물 ______ 시간   (병원 프로토콜 · AAHA 금식 권고표 참고)", { w: TOTAL })],
      [cell("□  IV 카테터 장착      □  기관튜브 3종 준비 ( ____ / ____ / ____ )      □  응급약물 용량 사전 계산 · 비치", { w: TOTAL })],
      [cell("□  마취 회로 · 산소 · 흡인기 점검      □  항불안 처치 필요 여부 평가 (겁 많음 · 공격성)", { w: TOTAL })],
      [cell("□  보호자 설명 및 동의서 작성 완료 (서식 KAHA-F-2601)", { w: TOTAL })],
    ]),
    gap(),
    sectionBar("마취 중 모니터링 기록  (15분 간격 권장)"),
    table(mon, monRows),
    para("※ 저체온과 저혈압은 가장 흔한 마취 중 합병증입니다. 조기 인지와 가온 · 수액 대응 프로토콜을 준비하십시오.", { size: 14, color: GREY }),
    gap(),
    sectionBar("회복기 관리  (마취 관련 사망 위험이 높은 구간 — 담당자 지정)"),
    table([TOTAL], [
      [cell("□  발관 시각 : ________       □  체온 회복 확인 ( ________ ℃ )       □  통증 평가 ( 도구 / 점수 : ____________ )", { w: TOTAL })],
      [cell("□  의식 · 기립 확인       □  퇴원 전 보호자 주의사항 전달", { w: TOTAL })],
    ]),
    gap(),
    table([1400, 3645, 1500, 3545], [[
      cell("마취 담당", { w: 1400, label: true }), cell("성명 : __________ (서명)", { w: 3645 }),
      cell("회복기 담당", { w: 1500, label: true }), cell("성명 : __________ (서명)", { w: 3545 }),
    ]]),
    footerPara("KAHA-F-2602"),
  ]);
  Packer.toBuffer(doc).then((b) => fs.writeFileSync(path.join(OUT, "pre-anesthesia-checklist.docx"), b));
})();

// ═══ 3. 영양 평가·BCS/MCS 기록지 ═══════════════════════════════════
(function () {
  const c2 = [2300, 7790];
  const bcs = [1600].concat(Array(9).fill(Math.floor((TOTAL - 1600) / 9)));
  bcs[9] += TOTAL - bcs.reduce((a, b) => a + b, 0);
  const bcsRow = [cell("BCS (9점)", { w: bcs[0], bold: true, size: 16, color: BLUE_DK, fill: BLUE_BG })]
    .concat(Array.from({ length: 9 }, (_, i) => cell(`□ ${i + 1}`, { w: bcs[i + 1], size: 16 })));
  const doc = buildDoc([
    ...header("영양 평가 · BCS / MCS 기록지",
      "WSAVA 영양 평가 가이드라인(2011, JSAP) · 글로벌 영양 툴킷 기반 (참고용) — 모든 환자, 모든 내원 시 스크리닝 / 서식번호 KAHA-F-2603"),
    sectionBar("환자 정보"),
    table([1900, 1750, 1300, 1650, 900, 1000, 900, 690 + 2000 - 2000], [[
      cell("동물명 / 차트번호", { w: 1900, label: true }), cell("", { w: 1750 }),
      cell("종 / 품종", { w: 1300, label: true }), cell("", { w: 1650 }),
      cell("연령", { w: 900, label: true }), cell("", { w: 1000 }),
      cell("중성화", { w: 900, label: true }), cell("□ 예  □ 아니오", { w: 690 }),
    ]]),
    gap(),
    sectionBar("1. 식이 이력"),
    table([2000, 3400, 2000, 2690], [
      [cell("주식 (제품명 · 형태)", { w: 2000, label: true }), cell("", { w: 3400 }), cell("1일 급여량 / 횟수", { w: 2000, label: true }), cell("", { w: 2690 })],
      [cell("간식 · 사람 음식", { w: 2000, label: true }), cell("", { w: 3400 }), cell("영양제 · 보조제", { w: 2000, label: true }), cell("", { w: 2690 })],
      [cell("식욕 변화", { w: 2000, label: true }), cell("□ 없음  □ 증가  □ 감소 (기간: ______)", { w: 3400, size: 16 }),
       cell("음수량 변화", { w: 2000, label: true }), cell("□ 없음  □ 증가  □ 감소", { w: 2690, size: 16 })],
    ]),
    gap(),
    sectionBar("2. 체중 및 신체 평가"),
    table([1800, 1800, 2100, 2100, 1200, 1090], [[
      cell("금일 체중(kg)", { w: 1800, label: true }), cell("", { w: 1800 }),
      cell("직전 체중 / 측정일", { w: 2100, label: true }), cell("", { w: 2100 }),
      cell("변화율(%)", { w: 1200, label: true }), cell("", { w: 1090 }),
    ]]),
    table(bcs, [bcsRow]),
    para("1–3 저체중 · 4–5 이상적 · 6–7 과체중 · 8–9 비만  (갈비뼈 촉진, 허리 라인, 복부 턱업으로 판정)", { size: 14, color: GREY }),
    table([2000, 8090], [[
      cell("MCS (근육상태)", { w: 2000, label: true }),
      cell("□ 정상      □ 경도 소실      □ 중등도 소실      □ 중증 소실", { w: 8090 }),
    ]]),
    para("척추 · 견갑 · 측두부 · 골반 촉진으로 판정 — 비만 개체도 근소실이 동반될 수 있습니다 (특히 고령 · 만성질환).", { size: 14, color: GREY }),
    gap(),
    sectionBar("3. 위험요인 스크리닝  (하나라도 해당 시 확장 평가)"),
    table([TOTAL], [[cell("□ 질병(만성 포함)     □ 고령     □ 비만 / 저체중     □ 수제식 · 생식 · 비전형 식이     □ 피모 · 치아 이상     □ 체중 급변", { w: TOTAL })]]),
    gap(),
    sectionBar("4. 평가 결과 및 계획"),
    table(c2, [
      [cell("확장 평가 필요", { w: c2[0], label: true }), cell("□ 불필요       □ 필요  ( 사유 : ______________________________ )", { w: c2[1] })],
      [cell("권장 사료 · 급여량", { w: c2[0], label: true }), cell("", { w: c2[1], empty: 1 })],
      [cell("목표 체중 · 재평가 일정", { w: c2[0], label: true }), cell("", { w: c2[1], empty: 1 })],
      [cell("보호자 상담 내용", { w: c2[0], label: true }), cell("", { w: c2[1], empty: 2 })],
    ]),
    gap(),
    table([1200, 3200, 1200, 4490], [[
      cell("평가일", { w: 1200, label: true }), cell("20____년  ____월  ____일", { w: 3200 }),
      cell("평가자", { w: 1200, label: true }), cell("성명 : ______________ (서명)", { w: 4490 }),
    ]]),
    footerPara("KAHA-F-2603"),
  ]);
  Packer.toBuffer(doc).then((b) => fs.writeFileSync(path.join(OUT, "nutrition-assessment-chart.docx"), b));
})();

console.log("워드 양식 3종 생성 요청 완료");

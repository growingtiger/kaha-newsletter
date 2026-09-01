// KAHA 양식 워드(.docx) 생성 — 협회 사무국 표준 서식(form_style_docx.js) 기준.
// PDF(tools/make_forms.py)와 같은 구성으로 나온다.
// 실행: node tools/make_forms_docx.js   (필요 패키지: docx)
const S = require("./form_style_docx");
const {
  TOTAL, LABEL_BG, AlignmentType, para, centered, cell, plainCell, table, gap,
  titleBlock, infoTable, sec, bulletLines, fieldTable, recTable, asaTable,
  closing, signRow, buildDoc,
} = S;

const LB = 1928;                 // 구획 라벨 열 폭 (34mm)
const CW = TOTAL - LB;           // 구획 내용 폭
const IW = CW - 240;             // 구획 안쪽 실제 사용 폭
const mm = (v) => Math.round(v * 56.7);

// 인적사항 표 열 폭 (라벨 28mm · 항목 26mm · 값 균등)
const L = mm(26), M = mm(30);
const V = Math.floor((TOTAL - L - 2 * M) / 2);
const IN_W = [L, M, V, M, TOTAL - L - 2 * M - V];

const jobs = [];

// ═══ 1. 수술등중대진료(마취) 동의서 ════════════════════════════════
{
  const body = [].concat(
    titleBlock("수술등중대진료(마취) 동의서",
      "본 동의서는 「수의사법」 제13조의2 및 같은 법 시행규칙 제13조의2에 따라 작성되었습니다.", 40),
    [
      infoTable([
        ["보호자", [["성명", "", "연락처", ""], ["주소", "", null, null]]],
        ["반려동물", [["이름", "", "종 / 품종", ""], ["성별 / 중성화", "□ 암  □ 수       □ 중성화", "연령 / 체중", ""],
                     ["특이사항", "", null, null]]],
        ["수의사", [["동물병원명", "", "수의사 성명", ""], ["면허번호", "", null, null]]],
      ], IN_W, 455),
      gap(70),
      sec("설명 및\n동의사항", bulletLines([
        "위 반려동물의 수술등중대진료를 위해 전신마취가 필요합니다.",
        "마취 중 심정지가 발생할 경우 아래 처치에 동의합니다.",
      ]).concat([para("", { size: 8 })]).concat(
        bulletLines(["심폐소생술 원함          □ 심폐소생술 원하지 않음"], { marker: "□ " })),
        { note: "동의하시는 부분에\n체크해주세요.", height: mm(19) }),
      gap(70),
      sec("수술등중대진료의\n필요성 ·\n방법 및 내용", [
        fieldTable([
          [{ text: "진단명", label: true }, "", { text: "예정 일시", label: true }, ""],
          [{ text: "수술 / 처치명", label: true }, "", { text: "마취 방식", label: true }, ""],
          [{ text: "필요성", label: true }, "", null, null],
          [{ text: "방법 및 내용", label: true }, "", null, null],
        ], [mm(25), Math.floor((IW - mm(45)) / 2), mm(20), IW - mm(45) - Math.floor((IW - mm(45)) / 2)],
          [mm(7.2), mm(7.2), mm(8), mm(8)]),
      ], { height: mm(33) }),
      gap(70),
      sec("수술등중대진료에\n따라 전형적으로\n발생이 예상되는\n후유증 또는 부작용", [
        fieldTable([
          [{ text: "1) 저혈압, 저체온, 고체온", size: 15 }, { text: "2) 약물과민반응에 의한 쇼크", size: 15 }, { text: "3) 순환부전에 의한 쇼크", size: 15 }],
          [{ text: "4) 췌장염, 신부전 및 폐수종", size: 15 }, { text: "5) 기저질환 발현 및 현증악화", size: 15 }, { text: "6) 삽관에 의한 일시적 기침", size: 15 }],
        ], [Math.floor(IW / 3), Math.floor(IW / 3), IW - 2 * Math.floor(IW / 3)], mm(5.4)),
        para("", { size: 8 }),
        asaTable(IW, mm(4.8)),
      ], { height: mm(43.5) }),
      gap(70),
      sec("수술등중대진료\n전후에 보호자의\n준수 및 숙지사항",
        bulletLines([
          "마취 시 수술 전 일정 시간의 금식과 금수가 필수적입니다.",
          "마취로 발생할 수 있는 부작용 · 합병증 · 후유증에 대한 설명을 충분히 듣고 이해했습니다.",
          "마취 과정에서 불가항력적이거나 환자의 특이체질로 인한 우발사고의 가능성을 인정합니다.",
          "보호자의 자유 의사에 의하여 마취를 시행하는 것에 동의합니다.",
          "마취 및 수술비 설명을 들었으며, 필요시 구두 동의 하에 추가 검사 · 추가 수술 진행에 동의합니다.",
        ], { size: 15, lineH: 250 }), { height: mm(29.5) }),
      gap(220),
      table([TOTAL], [[plainCell(closing(
        "「수의사법」 제13조의2 및 같은 법 시행규칙 제13조의2에 따라 위와 같이 수의사로부터 수술등중대진료의 필요성 · 방법 · 내용과 전형적으로 발생이 예상되는 후유증 및 부작용에 관한 설명을 충분히 듣고 이해하였습니다. 이에 위 수술등중대진료 및 마취의 시행에 동의하며, 시행 과정에서 필요한 수의학적 판단과 처리를 담당 수의사에게 위임합니다."),
        { w: TOTAL, margins: { top: 0, bottom: 0, left: 0, right: 0 } })]], mm(17)),
      gap(180),
      signRow(["보호자", "설명 수의사"]),
    ]);
  jobs.push(buildDoc("수술등중대진료(마취) 동의서", body, "01_수술마취/마취동의서_한국동물병원협회.docx"));
}

// ═══ 2. 입원 동의서 ════════════════════════════════════════════════
{
  const lw = mm(24), vw = Math.floor((IW - lw * 2) / 2);
  const W4 = [lw, vw, lw, IW - lw * 2 - vw];
  const body = [].concat(
    titleBlock("입원 동의서",
      "본 동의서는 입원 진료의 내용 · 비용 · 연락 방식에 관한 설명과 동의를 확인하기 위해 작성되었습니다.", 44),
    [
      infoTable([
        ["보호자", [["성명", "", "연락처", ""], ["주소", "", "제2연락처", ""]]],
        ["반려동물", [["이름", "", "종 / 품종", ""], ["성별 / 중성화", "□ 암  □ 수       □ 중성화", "연령 / 체중", ""]]],
        ["수의사", [["동물병원명", "", "담당 수의사", ""]]],
      ], IN_W, 470),
      gap(115),
      sec("입원 사유 및\n예상 기간", [fieldTable([
        [{ text: "추정 진단명", label: true }, "", { text: "입원 목적", label: true }, ""],
        [{ text: "예상 입원 기간", label: true }, "약 ______ 일        ( 20____. ____. ____.  ～  20____. ____. ____. )", null, null],
      ], W4, mm(8))], { height: mm(18.5) }),
      gap(115),
      sec("비용 안내", [
        fieldTable([
          [{ text: "1일 입원비", label: true }, "____________ 원", { text: "예상 총액", label: true }, "____________ 원"],
          [{ text: "입원비 포함 항목", label: true }, { text: "", top: true }, null, null],
          [{ text: "별도 청구 항목", label: true }, "□ 검사    □ 처치    □ 약제    □ 수혈    □ 기타 :", null, null],
        ], [lw + mm(6), vw - mm(6), lw, IW - lw * 2 - vw], [mm(8), mm(11), mm(8)]),
        para("", { size: 8 }),
      ].concat(bulletLines(["예상액의 ______ % 또는 ____________ 원을 초과할 것으로 예상되면 진행 전에 보호자에게 연락합니다."],
        { size: 15 })), { height: mm(35) }),
      gap(115),
      sec("경과 보고 및\n연락 방식", bulletLines([
        "정기 보고 : □ 1일 1회  □ 1일 2회  □ 기타 ______",
        "보고 방법 : □ 전화  □ 문자 · 메신저  □ 면회 시 구두",
        "상태가 급변하면 즉시 연락합니다.",
        "연락 불통 시 : □ 수의사 판단으로 필요한 처치 시행  □ 응급처치만 시행 후 재연락",
      ], { size: 15, lineH: 260 }), { height: mm(22) }),
      gap(115),
      sec("면회 · 반입물품 ·\n야간 관리", bulletLines([
        "면회 가능 시간 : __________    면회 제한 사유 : □ 감염  □ 중환자  □ 기타",
        "반입물품(사료 · 약 · 담요 등) : ______________   ※ 분실 시 병원이 책임지지 않을 수 있습니다.",
        "야간 · 휴일 관리 :  □ 수의사 상주   □ 간호인력 상주   □ 무인 관리 ( ____시 최종 처치 → ____시 확인 )",
      ], { size: 15, lineH: 260 }), { height: mm(22) }),
      gap(115),
      sec("응급 상황 및\n사망 시 처리", bulletLines([
        "심정지 시 심폐소생술(CPR) :  □ 시행   □ 시행하지 않음(DNR)",
        "생명 유지에 필요한 응급처치는 연락 전 시행하는 것에 동의합니다.",
        "사망 시 :  □ 사체 인도 희망   □ 병원 위탁 처리   □ 동물장묘업 등록 시설 이용 안내 희망",
      ], { size: 15, lineH: 260 }), { height: mm(19) }),
      gap(115),
      sec("입원 중\n중대진료가\n필요해지는 경우", bulletLines([
        "전신마취를 동반하는 내부장기 · 뼈 · 관절 수술 또는 전신마취를 동반하는 수혈이 필요해지면, 「수의사법」 제13조의2에 따라 별도의 수술등중대진료 동의서를 작성합니다. 본 입원 동의서가 이를 대신하지 않습니다.",
      ], { size: 15, lineH: 260 }), { height: mm(18) }),
      gap(220),
      table([TOTAL], [[plainCell(closing(
        "위와 같이 입원 진료의 내용과 예상 비용, 경과 보고 및 연락 방식, 응급 상황에서의 처리에 관하여 수의사로부터 설명을 충분히 듣고 이해하였으며, 위 조건에 따른 입원 진료에 동의합니다."),
        { w: TOTAL, margins: { top: 0, bottom: 0, left: 0, right: 0 } })]], mm(14)),
      gap(180),
      signRow(["보호자", "설명 수의사"]),
    ]);
  jobs.push(buildDoc("입원 동의서", body, "02_입원응급/입원동의서_한국동물병원협회.docx"));
}

// ═══ 3. 퇴원 안내문 ════════════════════════════════════════════════
{
  const lw = mm(26);
  const medW = [mm(22), mm(24), mm(16), mm(12), mm(15), mm(17), mm(16)];
  medW.push(IW - medW.reduce((a, b) => a + b, 0));
  const calW = [mm(18)].concat(Array(7).fill(Math.floor((IW - mm(18)) / 7)));
  calW[7] += IW - calW.reduce((a, b) => a + b, 0);
  const rw = mm(24), rv = mm(46);
  const body = [].concat(
    titleBlock("퇴원 안내문",
      "본 안내문은 가정에서의 투약과 관리, 재진 일정에 관한 설명 내용을 기록하기 위해 작성되었습니다.", 44),
    [
      infoTable([
        ["보호자", [["성명", "", "연락처", ""]]],
        ["반려동물", [["이름", "", "종 / 품종", ""], ["차트번호", "", "퇴원 일시", ""]]],
        ["수의사", [["동물병원명", "", "담당 수의사", ""]]],
      ], IN_W, 505),
      gap(120),
      sec("진단명 및\n시행한 처치", [fieldTable([
        [{ text: "진단명 / 처치", label: true }, "", null, null],
        [{ text: "퇴원 시점 상태", label: true }, "□ 각성   □ 반응 있음   □ 체온 회복   □ 통증 조절됨",
         { text: "마취 시행", label: true }, "□ 예   □ 아니오"],
      ], [lw, IW - lw - mm(18) - mm(24), mm(18), mm(24)], mm(9.5))], { height: mm(21) }),
      gap(120),
      sec("가정 투약 안내", [
        recTable(["약품명", "무엇 때문에", "1회 용량", "경로", "1일 횟수", "종료일", "식전/식후", "주의할 점"],
          medW, 3, mm(7), mm(5.6)),
        para("", { size: 8 }),
      ].concat(bulletLines(["퇴원 전 경구약 투여 방법을 보호자가 직접 해보고 확인하였습니다.",
        "약 보관 방법을 안내하였습니다."], { size: 15, marker: "□ " })), { height: mm(41) }),
      gap(120),
      sec("투약 체크 달력", [fieldTable([
        [{ text: "", label: true }].concat([1, 2, 3, 4, 5, 6, 7].map((i) => ({ text: i + "일차", label: true, size: 14, align: AlignmentType.CENTER }))),
        [{ text: "아침", label: true }].concat(Array(7).fill("")),
        [{ text: "저녁", label: true }].concat(Array(7).fill("")),
      ], calW, [mm(5.6), mm(7), mm(7)])], { note: "투여 후 표시하세요", height: mm(23) }),
      gap(120),
      sec("가정 관리", bulletLines([
        "활동 제한 :  □ 산책 제한   □ 계단 · 점프 금지   □ 목줄 산책만        기간 : ________",
        "넥카라 · 수술복 :  □ 착용 필요 ( 기간 : ________ )   □ 해당 없음",
        "절개 부위 :  □ 물 닿지 않게   □ 소독 : ____________        목욕 가능 시점 : ________",
        "식이 · 급수 : ______________________________________________________________",
        "배뇨 · 배변 · 식욕 · 활력에 변화가 있으면 기록해 주세요.",
      ], { size: 15, lineH: 250 }), { height: mm(25) }),
      gap(120),
      sec("재진 및\n응급 연락", [fieldTable([
        [{ text: "다음 내원일", label: true }, "20____. ____. ____.    ____시",
         { text: "재진 목적", label: true }, "□ 경과 확인  □ 봉합사 제거  □ 재검사"],
        [{ text: "즉시 연락할 증상", label: true }, { text: "", top: true }, null, null],
        [{ text: "병원 연락처", label: true }, "", { text: "야간 · 휴일", label: true }, ""],
      ], [rw + mm(4), rv, rw, IW - rw * 2 - rv - mm(4)], [mm(9.5), mm(12), mm(8)])],
        { height: mm(33) }),
      gap(220),
      table([TOTAL], [[plainCell(closing(
        "위 내용을 안내문과 함께 읽으며 설명하였고, 보호자가 이를 이해하였음을 확인합니다. 마취 후에는 회복기에 상태가 변할 수 있으므로 퇴원 후 몇 시간 동안 특히 주의 깊게 지켜봐 주십시오."),
        { w: TOTAL, margins: { top: 0, bottom: 0, left: 0, right: 0 } })]], mm(11)),
      gap(180),
      signRow(["보호자", "설명자"]),
    ]);
  jobs.push(buildDoc("퇴원 안내문", body, "02_입원응급/퇴원안내문_한국동물병원협회.docx"));
}

// ═══ 4. 마취 전 평가 · 모니터링 체크리스트 ═════════════════════════
{
  const lw = mm(26);
  const v3 = Math.floor((IW - lw) / 3);
  const monW = [mm(16), mm(14), mm(14), mm(16), mm(16), mm(18), mm(16)];
  monW.push(IW - monW.reduce((a, b) => a + b, 0));
  const body = [].concat(
    titleBlock("마취 전 평가 · 모니터링 체크리스트",
      "본 기록지는 마취 전 준비와 마취 중 경과, 회복기 관리를 원내에서 기록하기 위한 서식입니다.", 34),
    [
      infoTable([
        ["반려동물", [["이름 / 차트번호", "", "종 / 품종", ""], ["성별 / 중성화", "□ 암  □ 수       □ 중성화", "연령 / 체중", ""]]],
        ["수의사", [["동물병원명", "", "담당 수의사", ""]]],
      ], IN_W, 570),
      gap(120),
      sec("환자 평가", [
        fieldTable([
          [{ text: "병력 · 현재 투약", label: true }, { text: "", top: true }, null, null],
          [{ text: "신체검사 요약", label: true }, { text: "", top: true }, null, null],
          [{ text: "사전 혈액검사", label: true }, "□ CBC    □ 혈액화학    □ 전해질    □ 응고계    □ 기타 :", null, null],
        ], [lw, v3, v3, IW - lw - 2 * v3], [mm(10), mm(10), mm(7)]),
        para("", { size: 10 }),
        asaTable(IW, mm(5)),
      ], { height: mm(63) }),
      gap(120),
      sec("마취 전 준비", bulletLines([
        "금식 확인 — 음식 ______ 시간 · 물 ______ 시간   (병원 프로토콜 기준)",
        "IV 카테터 장착      □ 기관튜브 3종 준비 ( ____ / ____ / ____ )      □ 응급약물 용량 사전 계산 · 비치",
        "마취 회로 · 산소 · 흡인기 점검      □ 항불안 처치 필요 여부 평가 (겁 많음 · 공격성)",
        "보호자 설명 및 수술등중대진료(마취) 동의서 작성 완료",
      ], { size: 15, marker: "□ ", lineH: 260 }), { height: mm(25) }),
      gap(120),
      sec("마취 중\n모니터링 기록", [
        recTable(["시각", "HR", "RR", "SpO2", "EtCO2", "혈압", "체온", "마취심도 · 처치 · 비고"],
          monW, 7, mm(6.2), mm(8)),
        para("", { size: 8 }),
      ].concat(bulletLines(["저체온과 저혈압은 가장 흔한 마취 중 합병증입니다. 조기 인지와 가온 · 수액 대응 프로토콜을 준비하십시오."],
        { size: 13, marker: "※ " })), { note: "15분 간격 권장", height: mm(63) }),
      gap(120),
      sec("회복기 관리", bulletLines([
        "발관 시각 : ________      □ 체온 회복 확인 ( ________ ℃ )      □ 통증 평가 ( 도구 / 점수 : ____________ )",
        "의식 · 기립 확인      □ 퇴원 전 보호자 주의사항 전달",
      ], { size: 15, marker: "□ ", lineH: 260 }), { note: "마취 관련 사망 위험이\n높은 구간 — 담당자 지정", height: mm(16) }),
      gap(230),
      signRow(["마취 담당", "회복기 담당"]),
    ]);
  jobs.push(buildDoc("마취 전 평가·모니터링 체크리스트", body, "06_진료기록/마취전평가체크리스트_한국동물병원협회.docx"));
}

// ═══ 5. 영양 평가 · BCS / MCS 기록지 ═══════════════════════════════
{
  const lw = mm(28), vw = Math.floor((IW - lw * 2) / 2);
  const lw2 = mm(26), v3 = Math.floor((IW - mm(78)) / 3);
  const bcsW = [mm(22)].concat(Array(9).fill(Math.floor((IW - mm(22)) / 9)));
  bcsW[9] += IW - bcsW.reduce((a, b) => a + b, 0);
  const lw3 = mm(32), hv = Math.floor((IW - lw3) / 2);
  const body = [].concat(
    titleBlock("영양 평가 · BCS / MCS 기록지",
      "본 기록지는 모든 환자의 영양 상태를 내원 시마다 선별하고 기록하기 위한 서식입니다.", 38),
    [
      infoTable([
        ["반려동물", [["이름 / 차트번호", "", "종 / 품종", ""], ["연령", "", "중성화", "□ 예     □ 아니오"]]],
        ["수의사", [["동물병원명", "", "평가자", ""]]],
      ], IN_W, 690),
      gap(170),
      sec("식이 이력", [fieldTable([
        [{ text: "주식 (제품명 · 형태)", label: true }, "", { text: "1일 급여량 / 횟수", label: true }, ""],
        [{ text: "간식 · 사람 음식", label: true }, "", { text: "영양제 · 보조제", label: true }, ""],
        [{ text: "식욕 변화", label: true }, "□ 없음  □ 증가  □ 감소 (기간 : ______)",
         { text: "음수량 변화", label: true }, "□ 없음  □ 증가  □ 감소"],
      ], [lw, vw, lw, IW - lw * 2 - vw], mm(10))], { height: mm(35) }),
      gap(170),
      sec("체중 및\n신체 평가", [
        fieldTable([[{ text: "금일 체중(kg)", label: true }, "", { text: "직전 체중 / 측정일", label: true }, "",
                     { text: "변화율(%)", label: true }, ""]],
          [lw2, v3, mm(30), v3, mm(22), IW - lw2 - mm(52) - 2 * v3], mm(9)),
        para("", { size: 8 }),
        fieldTable([[{ text: "BCS (9점)", label: true, size: 15 }].concat(
          [1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => ({ text: "□ " + i, size: 15 })))], bcsW, mm(8)),
        para("1–3 저체중 · 4–5 이상적 · 6–7 과체중 · 8–9 비만 (갈비뼈 촉진, 허리 라인, 복부 턱업으로 판정)",
          { size: 13, color: S.SOFT }),
        fieldTable([[{ text: "MCS (근육상태)", label: true },
                     "□ 정상        □ 경도 소실        □ 중등도 소실        □ 중증 소실", null, null]],
          [lw2 + mm(4), v3, v3, IW - lw2 - mm(4) - 2 * v3], mm(8)),
        para("척추 · 견갑 · 측두부 · 골반 촉진으로 판정 — 비만 개체도 근소실이 동반될 수 있습니다 (특히 고령 · 만성질환).",
          { size: 13, color: S.SOFT }),
      ], { height: mm(38) }),
      gap(170),
      sec("위험요인\n스크리닝", bulletLines([
        "□ 질병(만성 포함)    □ 고령    □ 비만 / 저체중    □ 수제식 · 생식 · 비전형 식이    □ 피모 · 치아 이상    □ 체중 급변",
      ], { size: 15, marker: "" }), { note: "하나라도 해당 시\n확장 평가", height: mm(16.5) }),
      gap(170),
      sec("평가 결과 및 계획", [fieldTable([
        [{ text: "확장 평가 필요", label: true }, "□ 불필요        □ 필요  ( 사유 : ________________________________ )", null],
        [{ text: "권장 사료 · 급여량", label: true }, { text: "", top: true }, null],
        [{ text: "목표 체중 · 재평가 일정", label: true }, { text: "", top: true }, null],
        [{ text: "보호자 상담 내용", label: true }, { text: "", top: true }, null],
      ], [lw3, hv, IW - lw3 - hv], [mm(9), mm(15), mm(15), mm(26)])], { height: mm(67.5) }),
      gap(170),
      signRow(["평가자"]),
    ]);
  jobs.push(buildDoc("영양 평가·BCS/MCS 기록지", body, "06_진료기록/영양평가기록지_한국동물병원협회.docx"));
}

// ═══ 6. 개인정보 수집·이용 동의서 (보호자용) ══════════════════════
{
  const lw = mm(26);
  const body = [].concat(
    titleBlock("개인정보 수집·이용 동의서",
      "본 동의서는 「개인정보 보호법」에 따라 진료 예약·안내 등에 필요한 보호자 개인정보의 수집·이용에 대한 동의를 확인하기 위해 작성되었습니다.", 36),
    [
      infoTable([
        ["보호자", [["성명", "", "연락처", ""], ["주소", "", null, null]]],
        ["반려동물", [["이름", "", "종 / 품종", ""]]],
        ["수의사", [["동물병원명", "", null, null]]],
      ], IN_W, mm(10)),
      gap(170),
      sec("수집·이용\n목적", bulletLines([
        "진료 예약의 확인 · 변경 · 취소 안내",
        "진료기록 작성 · 관리 및 진료비 정산",
        "검사 결과, 투약 · 재진 일정 등 진료 관련 안내(전화 · 문자)",
        "응급 상황 발생 시 보호자 연락",
      ], { size: 15, lineH: 270 }), { height: mm(23) }),
      gap(170),
      sec("수집 항목", [fieldTable([
        [{ text: "필수 항목", label: true }, "성명, 연락처, 주소, 반려동물 정보(이름 · 종 / 품종)"],
        [{ text: "선택 항목", label: true }, "이메일 주소 (검사 결과지 · 안내자료 전송 시)"],
      ], [lw, IW - lw], [mm(9), mm(9)])], { height: mm(20) }),
      gap(170),
      sec("보유 및\n이용 기간", bulletLines([
        "수집한 개인정보는 아래에서 선택한 기간 동안 보유 · 이용한 뒤 지체 없이 파기합니다.",
        "□ 최종 진료일로부터 ______ 년      □ 폐업 시까지      □ 동의 철회 시까지",
      ], { size: 15, lineH: 260 }), { height: mm(15) }),
      gap(170),
      sec("제3자 제공 및\n안내 문자 발송", bulletLines([
        "수집한 개인정보는 위 목적 범위에서만 이용하며, 원칙적으로 제3자에게 제공하지 않습니다.",
        "다만 법령에 근거가 있거나 응급 상황에서 생명 · 신체의 위험을 막기 위해 필요한 경우는 예외로 합니다.",
        "건강관리 · 이벤트 등 안내 문자 발송에는 별도로 동의합니다.   □ 동의   □ 동의하지 않음",
      ], { size: 14, lineH: 240 }), { height: mm(19.5) }),
      gap(170),
      sec("동의 거부 권리 및\n열람 · 정정 요청", bulletLines([
        "위 개인정보 수집 · 이용에 동의하지 않을 권리가 있습니다.",
        "다만 필수 항목에 동의하지 않으면 진료 예약, 진료기록 관리, 진료비 정산 등 병원 이용에 제한이 있을 수 있습니다.",
        "보호자는 병원에 본인의 개인정보 열람 · 정정 · 삭제를 요청할 수 있습니다.",
      ], { size: 15, lineH: 260 }), { height: mm(21) }),
      gap(220),
      table([TOTAL], [[plainCell(closing(
        "위와 같이 개인정보의 수집 · 이용 목적, 항목, 보유 및 이용 기간과 동의 거부 권리에 관하여 안내받았으며, 이를 이해하고 위 내용에 따른 개인정보 수집 · 이용에 동의합니다."),
        { w: TOTAL, margins: { top: 0, bottom: 0, left: 0, right: 0 } })]], mm(15)),
      gap(180),
      signRow(["보호자"]),
    ]);
  jobs.push(buildDoc("개인정보 수집·이용 동의서", body, "04_병원운영/개인정보수집이용동의서_한국동물병원협회.docx"));
}

Promise.all(jobs).then(() => console.log("워드 양식 6종 생성 완료"))
  .catch((e) => { console.error(e.message); process.exit(1); });

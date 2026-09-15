// 양식 전체를 한 번에 내려받을 수 있는 압축 파일을 만든다.
//
// 이 파일은 **저장소에 커밋하지 않는다**(.gitignore). 배포할 때 Vercel 이 이
// 스크립트를 돌려 새로 만든다. 예전에는 58MB 짜리 zip 을 양식 고칠 때마다
// 커밋했는데, 저장소가 무거워져 일일 발행 루틴의 클론이 위태로워졌다.
//
// 로컬에서도 같은 스크립트를 쓴다(tools/build_all.sh 의 마지막 단계).
// 파이썬 대신 Node 로 쓴 이유는 Vercel 빌드 환경에 Node 가 반드시 있기 때문이다.
// 외부 패키지 없이 기본 모듈(zlib)만 쓴다.
//
// 실행: node tools/make_forms_zip.js
"use strict";
const fs = require("fs");
const path = require("path");
const zlib = require("zlib");

const BASE = path.dirname(__dirname);
const FORMS = path.join(BASE, "forms");
const OUT_DIR = path.join(BASE, "downloads");
const OUT_NAME = "KAHA_양식모음_전체_한국동물병원협회.zip";

// 내용이 같으면 파일도 같게 나오도록 시각을 고정한다
const DOS_TIME = 0;
const DOS_DATE = ((2026 - 1980) << 9) | (1 << 5) | 1;

const crc32 = zlib.crc32 ? (buf) => zlib.crc32(buf) >>> 0 : (() => {
  const T = new Int32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
    T[i] = c;
  }
  return (buf) => {
    let c = -1;
    for (let i = 0; i < buf.length; i++) c = T[(c ^ buf[i]) & 0xff] ^ (c >>> 8);
    return (c ^ -1) >>> 0;
  };
})();

function walk(dir, out) {
  for (const n of fs.readdirSync(dir).sort()) {
    const p = path.join(dir, n);
    const st = fs.statSync(p);
    if (st.isDirectory()) walk(p, out);
    else if (/\.(pdf|docx)$/i.test(n)) out.push(p);
  }
  return out;
}

function readme(manifest, date, count) {
  const lines = [];
  for (const g of manifest.groups) {
    if (g.external) continue;   // 정부·유관기관 서식은 협회가 배포하지 않는다
    lines.push("", "[" + g.label + "]");
    for (const c of g.cats) {
      lines.push("  " + c.label + " (" + c.items.length + "종)");
      for (const it of c.items) lines.push("    - " + it.name);
    }
  }
  return "한국동물병원협회(KAHA) 회원병원 양식 모음\n"
    + date + " 기준 · 양식 " + count + "종 (PDF + 워드 각 1개)\n\n"
    + "- PDF : 그대로 인쇄해서 쓰시는 용도입니다.\n"
    + "- 워드: 병원 사정에 맞게 고쳐 쓰시는 용도입니다.\n"
    + "- 모든 문서는 A4 한 장에 맞춰 만들었습니다.\n"
    + "- 법령·고시가 정한 정부 서식(진단서·처방전·개설신고서 등)은 협회가 배포할 수\n"
    + "  없으므로 이 압축 파일에 들어 있지 않습니다. 자료실 화면의\n"
    + "  「정부 · 유관기관 공식 서식」 목록에서 받는 곳을 안내해 두었습니다.\n\n"
    + "문의 · 최신본 확인: 사단법인 한국동물병원협회\n\n"
    + "────────────────────────────────────────\n수록 목록\n"
    + "────────────────────────────────────────\n"
    + lines.join("\n") + "\n";
}

function main() {
  const manifest = JSON.parse(fs.readFileSync(path.join(BASE, "forms.json"), "utf8"));
  fs.mkdirSync(OUT_DIR, { recursive: true });
  const out = path.join(OUT_DIR, OUT_NAME);

  const files = walk(FORMS, []).map((p) => [p, path.relative(BASE, p)]);
  files.sort((a, b) => (a[1] < b[1] ? -1 : a[1] > b[1] ? 1 : 0));

  let newest = 0;
  for (const [p] of files) newest = Math.max(newest, fs.statSync(p).mtimeMs);
  const date = process.env.KAHA_BUILD_DATE
    || new Date(newest).toISOString().slice(0, 10);

  const entries = [["KAHA_양식모음_안내.txt", Buffer.from(readme(manifest, date, manifest.count), "utf8")]];
  for (const [p, rel] of files) entries.push([rel, null, p]);

  const fd = fs.openSync(out, "w");
  let offset = 0;
  const central = [];
  const w = (buf) => { fs.writeSync(fd, buf); offset += buf.length; };

  for (const [name, inline, src] of entries) {
    const raw = inline || fs.readFileSync(src);
    const comp = zlib.deflateRawSync(raw, { level: 6 });
    const nameBuf = Buffer.from(name, "utf8");
    const crc = crc32(raw);
    const localOffset = offset;

    const lh = Buffer.alloc(30);
    lh.writeUInt32LE(0x04034b50, 0);
    lh.writeUInt16LE(20, 4);
    lh.writeUInt16LE(0x0800, 6);      // 파일명이 UTF-8 임을 알린다 (한글 깨짐 방지)
    lh.writeUInt16LE(8, 8);           // deflate
    lh.writeUInt16LE(DOS_TIME, 10);
    lh.writeUInt16LE(DOS_DATE, 12);
    lh.writeUInt32LE(crc, 14);
    lh.writeUInt32LE(comp.length, 18);
    lh.writeUInt32LE(raw.length, 22);
    lh.writeUInt16LE(nameBuf.length, 26);
    lh.writeUInt16LE(0, 28);
    w(lh); w(nameBuf); w(comp);

    const ch = Buffer.alloc(46);
    ch.writeUInt32LE(0x02014b50, 0);
    ch.writeUInt16LE(20, 4);
    ch.writeUInt16LE(20, 6);
    ch.writeUInt16LE(0x0800, 8);
    ch.writeUInt16LE(8, 10);
    ch.writeUInt16LE(DOS_TIME, 12);
    ch.writeUInt16LE(DOS_DATE, 14);
    ch.writeUInt32LE(crc, 16);
    ch.writeUInt32LE(comp.length, 20);
    ch.writeUInt32LE(raw.length, 24);
    ch.writeUInt16LE(nameBuf.length, 28);
    ch.writeUInt16LE(0, 30);
    ch.writeUInt16LE(0, 32);
    ch.writeUInt16LE(0, 34);
    ch.writeUInt16LE(0, 36);
    ch.writeUInt32LE(0o644 << 16, 38);
    ch.writeUInt32LE(localOffset, 42);
    central.push(Buffer.concat([ch, nameBuf]));
  }

  const cdOffset = offset;
  for (const c of central) w(c);
  const cdSize = offset - cdOffset;

  const eocd = Buffer.alloc(22);
  eocd.writeUInt32LE(0x06054b50, 0);
  eocd.writeUInt16LE(0, 4);
  eocd.writeUInt16LE(0, 6);
  eocd.writeUInt16LE(central.length, 8);
  eocd.writeUInt16LE(central.length, 10);
  eocd.writeUInt32LE(cdSize, 12);
  eocd.writeUInt32LE(cdOffset, 16);
  eocd.writeUInt16LE(0, 20);
  w(eocd);
  fs.closeSync(fd);

  const size = fs.statSync(out).size;
  console.log("압축 파일 생성 — " + OUT_NAME);
  console.log("  문서 " + files.length + "개 · " + (size / 1048576).toFixed(1) + " MB");

  // 화면에서 크기를 보여줄 수 있도록 forms.json 에 적어 둔다
  manifest.bundle = { path: "downloads/" + OUT_NAME, bytes: size, files: files.length, date: date };
  fs.writeFileSync(path.join(BASE, "forms.json"),
    JSON.stringify(manifest) + "\n", "utf8");
  console.log("  forms.json 에 기록: " + manifest.bundle.path);
}

main();

#!/bin/sh
# 양식 전체를 다시 만들고 검사한다. 순서가 중요하다 — 압축 파일은 반드시 맨 마지막이다.
#
#   sh tools/build_all.sh
#
set -e
cd "$(dirname "$0")/.."

echo "── 1. 데이터 반영"
python3 tools/apply_proc_about.py

echo "── 2. PDF"
python3 tools/make_forms.py            > /dev/null
python3 tools/make_procedure_forms.py  | tail -1
python3 tools/make_disease_guides.py   | tail -1
python3 tools/make_admin_forms.py      | tail -1

echo "── 3. 워드"
node tools/make_forms_docx.js          | tail -1
node tools/make_procedure_forms_docx.js| tail -1
node tools/make_guide_admin_docx.js    | tail -1

echo "── 4. 목록(forms.json)"
python3 tools/make_forms_manifest.py   | head -1

echo "── 5. 골든룰 검사"
python3 tools/check_forms.py

echo "── 6. 전체 내려받기 압축 파일 (반드시 마지막)"
python3 tools/make_forms_zip.py

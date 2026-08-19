/* KAHA 양식 모음 화면 — 소식지(index.html)와 회원 자료실(library/) 이 함께 씁니다.
 *
 * 두 사이트가 같은 forms.json 을 읽고 같은 코드로 그리므로,
 * 양식을 새로 만들거나 고친 뒤 forms.json 만 다시 만들면 양쪽에 그대로 반영됩니다.
 * 화면 기능을 고칠 일이 있으면 반드시 이 파일 하나만 고치십시오.
 *
 *   KAHAForms.mount(element, { base: "../" });
 *     base  — forms.json 과 forms/ 폴더까지의 상대 경로 (기본값 "")
 *     intro — 머리말 문단을 바꾸고 싶을 때
 *     title — 제목을 바꾸고 싶을 때 (기본값 "양식 모음")
 */
(function (global) {
  "use strict";

  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  // 띄어쓰기를 무시하고 한 번 더 본다 ("유선종양" ↔ "유선 종양")
  function match(it, q) {
    if (!q) return true;
    var hay = (it.name + " " + (it.desc || "") + " " + (it.kw || "")).toLowerCase();
    if (hay.indexOf(q) !== -1) return true;
    return hay.replace(/\s+/g, "").indexOf(q.replace(/\s+/g, "")) !== -1;
  }

  function mb(bytes) {
    return (bytes / 1024 / 1024).toFixed(0) + "MB";
  }

  // 전체를 한 번에 받는 줄. forms.json 의 bundle 정보가 있을 때만 그린다.
  function bundleBar(b, base) {
    if (!b || !b.path) return "";
    return '<div class="fbundle">'
      + '<div class="t"><strong>전체 내려받기</strong>'
      + "<span>양식 전체를 분류 폴더 그대로 담은 압축 파일입니다(PDF·워드 " + b.files + "개). "
      + "병원 컴퓨터에 받아 두고 쓰실 수 있습니다. · " + mb(b.bytes) + " · " + esc(b.date) + " 기준</span></div>"
      + '<a class="dl" href="' + encodeURI(base + b.path) + '" download>ZIP 내려받기</a>'
      + "</div>";
  }

  // 협회가 만든 양식 — PDF·워드를 바로 받는다
  function ownItem(it, base) {
    var h = '<div class="fitem"><div class="t"><strong>' + esc(it.name) + "</strong>"
      + (it.desc ? "<span>" + esc(it.desc) + "</span>" : "") + '</div><div class="dl">';
    if (it.pdf) h += '<a class="pdf" href="' + encodeURI(base + it.pdf)
      + '" target="_blank" rel="noopener noreferrer">PDF</a>';
    if (it.docx) h += '<a href="' + encodeURI(base + it.docx)
      + '" target="_blank" rel="noopener noreferrer">워드</a>';
    return h + "</div></div>";
  }

  // 정부·유관기관 서식 — 협회가 만든 것이 아니므로 파일을 두지 않고 받는 곳을 안내한다
  function officialItem(it) {
    var h = '<div class="fitem is-official"><div class="t">'
      + '<span class="tag">협회 양식 아님</span>'
      + '<span class="tag agency">' + esc(it.agency) + "</span>"
      + "<strong>" + esc(it.name) + "</strong>"
      + (it.desc ? '<span class="no">' + esc(it.desc) + "</span>" : "");
    if (it.basis) h += "<span>근거 " + esc(it.basis) + "</span>";
    if (it.note) h += "<span>" + esc(it.note) + "</span>";
    if (!it.url && it.site) {
      h += '<span class="where">받는 곳 · ' + esc(it.site)
        + (it.path ? " (" + esc(it.path) + ")" : "") + "</span>";
    }
    h += '</div><div class="dl">';
    if (it.url) h += '<a class="pdf" href="' + encodeURI(it.url)
      + '" target="_blank" rel="noopener noreferrer">받으러 가기</a>';
    return h + "</div></div>";
  }

  function View(el, opts) {
    this.el = el;
    this.base = (opts && opts.base) || "";
    this.title = (opts && opts.title) || "양식 모음";
    this.intro = (opts && opts.intro) || null;
    this.q = "";
    this.cat = "";
    this.data = null;
    this.composing = false;
    this.loaded = false;
  }

  View.prototype.load = function () {
    if (this.loaded) return;
    this.loaded = true;
    var self = this;
    this.el.innerHTML = "<p>양식 목록을 불러오는 중…</p>";
    fetch(this.base + "forms.json", { cache: "no-store" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (data) { self.render(data); })
      .catch(function () {
        self.loaded = false;
        self.el.innerHTML = "<p>양식 목록을 불러오지 못했습니다. 잠시 후 새로고침해 주세요.</p>";
      });
  };

  // 검색창과 분류 칩은 한 번만 그리고, 입력할 때는 목록만 바꾼다.
  // (매번 다시 그리면 한글 입력 중 조합이 끊겨 자모가 분리된다)
  View.prototype.render = function (data) {
    this.data = data;
    var extra = data.total && data.total > data.count
      ? " 정부·유관기관이 배포하는 공식 서식 " + (data.total - data.count) + "종도 목록 맨 아래에 함께 안내해 두었습니다."
      : "";
    var intro = this.intro || ("회원병원에서 바로 쓰실 수 있는 협회 양식 " + data.count + "종입니다. "
      + "인쇄해서 바로 쓰실 수 있고, 워드 파일은 자유롭게 고쳐 쓰실 수 있습니다. 모두 A4 한 장입니다." + extra);

    this.el.innerHTML = '<div class="forms-head"><h1>' + esc(this.title) + "</h1>"
      + "<p>" + esc(intro) + "</p></div>"
      + bundleBar(data.bundle, this.base)
      + '<div class="fsearch"><input type="search" class="fq" '
      + 'placeholder="양식 · 진단명 검색 (예: 슬개골, 백내장, cataract, 연차)" '
      + 'aria-label="양식 검색" autocomplete="off">'
      + '<span class="cnt fcnt"></span></div>'
      + '<div class="fchips"></div><div class="flist"></div>';

    this.box = this.el.querySelector(".fq");
    this.chipWrap = this.el.querySelector(".fchips");
    this.listWrap = this.el.querySelector(".flist");
    this.cntEl = this.el.querySelector(".fcnt");

    var self = this;
    this.box.addEventListener("compositionstart", function () { self.composing = true; });
    this.box.addEventListener("compositionend", function () {
      self.composing = false;
      self.q = self.box.value;
      self.renderList();
    });
    this.box.addEventListener("input", function () {
      self.q = self.box.value;
      if (!self.composing) self.renderList();   // 한글 조합 중에는 목록을 건드리지 않는다
    });

    this.renderChips();
    this.renderList();
  };

  View.prototype.renderChips = function () {
    var self = this;
    var h = '<button type="button" class="fchip' + (this.cat ? "" : " on") + '" data-cat="">전체</button>';
    this.data.groups.forEach(function (g) {
      g.cats.forEach(function (c) {
        var key = g.key + "/" + c.folder;
        h += '<button type="button" class="fchip' + (self.cat === key ? " on" : "")
          + (g.external ? " ext" : "")
          + '" data-cat="' + esc(key) + '">' + esc(c.label) + " " + c.items.length + "</button>";
      });
    });
    this.chipWrap.innerHTML = h;
    this.chipWrap.querySelectorAll(".fchip").forEach(function (b) {
      b.addEventListener("click", function () {
        self.cat = b.getAttribute("data-cat");
        self.renderChips();
        self.renderList();
      });
    });
  };

  View.prototype.renderList = function () {
    var self = this;
    var q = this.q.trim().toLowerCase();
    var shown = 0, body = "";
    this.data.groups.forEach(function (g) {
      var cats = "";
      g.cats.forEach(function (c) {
        if (self.cat && self.cat !== g.key + "/" + c.folder) return;
        var hits = c.items.filter(function (it) { return match(it, q); });
        if (!hits.length) return;
        shown += hits.length;
        cats += '<div class="fcat"><h2>' + esc(c.label) + "</h2>"
          + (c.blurb ? "<p>" + esc(c.blurb) + "</p>" : "");
        hits.forEach(function (it) {
          cats += it.agency ? officialItem(it) : ownItem(it, self.base);
        });
        cats += "</div>";
      });
      if (cats) {
        body += '<div class="fgroup"><h2>' + esc(g.label) + "</h2>"
          + (g.blurb ? "<p>" + esc(g.blurb) + "</p>" : "") + cats + "</div>";
      }
    });
    this.listWrap.innerHTML = body || "<p>검색 결과가 없습니다. 다른 말로 찾아보시거나 위 분류를 눌러 보세요.</p>";
    this.cntEl.textContent = shown + "종 표시";
  };

  global.KAHAForms = {
    mount: function (el, opts) {
      var v = new View(el, opts);
      v.load();
      return v;
    }
  };
})(window);

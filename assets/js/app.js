/* ==========================================================================
   鑫威凯科技官网 / Xinweikai Technology - site behaviour
   Language switching, instant search, catalogue filtering and the inquiry list.
   Plain ES5+ JavaScript, no dependency, works from file:// as well as https.
   ========================================================================== */
(function () {
  "use strict";

  var DATA = window.XWK_DATA || {};
  var I18N = window.XWK_I18N || { zh: {}, en: {} };
  var COMPANY = DATA.company || {};
  var LANG_KEY = "xwk_lang_v1";
  var INQUIRY_KEY = "xwk_inquiry_v1";
  var PAGE_SIZE = 60;

  /* ---------------------------------------------------------------- helpers */
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }

  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;").replace(/'/g, "&#39;");
  }

  function store(key, value) {
    try {
      if (value === undefined) {
        return window.localStorage.getItem(key);
      }
      window.localStorage.setItem(key, value);
      return value;
    } catch (err) {
      return null;
    }
  }

  function detectLang() {
    var fromUrl = null;
    try {
      fromUrl = new URLSearchParams(window.location.search).get("lang");
    } catch (err) { fromUrl = null; }
    if (fromUrl === "en" || fromUrl === "zh") { return fromUrl; }
    var saved = store(LANG_KEY);
    return saved === "en" ? "en" : "zh";
  }

  var lang = detectLang();

  function fillVars(value) {
    var meta = DATA.meta || {};
    return String(value).replace(/\{(cats|subs|parts|email|phone|address|short)\}/g, function (match, key) {
      if (key === "cats") { return String(meta.categories || ""); }
      if (key === "subs") { return String(meta.subs || ""); }
      if (key === "parts") { return String(meta.parts || ""); }
      if (key === "email") { return COMPANY.email || ""; }
      if (key === "phone") { return COMPANY.phone || ""; }
      if (key === "address") { return COMPANY.addressZh || ""; }
      if (key === "short") { return COMPANY.shortZh || ""; }
      return match;
    });
  }

  function t(key, vars) {
    var dict = I18N[lang] || I18N.zh || {};
    var value = dict[key];
    if (value === undefined) { value = (I18N.zh || {})[key]; }
    if (value === undefined) { return key; }
    if (vars) {
      Object.keys(vars).forEach(function (k) {
        value = value.split("{" + k + "}").join(vars[k]);
      });
    }
    return fillVars(value);
  }

  function nameOf(obj, zhField, enField) {
    if (!obj) { return ""; }
    return lang === "en" ? (obj[enField] || obj[zhField]) : (obj[zhField] || obj[enField]);
  }

  function toast(message) {
    var el = $("[data-toast]");
    if (!el) { return; }
    el.textContent = message;
    el.hidden = false;
    el.classList.add("is-visible");
    window.clearTimeout(toast._timer);
    toast._timer = window.setTimeout(function () {
      el.classList.remove("is-visible");
      window.setTimeout(function () { el.hidden = true; }, 240);
    }, 1800);
  }

  function copyText(text, okMessage) {
    var value = String(text == null ? "" : text);
    function done() { toast(okMessage || t("common.copied")); }
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(value).then(done, function () { fallback(); });
      return;
    }
    fallback();
    function fallback() {
      var area = document.createElement("textarea");
      area.value = value;
      area.setAttribute("readonly", "readonly");
      area.style.position = "fixed";
      area.style.opacity = "0";
      document.body.appendChild(area);
      area.select();
      try { document.execCommand("copy"); } catch (err) { /* ignore */ }
      document.body.removeChild(area);
      done();
    }
  }

  function highlight(text, query) {
    var raw = String(text == null ? "" : text);
    var q = String(query || "").trim();
    if (!q) { return esc(raw); }
    var idx = raw.toLowerCase().indexOf(q.toLowerCase());
    if (idx < 0) { return esc(raw); }
    return esc(raw.slice(0, idx)) + "<mark>" + esc(raw.slice(idx, idx + q.length)) + "</mark>" +
      esc(raw.slice(idx + q.length));
  }

  /* ------------------------------------------------------ part illustrations */
  function artHtml(part, size) {
    var art = window.XWK_PART_ART;
    var typeName = part && part.type ? typeLabel(part.type) : "";
    if (art && typeof art.html === "function") {
      return art.html(part, { size: size || "sm", typeLabel: typeName });
    }
    return "";
  }

  function thumbHtml(part) {
    return '<button type="button" class="part-thumb" data-open-art="' + esc(part.model) + '"' +
      ' aria-label="' + esc(t("common.viewImage", { model: part.model })) + '"' +
      ' title="' + esc(t("common.viewImage", { model: part.model })) + '">' +
      artHtml(part, "sm") + "</button>";
  }

  /* 实物图加载失败时，回落到该型号的矢量示意图，保证永远有图 */
  function fallbackArtElement(part, size) {
    var wrap = document.createElement("span");
    wrap.className = "part-art-fallback";
    if (window.XWK_PART_ART) {
      wrap.innerHTML = window.XWK_PART_ART.svgFor(part, { size: size || "md", typeLabel: typeLabel(part.type) });
    }
    return wrap;
  }

  function handleArtError(ev) {
    var img = ev.target;
    if (!img || img.tagName !== "IMG" || !img.classList || !img.classList.contains("part-art")) { return; }
    var model = img.getAttribute("data-model") || "";
    var part = model ? partByModel(model) : null;
    if (!part) { return; }
    var size = img.getAttribute("data-art-size") || "md";
    var node = fallbackArtElement(part, size);
    if (node && img.parentNode) {
      img.parentNode.replaceChild(node, img);
    }
  }

  /* ------------------------------------------------------------ data index */
  var BRAND_MAP = {};
  var TYPE_MAP = {};
  var PART_INDEX = [];
  var CAT_MAP = {};

  (DATA.brands || []).forEach(function (b) { BRAND_MAP[b.id] = b; });
  (DATA.types || []).forEach(function (x) { TYPE_MAP[x.id] = x; });
  (DATA.categories || []).forEach(function (cat) {
    CAT_MAP[cat.id] = cat;
    (cat.subs || []).forEach(function (sub) {
      (sub.parts || []).forEach(function (p) {
        PART_INDEX.push({
          model: p.m, brand: p.b, pkg: p.k, params: p.p, type: p.t,
          catId: cat.id, subId: sub.id, img: p.img || "", imgCredit: p.imgCredit || ""
        });
      });
    });
  });

  function brandLabel(id) {
    var b = BRAND_MAP[id];
    return b ? nameOf(b, "zh", "en") : String(id || "");
  }

  function typeLabel(id) {
    var x = TYPE_MAP[id];
    return x ? nameOf(x, "zh", "en") : String(id || "");
  }

  function catLabel(id) {
    var c = CAT_MAP[id];
    return c ? nameOf(c, "zh", "en") : String(id || "");
  }

  function subLabel(sub) {
    return sub ? nameOf(sub, "zh", "en") : "";
  }

  /* ---------------------------------------------------------------- search */
  function searchAll(query, limitParts) {
    var q = String(query || "").trim().toLowerCase();
    if (!q) { return { cats: [], brands: [], parts: [], total: 0 }; }
    var cats = [], brands = [], parts = [];

    (DATA.categories || []).forEach(function (cat) {
      var subs = cat.subs || [];
      var subHit = subs.filter(function (s) {
        return (s.zh + " " + s.en).toLowerCase().indexOf(q) >= 0;
      });
      var selfHit = (cat.zh + " " + cat.en).toLowerCase().indexOf(q) >= 0;
      if (selfHit || subHit.length) {
        cats.push({ cat: cat, subs: subHit.slice(0, 4) });
      }
    });

    (DATA.brands || []).forEach(function (b) {
      if ((b.zh + " " + b.en).toLowerCase().indexOf(q) >= 0) { brands.push(b); }
    });

    PART_INDEX.forEach(function (p) {
      var hay = (p.model + " " + brandLabel(p.brand) + " " + p.pkg + " " + p.params + " " +
        typeLabel(p.type) + " " + catLabel(p.catId)).toLowerCase();
      if (hay.indexOf(q) >= 0) {
        var score = 0;
        if (p.model.toLowerCase() === q) { score = 0; }
        else if (p.model.toLowerCase().indexOf(q) === 0) { score = 1; }
        else if (p.model.toLowerCase().indexOf(q) >= 0) { score = 2; }
        else if (String(p.pkg).toLowerCase().indexOf(q) >= 0) { score = 3; }
        else { score = 4; }
        parts.push({ part: p, score: score });
      }
    });
    parts.sort(function (a, b) {
      return a.score - b.score || a.part.model.length - b.part.model.length;
    });

    return {
      cats: cats, brands: brands,
      parts: parts.slice(0, limitParts || 48).map(function (x) { return x.part; }),
      total: parts.length
    };
  }

  function partRowHtml(p, query, withCat) {
    var catName = catLabel(p.catId);
    return '<tr data-model="' + esc(p.model) + '">' +
      '<td data-label="' + esc(t("common.image")) + '" class="art-cell">' + thumbHtml(p) + "</td>" +
      '<td data-label="' + esc(t("common.model")) + '" class="model-cell">' + highlight(p.model, query) + "</td>" +
      (withCat !== false ? '<td data-label="' + esc(t("common.category")) + '"><span class="tag">' + esc(catName) + "</span></td>" : "") +
      '<td data-label="' + esc(t("common.brand")) + '">' + highlight(brandLabel(p.brand), query) + "</td>" +
      '<td data-label="' + esc(t("common.package")) + '">' + highlight(p.pkg, query) + "</td>" +
      '<td data-label="' + esc(t("common.params")) + '" class="params-cell">' + highlight(p.params, query) + "</td>" +
      '<td data-label="' + esc(t("common.desc")) + '">' + esc(typeLabel(p.type)) + "</td>" +
      '<td data-label="' + esc(t("common.actions")) + '" class="row-actions-cell"><div class="row-actions">' +
      '<button type="button" class="btn btn-primary" data-add-part="' + esc(p.model) + '">' + esc(t("common.addInquiry")) + "</button>" +
      '<button type="button" class="btn btn-outline" data-copy-part="' + esc(p.model) + '">' + esc(t("common.copyModel")) + "</button>" +
      "</div></td></tr>";
  }

  function partsTableHtml(parts, query, withCat) {
    if (!parts.length) { return ""; }
    return '<table class="parts-table"><thead><tr>' +
      "<th>" + esc(t("common.image")) + "</th>" +
      "<th>" + esc(t("common.model")) + "</th>" +
      (withCat !== false ? "<th>" + esc(t("common.category")) + "</th>" : "") +
      "<th>" + esc(t("common.brand")) + "</th>" +
      "<th>" + esc(t("common.package")) + "</th>" +
      "<th>" + esc(t("common.params")) + "</th>" +
      "<th>" + esc(t("common.desc")) + "</th>" +
      "<th>" + esc(t("common.actions")) + "</th>" +
      "</tr></thead><tbody>" +
      parts.map(function (p) { return partRowHtml(p, query, withCat); }).join("") +
      "</tbody></table>" +
      '<p class="art-note" data-i18n="common.imageNote">' + esc(t("common.imageNote")) + "</p>";
  }

  /* ------------------------------------------------------- search dropdown */
  var searchForms = [];

  function renderSearchPanel(panel, query) {
    var q = String(query || "").trim();
    if (!q) { panel.hidden = true; panel.innerHTML = ""; return; }
    var res = searchAll(q, 8);
    var html = "";
    if (res.cats.length) {
      html += '<div class="search-group"><div class="search-group-title">' + esc(t("search.groupCategories")) + "</div>";
      res.cats.slice(0, 3).forEach(function (entry) {
        html += '<a class="search-item" href="category.html?cat=' + esc(entry.cat.id) + '">' +
          '<span class="search-item-main"><span class="search-item-model">' + highlight(nameOf(entry.cat, "zh", "en"), q) + "</span>" +
          '<span class="search-item-meta">' + esc((entry.cat.subs || []).length) + " " + esc(t("category.subs")) + "</span></span></a>";
      });
      html += "</div>";
    }
    if (res.brands.length) {
      html += '<div class="search-group"><div class="search-group-title">' + esc(t("search.groupBrands")) + "</div>";
      res.brands.slice(0, 3).forEach(function (b) {
        html += '<a class="search-item" href="products.html?brand=' + esc(b.id) + '">' +
          '<span class="search-item-main"><span class="search-item-model">' + highlight(b.zh, q) + "</span>" +
          '<span class="search-item-meta">' + esc(b.en) + "</span></span></a>";
      });
      html += "</div>";
    }
    if (res.parts.length) {
      html += '<div class="search-group"><div class="search-group-title">' + esc(t("search.groupParts")) + "</div>";
      res.parts.forEach(function (p) {
        html += '<a class="search-item" href="category.html?cat=' + esc(p.catId) + "&hl=" + encodeURIComponent(p.model) + '">' +
          '<span class="search-item-art">' + artHtml(p, "sm") + "</span>" +
          '<span class="search-item-main"><span class="search-item-model">' + highlight(p.model, q) + "</span>" +
          '<span class="search-item-meta">' + esc(brandLabel(p.brand)) + " · " + esc(p.pkg) + " · " + esc(p.params) + "</span></span></a>";
      });
      html += "</div>";
    }
    if (!res.parts.length && !res.cats.length && !res.brands.length) {
      html = '<div class="search-empty"><b>' + esc(t("search.emptyTitle")) + "</b>" +
        "<p>" + esc(t("search.emptyText")) + "</p>" +
        '<a class="btn btn-outline btn-sm" href="contact.html">' + esc(t("search.emptyCta")) + "</a></div>";
    } else {
      html += '<a class="search-more" href="products.html?q=' + encodeURIComponent(q) + '">' +
        esc(t("search.viewAll", { n: res.total })) + "</a>";
    }
    panel.innerHTML = html;
    panel.hidden = false;
  }

  function setupSearchForm(form) {
    var input = $("[data-search-input]", form);
    var panel = $("[data-search-panel]", form);
    if (!input || !panel) { return; }
    var state = { items: [], active: -1 };
    searchForms.push({ form: form, input: input, panel: panel, state: state });

    input.addEventListener("input", function () {
      renderSearchPanel(panel, input.value);
      state.items = $$(".search-item", panel);
      state.active = -1;
    });
    input.addEventListener("focus", function () {
      if (input.value.trim()) { renderSearchPanel(panel, input.value); }
    });
    input.addEventListener("keydown", function (ev) {
      var items = state.items;
      if (ev.key === "ArrowDown" && items.length) {
        ev.preventDefault();
        state.active = (state.active + 1) % items.length;
        syncActive(items, state);
      } else if (ev.key === "ArrowUp" && items.length) {
        ev.preventDefault();
        state.active = (state.active - 1 + items.length) % items.length;
        syncActive(items, state);
      } else if (ev.key === "Enter") {
        if (state.active >= 0 && items[state.active]) {
          ev.preventDefault();
          items[state.active].click();
          return;
        }
        ev.preventDefault();
        if (input.value.trim()) {
          window.location.href = "products.html?q=" + encodeURIComponent(input.value.trim());
        }
      } else if (ev.key === "Escape") {
        panel.hidden = true;
        input.blur();
      }
    });
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (input.value.trim()) {
        window.location.href = "products.html?q=" + encodeURIComponent(input.value.trim());
      }
    });
    document.addEventListener("click", function (ev) {
      if (!form.contains(ev.target)) { panel.hidden = true; }
    });
  }

  function syncActive(items, state) {
    items.forEach(function (el, i) { el.classList.toggle("is-active", i === state.active); });
    if (items[state.active]) {
      items[state.active].scrollIntoView({ block: "nearest" });
    }
  }

  /* ---------------------------------------------------------------- render */
  function renderCatGrid() {
    var host = $("[data-cat-grid]");
    if (!host) { return; }
    host.innerHTML = (DATA.categories || []).map(function (cat) {
      var subs = (cat.subs || []).slice(0, 3).map(function (s) { return nameOf(s, "zh", "en"); }).join(" / ");
      return '<a class="cat-card" href="category.html?cat=' + esc(cat.id) + '">' +
        '<span class="cat-card-top"><span class="icon-wrap">' + iconMarkup(cat.id) + "</span>" +
        '<span class="cat-count">' + esc(cat.count) + "</span></span>" +
        '<span class="cat-name">' + esc(nameOf(cat, "zh", "en")) + "</span>" +
        '<span class="cat-name-en">' + esc(lang === "en" ? cat.zh : cat.en) + "</span>" +
        '<p class="cat-subs">' + esc(subs) + "</p></a>";
    }).join("");
  }

  function iconMarkup(catId) {
    var path = (DATA.icons || {})[catId] || (DATA.icons || {})["pcb-wire"] || "";
    return '<svg class="icon" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + path + "</svg>";
  }

  function renderHotTable() {
    var host = $("[data-hot-table]");
    if (!host) { return; }
    var byModel = {};
    PART_INDEX.forEach(function (p) { byModel[p.model] = p; });
    var parts = (DATA.hot || []).map(function (m) { return byModel[m]; }).filter(Boolean);
    host.innerHTML = partsTableHtml(parts, "", true);
  }

  function renderServices() {
    var host = $("[data-service-grid]");
    if (!host) { return; }
    host.innerHTML = (DATA.services || []).map(function (s) {
      var title = lang === "en" ? s.enT : s.zhT;
      var desc = lang === "en" ? s.enD : s.zhD;
      return '<div class="service-card"><span class="icon-wrap">' + serviceIcon(s.icon) + "</span>" +
        "<h3>" + esc(title) + "</h3><p>" + esc(desc) + "</p></div>";
    }).join("");
  }

  function serviceIcon(name) {
    var paths = {
      search: '<circle cx="21" cy="21" r="12"/><path d="M30 30l12 12"/>',
      bom: '<rect x="10" y="8" width="28" height="34" rx="3"/><path d="M17 17h14M17 24h14M17 31h8"/>',
      stock: '<path d="M8 20l16-10 16 10-16 10z"/><path d="M8 28l16 10 16-10"/><path d="M24 30v10"/>',
      sample: '<path d="M24 8l4.6 9.8 10.4 1.4-7.6 7.4 1.9 10.4L24 31.9 14.7 37l1.9-10.4L9 19.2l10.4-1.4z"/>',
      invoice: '<rect x="12" y="7" width="24" height="34" rx="3"/><path d="M18 16h12M18 23h12M18 30h7"/>',
      support: '<path d="M10 26v-4a14 14 0 0 1 28 0v4"/><rect x="6" y="24" width="8" height="12" rx="3"/>' +
        '<rect x="34" y="24" width="8" height="12" rx="3"/><path d="M38 36v2a4 4 0 0 1-4 4h-6"/>'
    };
    return '<svg class="icon" viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + (paths[name] || paths.search) + "</svg>";
  }

  function renderBrandStrip() {
    var host = $("[data-brand-strip]");
    if (!host) { return; }
    var counts = {};
    PART_INDEX.forEach(function (p) { counts[p.brand] = (counts[p.brand] || 0) + 1; });
    var list = (DATA.brands || []).slice().sort(function (a, b) {
      return (counts[b.id] || 0) - (counts[a.id] || 0);
    }).slice(0, 24);
    host.innerHTML = list.map(function (b) {
      return '<a class="brand-chip" href="products.html?brand=' + esc(b.id) + '">' + esc(b.zh) +
        "<span>" + esc(b.en) + "</span></a>";
    }).join("");
  }

  function renderBrandGrid() {
    var host = $("[data-brand-grid]");
    if (!host) { return; }
    var counts = {}, parts = {};
    PART_INDEX.forEach(function (p) {
      counts[p.brand] = (counts[p.brand] || 0) + 1;
      parts[p.brand] = parts[p.brand] || {};
      parts[p.brand][p.catId] = true;
    });
    host.innerHTML = (DATA.brands || []).slice().sort(function (a, b) {
      return (counts[b.id] || 0) - (counts[a.id] || 0);
    }).map(function (b) {
      var catCount = Object.keys(parts[b.id] || {}).length;
      return '<a class="brand-card" href="products.html?brand=' + esc(b.id) + '">' +
        "<b>" + esc(b.zh) + "</b><span>" + esc(b.en) + "</span>" +
        '<span class="cat-count">' + esc(t("brands.partsCount", { n: counts[b.id] || 0 })) + "</span>" +
        '<span class="cat-count">' + esc(t("brands.catCount", { n: catCount })) + "</span></a>";
    }).join("");
  }

  function renderAbout() {
    var host = $("[data-about-profile]");
    if (host) {
      var paras = lang === "en" ? DATA.profileEn : DATA.profileZh;
      host.innerHTML = (paras || []).map(function (p) { return "<p>" + esc(p) + "</p>"; }).join("");
    }
    var chips = $("[data-range-chips]");
    if (chips) {
      chips.innerHTML = (DATA.categories || []).map(function (cat) {
        return '<a href="category.html?cat=' + esc(cat.id) + '">' + esc(nameOf(cat, "zh", "en")) + "</a>";
      }).join("");
    }
    var promises = $("[data-promise-list]");
    if (promises) {
      var list = lang === "en" ? DATA.promisesEn : DATA.promisesZh;
      promises.innerHTML = (list || []).map(function (p) {
        return '<div class="promise-item">' + esc(p) + "</div>";
      }).join("");
    }
  }

  /* -------------------------------------------------------- products page */
  var products = null;

  function readParams() {
    var params;
    try {
      params = new URLSearchParams(window.location.search);
    } catch (err) {
      params = { get: function () { return null; } };
    }
    return {
      q: params.get("q") || "",
      cat: params.get("cat") || "",
      sub: params.get("sub") || "",
      brand: params.get("brand") || "",
      pkg: params.get("pkg") || ""
    };
  }

  function writeParams(state) {
    if (!window.history || !window.history.replaceState) { return; }
    var params = new URLSearchParams();
    ["q", "cat", "sub", "brand", "pkg"].forEach(function (k) {
      if (state[k]) { params.set(k, state[k]); }
    });
    var qs = params.toString();
    window.history.replaceState(null, "", "products.html" + (qs ? "?" + qs : ""));
  }

  function filterParts(state) {
    var q = (state.q || "").trim().toLowerCase();
    return PART_INDEX.filter(function (p) {
      if (state.cat && p.catId !== state.cat) { return false; }
      if (state.sub && p.subId !== state.sub) { return false; }
      if (state.brand && p.brand !== state.brand) { return false; }
      if (state.pkg && p.pkg !== state.pkg) { return false; }
      if (!q) { return true; }
      var hay = (p.model + " " + brandLabel(p.brand) + " " + p.pkg + " " + p.params + " " +
        typeLabel(p.type) + " " + catLabel(p.catId)).toLowerCase();
      return hay.indexOf(q) >= 0;
    });
  }

  function renderCatTree(state) {
    var host = $("[data-cat-tree]");
    if (!host) { return; }
    var html = '<button type="button" class="cat-tree-item' + (state.cat ? "" : " is-active") +
      '" data-cat="">' + "<span>" + esc(t("products.all")) + "</span>" +
      '<span class="cat-tree-count">' + PART_INDEX.length + "</span></button>";
    (DATA.categories || []).forEach(function (cat) {
      var active = state.cat === cat.id;
      html += '<button type="button" class="cat-tree-item' + (active ? " is-active" : "") +
        '" data-cat="' + esc(cat.id) + '"><span>' + esc(nameOf(cat, "zh", "en")) + "</span>" +
        '<span class="cat-tree-count">' + esc(cat.count) + "</span></button>";
      if (active) {
        (cat.subs || []).forEach(function (sub) {
          html += '<button type="button" class="cat-tree-item cat-tree-sub' +
            (state.sub === sub.id ? " is-active" : "") + '" data-cat="' + esc(cat.id) +
            '" data-sub="' + esc(sub.id) + '"><span>' + esc(nameOf(sub, "zh", "en")) + "</span>" +
            '<span class="cat-tree-count">' + esc((sub.parts || []).length) + "</span></button>";
        });
      }
    });
    host.innerHTML = html;
  }

  function renderSelect(select, items, selected, placeholder) {
    if (!select) { return; }
    var html = '<option value="">' + esc(placeholder) + "</option>";
    items.forEach(function (item) {
      html += '<option value="' + esc(item.value) + '"' + (item.value === selected ? " selected" : "") +
        ">" + esc(item.label) + "</option>";
    });
    select.innerHTML = html;
  }

  function renderActiveFilters(state) {
    var host = $("[data-active-filters]");
    if (!host) { return; }
    var chips = [];
    if (state.q) { chips.push(["q", t("common.model") + ": " + state.q]); }
    if (state.cat) { chips.push(["cat", catLabel(state.cat)]); }
    if (state.sub) {
      var cat = CAT_MAP[state.cat];
      var sub = cat && (cat.subs || []).filter(function (s) { return s.id === state.sub; })[0];
      chips.push(["sub", subLabel(sub)]);
    }
    if (state.brand) { chips.push(["brand", brandLabel(state.brand)]); }
    if (state.pkg) { chips.push(["pkg", state.pkg]); }
    host.innerHTML = chips.length && chips.map(function (c) {
      return '<span class="chip">' + esc(c[1]) +
        '<button type="button" data-clear="' + esc(c[0]) + '" aria-label="remove">×</button></span>';
    }).join("");
  }

  function setupProducts() {
    var state = readParams();
    products = {
      state: state,
      shown: PAGE_SIZE,
      list: []
    };

    var brandCounts = {}, pkgCounts = {};
    PART_INDEX.forEach(function (p) {
      brandCounts[p.brand] = (brandCounts[p.brand] || 0) + 1;
      pkgCounts[p.pkg] = (pkgCounts[p.pkg] || 0) + 1;
    });
    var brandItems = Object.keys(brandCounts).sort(function (a, b) {
      return brandCounts[b] - brandCounts[a];
    }).map(function (id) { return { value: id, label: brandLabel(id) + " (" + brandCounts[id] + ")" }; });
    var pkgItems = Object.keys(pkgCounts).filter(function (k) {
      return pkgCounts[k] >= 2;
    }).sort(function (a, b) { return pkgCounts[b] - pkgCounts[a]; }).slice(0, 90).map(function (k) {
      return { value: k, label: k + " (" + pkgCounts[k] + ")" };
    });
    renderSelect($("[data-filter-brand]"), brandItems, state.brand, t("common.brand") + " · " + t("common.all"));
    renderSelect($("[data-filter-pkg]"), pkgItems, state.pkg, t("common.package") + " · " + t("common.all"));

    var qInput = $("[data-filter-q]");
    if (qInput) { qInput.value = state.q; }

    renderCatTree(state);
    renderActiveFilters(state);
    renderProductsResults(true);

    var tree = $("[data-cat-tree]");
    if (tree) {
      tree.addEventListener("click", function (ev) {
        var btn = ev.target.closest("[data-cat]");
        if (!btn) { return; }
        var cat = btn.getAttribute("data-cat");
        var sub = btn.getAttribute("data-sub") || "";
        if (cat === state.cat && !sub) { cat = ""; sub = ""; }
        state.cat = cat;
        state.sub = cat ? sub : "";
        products.shown = PAGE_SIZE;
        writeParams(state);
        renderCatTree(state);
        renderActiveFilters(state);
        renderProductsResults(true);
      });
    }

    if (qInput) {
      qInput.addEventListener("input", function () {
        state.q = qInput.value;
        products.shown = PAGE_SIZE;
        writeParams(state);
        renderActiveFilters(state);
        renderProductsResults(true);
      });
    }
    var brandSel = $("[data-filter-brand]");
    if (brandSel) {
      brandSel.addEventListener("change", function () {
        state.brand = brandSel.value;
        products.shown = PAGE_SIZE;
        writeParams(state);
        renderActiveFilters(state);
        renderProductsResults(true);
      });
    }
    var pkgSel = $("[data-filter-pkg]");
    if (pkgSel) {
      pkgSel.addEventListener("change", function () {
        state.pkg = pkgSel.value;
        products.shown = PAGE_SIZE;
        writeParams(state);
        renderActiveFilters(state);
        renderProductsResults(true);
      });
    }
    var reset = $("[data-filter-reset]");
    if (reset) {
      reset.addEventListener("click", function () {
        state.q = ""; state.cat = ""; state.sub = ""; state.brand = ""; state.pkg = "";
        products.shown = PAGE_SIZE;
        if (qInput) { qInput.value = ""; }
        if (brandSel) { brandSel.value = ""; }
        if (pkgSel) { pkgSel.value = ""; }
        writeParams(state);
        renderCatTree(state);
        renderActiveFilters(state);
        renderProductsResults(true);
      });
    }
    var chips = $("[data-active-filters]");
    if (chips) {
      chips.addEventListener("click", function (ev) {
        var btn = ev.target.closest("[data-clear]");
        if (!btn) { return; }
        var key = btn.getAttribute("data-clear");
        state[key] = "";
        if (key === "cat") { state.sub = ""; }
        if (key === "q" && qInput) { qInput.value = ""; }
        if (key === "brand" && brandSel) { brandSel.value = ""; }
        if (key === "pkg" && pkgSel) { pkgSel.value = ""; }
        products.shown = PAGE_SIZE;
        writeParams(state);
        renderCatTree(state);
        renderActiveFilters(state);
        renderProductsResults(true);
      });
    }
    var more = $("[data-load-more]");
    if (more) {
      more.addEventListener("click", function () {
        products.shown += PAGE_SIZE;
        renderProductsResults(false);
      });
    }
  }

  function renderProductsResults() {
    if (!products) { return; }
    var state = products.state;
    var list = filterParts(state);
    products.list = list;
    var slice = list.slice(0, products.shown);
    var host = $("[data-results]");
    if (host) { host.innerHTML = partsTableHtml(slice, state.q, true); }
    var count = $("[data-result-count]");
    if (count) { count.textContent = t("common.results", { n: list.length }); }
    var more = $("[data-load-more]");
    if (more) {
      more.hidden = slice.length >= list.length;
      more.textContent = t("common.more") + " (" + slice.length + " / " + list.length + ")";
    }
    var empty = $("[data-results-empty]");
    if (empty) { empty.hidden = list.length > 0; }
  }

  /* -------------------------------------------------------- category page */
  function setupCategory() {
    var params = readParams();
    var cat = CAT_MAP[params.cat] || (DATA.categories || [])[0];
    var head = $("[data-category-name]");
    var title = $("[data-category-title]");
    var blurb = $("[data-category-blurb]");
    if (head) { head.textContent = nameOf(cat, "zh", "en"); }
    if (title) { title.textContent = nameOf(cat, "zh", "en"); }
    if (blurb) { blurb.textContent = lang === "en" ? cat.blurbEn : cat.blurbZh; }
    document.title = nameOf(cat, "zh", "en") + " | " + (lang === "en" ? COMPANY.shortEn : COMPANY.shortZh);

    var tips = $("[data-category-tips]");
    if (tips) {
      var list = lang === "en" ? cat.tipsEn : cat.tipsZh;
      tips.innerHTML = (list || []).map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("");
    }
    var chips = $("[data-sub-chips]");
    if (chips) {
      chips.innerHTML = (cat.subs || []).map(function (sub) {
        return '<a class="chip" href="#sub-' + esc(sub.id) + '">' + esc(nameOf(sub, "zh", "en")) +
          " (" + (sub.parts || []).length + ")</a>";
      }).join("");
    }
    renderCategorySections(cat, "");

    var input = $("[data-category-q]");
    if (input) {
      input.addEventListener("input", function () {
        renderCategorySections(cat, input.value);
      });
    }
    var hl = params.hl;
    if (hl) {
      window.setTimeout(function () {
        var row = document.querySelector('[data-model="' + hl.replace(/"/g, '\\"') + '"]');
        if (row) {
          row.classList.add("is-hit");
          row.scrollIntoView({ block: "center" });
        }
      }, 120);
    }
  }

  function renderCategorySections(cat, query) {
    var host = $("[data-sub-sections]");
    if (!host) { return; }
    var q = (query || "").trim().toLowerCase();
    var html = "";
    var total = 0;
    (cat.subs || []).forEach(function (sub) {
      var parts = (sub.parts || []).filter(function (p) {
        if (!q) { return true; }
        var hay = (p.m + " " + brandLabel(p.b) + " " + p.k + " " + p.p + " " + typeLabel(p.t)).toLowerCase();
        return hay.indexOf(q) >= 0;
      });
      if (!parts.length) { return; }
      total += parts.length;
      var mapped = parts.map(function (p) {
        return { model: p.m, brand: p.b, pkg: p.k, params: p.p, type: p.t, catId: cat.id,
                 subId: sub.id, img: p.img || "", imgCredit: p.imgCredit || "" };
      });
      html += '<section class="sub-section" id="sub-' + esc(sub.id) + '">' +
        '<div class="sub-head"><h3>' + esc(nameOf(sub, "zh", "en")) + "</h3>" +
        '<span class="cat-count">' + parts.length + "</span>" +
        '<p class="tip">' + esc(lang === "en" ? (sub.tipEn || "") : (sub.tipZh || "")) + "</p></div>" +
        '<div class="table-wrap table-wrap--parts">' + partsTableHtml(mapped, q, false) + "</div></section>";
    });
    if (!total) {
      html = '<p class="empty-state">' + esc(t("products.empty")) + "</p>";
    }
    host.innerHTML = html;
  }

  /* --------------------------------------------------------- inquiry list */
  function readInquiry() {
    var raw = store(INQUIRY_KEY);
    if (!raw) { return []; }
    try {
      var parsed = JSON.parse(raw);
      return parsed && parsed.length ? parsed : [];
    } catch (err) { return []; }
  }

  function writeInquiry(list) {
    store(INQUIRY_KEY, JSON.stringify(list));
    updateInquiryCount();
  }

  function updateInquiryCount() {
    var badge = $("[data-inquiry-count]");
    if (!badge) { return; }
    var n = readInquiry().length;
    badge.textContent = String(n);
    badge.hidden = n === 0;
  }

  function addToInquiry(model) {
    var part = PART_INDEX.filter(function (p) { return p.model === model; })[0];
    if (!part) { return; }
    var list = readInquiry();
    var found = list.filter(function (x) { return x.model === model; })[0];
    if (found) {
      found.qty = String((parseInt(found.qty, 10) || 0) + 1);
    } else {
      list.push({
        model: part.model, brand: part.brand, pkg: part.pkg, params: part.params,
        type: part.type, catId: part.catId, img: part.img || "",
        imgCredit: part.imgCredit || "", qty: "1", note: ""
      });
    }
    writeInquiry(list);
    toast(t("common.added") + " · " + model);
  }

  function renderInquiryTable() {
    var host = $("[data-inquiry-table]");
    var empty = $("[data-inquiry-empty]");
    if (!host) { return; }
    var list = readInquiry();
    if (empty) { empty.hidden = list.length > 0; }
    if (!list.length) { host.innerHTML = ""; return; }
    host.innerHTML = '<table class="parts-table inquiry-table"><thead><tr>' +
      "<th>" + esc(t("common.image")) + "</th>" +
      "<th>" + esc(t("common.model")) + "</th><th>" + esc(t("common.brand")) + "</th>" +
      "<th>" + esc(t("common.package")) + "</th><th>" + esc(t("common.params")) + "</th>" +
      "<th>" + esc(t("inquiry.qty")) + "</th><th>" + esc(t("inquiry.remark")) + "</th>" +
      "<th>" + esc(t("common.actions")) + "</th></tr></thead><tbody>" +
      list.map(function (item, i) {
        return '<tr data-index="' + i + '">' +
          '<td data-label="' + esc(t("common.image")) + '" class="art-cell">' + thumbHtml(item) + "</td>" +
          '<td data-label="' + esc(t("common.model")) + '" class="model-cell">' + esc(item.model) + "</td>" +
          '<td data-label="' + esc(t("common.brand")) + '">' + esc(brandLabel(item.brand)) + "</td>" +
          '<td data-label="' + esc(t("common.package")) + '">' + esc(item.pkg) + "</td>" +
          '<td data-label="' + esc(t("common.params")) + '" class="params-cell">' + esc(item.params) + "</td>" +
          '<td data-label="' + esc(t("inquiry.qty")) + '"><input type="text" inputmode="numeric" value="' +
          esc(item.qty || "") + '" data-item-qty="' + i + '"></td>' +
          '<td data-label="' + esc(t("inquiry.remark")) + '"><input type="text" value="' +
          esc(item.note || "") + '" data-item-note="' + i + '"></td>' +
          '<td data-label="' + esc(t("common.actions")) + '" class="row-actions-cell"><div class="row-actions">' +
          '<button type="button" class="btn btn-outline" data-item-remove="' + i + '">' + esc(t("inquiry.remove")) + "</button>" +
          "</div></td></tr>";
      }).join("") + "</tbody></table>";
  }

  function inquiryText() {
    var list = readInquiry();
    var company = valueOf("company");
    var person = valueOf("person");
    var tel = valueOf("tel");
    var remark = valueOf("remark");
    var lines = [];
    lines.push(lang === "en" ? "Inquiry list" : "询价清单");
    if (company) { lines.push((lang === "en" ? "Company: " : "公司：") + company); }
    if (person) { lines.push((lang === "en" ? "Contact: " : "联系人：") + person); }
    if (tel) { lines.push((lang === "en" ? "Phone/WeChat: " : "电话/微信：") + tel); }
    lines.push("");
    list.forEach(function (item, i) {
      lines.push((i + 1) + ". " + item.model + " | " + brandLabel(item.brand) + " | " + item.pkg +
        " | " + item.params + " | " + (lang === "en" ? "Qty " : "数量 ") + (item.qty || "") +
        (item.note ? " | " + (lang === "en" ? "Note: " : "备注：") + item.note : ""));
    });
    if (remark) {
      lines.push("");
      lines.push((lang === "en" ? "Other requirements: " : "其他要求：") + remark);
    }
    lines.push("");
    lines.push(COMPANY.nameZh + " · " + COMPANY.addressZh);
    return lines.join("\n");
  }

  function valueOf(field) {
    var el = $('[data-inquiry-field="' + field + '"]');
    return el ? el.value.trim() : "";
  }

  function setupInquiry() {
    renderInquiryTable();
    var host = $("[data-inquiry-table]");
    if (host) {
      host.addEventListener("input", function (ev) {
        var qty = ev.target.getAttribute("data-item-qty");
        var note = ev.target.getAttribute("data-item-note");
        if (qty === null && note === null) { return; }
        var list = readInquiry();
        var idx = parseInt(qty !== null ? qty : note, 10);
        if (!list[idx]) { return; }
        if (qty !== null) { list[idx].qty = ev.target.value; } else { list[idx].note = ev.target.value; }
        writeInquiry(list);
      });
      host.addEventListener("click", function (ev) {
        var btn = ev.target.closest("[data-item-remove]");
        if (!btn) { return; }
        var list = readInquiry();
        list.splice(parseInt(btn.getAttribute("data-item-remove"), 10), 1);
        writeInquiry(list);
        renderInquiryTable();
      });
    }
    var mail = $("[data-inquiry-mail]");
    if (mail) {
      mail.addEventListener("click", function () {
        if (!readInquiry().length) { toast(t("inquiry.empty")); return; }
        if (!valueOf("tel")) { toast(t("inquiry.needContact")); }
        var subject = (lang === "en" ? "Component inquiry - " : "元器件询价 - ") +
          (valueOf("company") || COMPANY.shortZh);
        window.location.href = "mailto:" + COMPANY.email + "?subject=" +
          encodeURIComponent(subject) + "&body=" + encodeURIComponent(inquiryText());
      });
    }
    var copy = $("[data-inquiry-copy]");
    if (copy) {
      copy.addEventListener("click", function () {
        if (!readInquiry().length) { toast(t("inquiry.empty")); return; }
        copyText(inquiryText(), t("common.copied"));
      });
    }
    var clear = $("[data-inquiry-clear]");
    if (clear) {
      clear.addEventListener("click", function () {
        writeInquiry([]);
        renderInquiryTable();
        toast(t("inquiry.clear"));
      });
    }
  }

  /* ------------------------------------------------------------- language */
  var lightboxEl = null;
  var lightboxReturnFocus = null;

  function lightboxHtml() {
    return '<div class="lightbox-backdrop" data-art-close></div>' +
      '<div class="lightbox-card" role="dialog" aria-modal="true" aria-labelledby="lightbox-title">' +
      '<button type="button" class="lightbox-close" data-art-close aria-label="' + esc(t("common.close")) + '">×</button>' +
      '<div class="lightbox-art" data-art-figure></div>' +
      '<div class="lightbox-body">' +
      '<h3 class="lightbox-title" id="lightbox-title" data-art-title>—</h3>' +
      '<div class="lightbox-meta" data-art-meta></div>' +
      '<p class="art-source" data-art-source hidden></p>' +
      '<p class="art-note">' + esc(t("common.imageNote")) + "</p>" +
      '<div class="lightbox-actions" data-art-actions></div>' +
      "</div></div>";
  }

  function ensureLightbox() {
    if (lightboxEl) { return lightboxEl; }
    var wrap = document.createElement("div");
    wrap.className = "lightbox";
    wrap.hidden = true;
    wrap.innerHTML = lightboxHtml();
    document.body.appendChild(wrap);
    lightboxEl = wrap;
    return wrap;
  }

  function partByModel(model) {
    for (var i = 0; i < PART_INDEX.length; i += 1) {
      if (PART_INDEX[i].model === model) { return PART_INDEX[i]; }
    }
    return null;
  }

  function openArt(model) {
    var part = partByModel(model);
    if (!part) { return; }
    var wrap = ensureLightbox();
    lightboxReturnFocus = document.activeElement;
    $("[data-art-figure]", wrap).innerHTML = artHtml(part, "lg");
    var sourceNote = $("[data-art-source]", wrap);
    if (sourceNote) {
      sourceNote.hidden = !part.img;
      sourceNote.textContent = t("common.imageSource", {
        source: part.imgCredit || t("common.imageSourceDefault")
      });
    }
    $("[data-art-title]", wrap).textContent = part.model;
    var rows = [
      [t("common.brand"), brandLabel(part.brand)],
      [t("common.package"), part.pkg],
      [t("common.params"), part.params],
      [t("common.desc"), typeLabel(part.type)],
      [t("common.category"), catLabel(part.catId)]
    ];
    $("[data-art-meta]", wrap).innerHTML = rows.map(function (row) {
      return '<div class="meta-row"><dt>' + esc(row[0]) + "</dt><dd>" + esc(row[1]) + "</dd></div>";
    }).join("");
    $("[data-art-actions]", wrap).innerHTML =
      '<button type="button" class="btn btn-primary" data-add-part="' + esc(part.model) + '">' +
      esc(t("common.addInquiry")) + "</button>" +
      '<button type="button" class="btn btn-outline" data-copy-part="' + esc(part.model) + '">' +
      esc(t("common.copyModel")) + "</button>" +
      '<a class="btn btn-outline" href="category.html?cat=' + esc(part.catId) + '">' +
      esc(t("common.viewCategory")) + "</a>";
    wrap.hidden = false;
    document.body.classList.add("no-scroll");
    var closeBtn = $(".lightbox-close", wrap);
    if (closeBtn) { closeBtn.focus(); }
    var figure = $("[data-art-figure]", wrap);
    if (figure) { figure.scrollTop = 0; }
  }

  function closeArt() {
    if (!lightboxEl || lightboxEl.hidden) { return; }
    lightboxEl.hidden = true;
    document.body.classList.remove("no-scroll");
    if (lightboxReturnFocus && lightboxReturnFocus.focus) {
      try { lightboxReturnFocus.focus(); } catch (err) { /* ignore */ }
    }
    lightboxReturnFocus = null;
  }

  var PAGE_META = {
    index: ["meta.home", "meta.home"],
    products: ["products.title", "meta.products"],
    category: ["products.title", "meta.category"],
    brands: ["brands.title", "meta.brands"],
    about: ["about.title", "meta.about"],
    contact: ["contact.title", "meta.contact"],
    inquiry: ["inquiry.title", "meta.inquiry"],
    "404": ["notfound.title", "meta.404"]
  };

  function applyTranslations() {
    document.documentElement.setAttribute("lang", lang === "en" ? "en" : "zh-CN");
    document.documentElement.setAttribute("data-lang", lang);
    $$("[data-i18n]").forEach(function (el) {
      el.textContent = t(el.getAttribute("data-i18n"));
    });
    $$("[data-i18n-placeholder]").forEach(function (el) {
      el.setAttribute("placeholder", t(el.getAttribute("data-i18n-placeholder")));
    });
    $$("[data-i18n-title]").forEach(function (el) {
      el.setAttribute("title", t(el.getAttribute("data-i18n-title")));
    });
    $$("[data-i18n-aria]").forEach(function (el) {
      el.setAttribute("aria-label", t(el.getAttribute("data-i18n-aria")));
    });
    $$("[data-lang-btn]").forEach(function (btn) {
      btn.setAttribute("aria-pressed", btn.getAttribute("data-lang-btn") === lang ? "true" : "false");
    });
    var page = document.body.getAttribute("data-page");
    var meta = PAGE_META[page];
    if (meta) {
      var short = lang === "en" ? (COMPANY.shortEn || COMPANY.shortZh) : COMPANY.shortZh;
      document.title = t(meta[0]) + " | " + short;
      var descEl = document.querySelector('meta[name="description"]');
      if (descEl) { descEl.setAttribute("content", t(meta[1])); }
      var og = document.querySelector('meta[property="og:title"]');
      if (og) { og.setAttribute("content", document.title); }
    }
    var note = t("inquiry.note", { email: COMPANY.email });
    $$('[data-i18n="inquiry.note"]').forEach(function (el) { el.textContent = note; });
    $$("[data-cat-name]").forEach(function (el) {
      var id = el.getAttribute("data-cat-name");
      if (CAT_MAP[id]) { el.textContent = nameOf(CAT_MAP[id], "zh", "en"); }
    });
    var year = $("[data-year]");
    if (year) { year.textContent = String(new Date().getFullYear()); }
  }

  function renderDynamic() {
    renderCatGrid();
    renderHotTable();
    renderServices();
    renderBrandStrip();
    renderBrandGrid();
    renderAbout();
    if (document.body.getAttribute("data-page") === "products") { setupProducts(); }
    if (document.body.getAttribute("data-page") === "category") { setupCategory(); }
    if (document.body.getAttribute("data-page") === "inquiry") { setupInquiry(); }
  }

  function setLang(next) {
    lang = next;
    store(LANG_KEY, next);
    closeArt();
    applyTranslations();
    $$(".search-panel").forEach(function (p) { p.hidden = true; });
    if (document.body.getAttribute("data-page") === "products") {
      var state = readParams();
      var brandCounts = {}, pkgCounts = {};
      PART_INDEX.forEach(function (p) {
        brandCounts[p.brand] = (brandCounts[p.brand] || 0) + 1;
        pkgCounts[p.pkg] = (pkgCounts[p.pkg] || 0) + 1;
      });
      var brandItems = Object.keys(brandCounts).sort(function (a, b) {
        return brandCounts[b] - brandCounts[a];
      }).map(function (id) { return { value: id, label: brandLabel(id) + " (" + brandCounts[id] + ")" }; });
      var pkgItems = Object.keys(pkgCounts).filter(function (k) {
        return pkgCounts[k] >= 2;
      }).sort(function (a, b) { return pkgCounts[b] - pkgCounts[a]; }).slice(0, 90).map(function (k) {
        return { value: k, label: k + " (" + pkgCounts[k] + ")" };
      });
      renderSelect($("[data-filter-brand]"), brandItems, state.brand, t("common.brand") + " · " + t("common.all"));
      renderSelect($("[data-filter-pkg]"), pkgItems, state.pkg, t("common.package") + " · " + t("common.all"));
      renderCatTree(state);
      renderActiveFilters(state);
      renderProductsResults(false);
    }
    if (document.body.getAttribute("data-page") === "category") { setupCategory(); }
    if (document.body.getAttribute("data-page") === "inquiry") { renderInquiryTable(); }
    renderDynamicSectionsOnly();
  }

  function renderDynamicSectionsOnly() {
    renderCatGrid();
    renderHotTable();
    renderServices();
    renderBrandStrip();
    renderBrandGrid();
    renderAbout();
  }

  /* -------------------------------------------------------------- wiring */
  function setupChrome() {
    $$('[data-lang-btn]').forEach(function (btn) {
      btn.addEventListener("click", function () { setLang(btn.getAttribute("data-lang-btn")); });
    });
    var toggle = $("[data-menu-toggle]");
    var nav = $("[data-nav]");
    if (toggle && nav) {
      toggle.addEventListener("click", function () {
        var open = nav.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", open ? "true" : "false");
      });
    }
    var header = $("[data-header]");
    if (header) {
      var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
      window.addEventListener("scroll", onScroll, { passive: true });
      onScroll();
    }
    $$("[data-search-form]").forEach(setupSearchForm);
    document.addEventListener("error", handleArtError, true);
    document.addEventListener("keydown", function (ev) {
      if (ev.key === "Escape") { closeArt(); return; }
      if (ev.key !== "/") { return; }
      var tag = (ev.target.tagName || "").toLowerCase();
      if (tag === "input" || tag === "textarea" || tag === "select") { return; }
      ev.preventDefault();
      var input = $("[data-search-input]");
      if (input) { input.focus(); }
    });
    document.addEventListener("click", function (ev) {
      var opener = ev.target.closest ? ev.target.closest("[data-open-art]") : null;
      if (opener) { openArt(opener.getAttribute("data-open-art")); return; }
      if (ev.target.closest && ev.target.closest("[data-art-close]")) { closeArt(); return; }
      var add = ev.target.closest("[data-add-part]");
      if (add) { addToInquiry(add.getAttribute("data-add-part")); return; }
      var copy = ev.target.closest("[data-copy-part]");
      if (copy) { copyText(copy.getAttribute("data-copy-part"), t("common.copied")); return; }
      var copyBtn = ev.target.closest("[data-copy]");
      if (copyBtn) { copyText(copyBtn.getAttribute("data-copy"), t("common.copied")); }
    });
    if (!$(".call-fab") && window.matchMedia("(max-width: 760px)").matches) {
      var fab = document.createElement("a");
      fab.className = "call-fab";
      fab.href = "tel:" + COMPANY.phone;
      fab.setAttribute("aria-label", t("common.call"));
      fab.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" ' +
        'stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h4l2 5-2.5 1.5a12 12 0 0 0 6 6L15 14l5 2v4a1 1 0 0 1-1.1 1A17 17 0 0 1 3 5.1 1 1 0 0 1 4 4z"/></svg>';
      document.body.appendChild(fab);
    }
  }

  function init() {
    applyTranslations();
    setupChrome();
    renderDynamic();
    updateInquiryCount();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();

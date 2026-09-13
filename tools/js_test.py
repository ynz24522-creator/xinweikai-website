# -*- coding: utf-8 -*-
"""Behavioural test for assets/js/app.js.

Runs the real application script inside JavaScriptCore with a minimal DOM shim,
then exercises search, filtering, i18n and the inquiry list.
Run: python3 js_test.py
"""

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
SITE = PARENT if os.path.isfile(os.path.join(PARENT, "index.html")) \
    else os.path.join(os.path.dirname(PARENT), "outputs", "xinweikai-website")
JSC = "/System/Library/Frameworks/JavaScriptCore.framework/Versions/A/Helpers/jsc"

SHIM = r"""
var global = this;
var window = global;
var __ls = {};
window.localStorage = {
  getItem: function (k) { return Object.prototype.hasOwnProperty.call(__ls, k) ? __ls[k] : null; },
  setItem: function (k, v) { __ls[k] = String(v); },
  removeItem: function (k) { delete __ls[k]; }
};
window.location = { search: "", href: "" };
window.history = { replaceState: function () {} };
window.matchMedia = function () { return { matches: false }; };
window.addEventListener = function () {};
window.scrollTo = function () {};
window.setTimeout = function (fn) { return 0; };
window.clearTimeout = function () {};
if (typeof setTimeout === "undefined") { var setTimeout = window.setTimeout; }
if (typeof clearTimeout === "undefined") { var clearTimeout = window.clearTimeout; }
var navigator = { clipboard: null };
function stubEl() {
  var self = {
    style: {}, hidden: false, value: "", textContent: "", innerHTML: "", _classes: {}, _q: {},
    classList: {
      add: function (c) { self._classes[c] = true; },
      remove: function (c) { delete self._classes[c]; },
      toggle: function (c, on) { if (on) { self._classes[c] = true; } else { delete self._classes[c]; } },
      contains: function (c) { return !!self._classes[c]; }
    },
    setAttribute: function (k, v) { self["attr_" + k] = v; },
    getAttribute: function (k) { return self["attr_" + k] === undefined ? null : self["attr_" + k]; },
    appendChild: function (child) { self._children = self._children || []; self._children.push(child); },
    removeChild: function () {}, replaceChild: function (n, o) { self._replaced = { next: n, prev: o }; },
    select: function () {},
    addEventListener: function () {}, click: function () {}, focus: function () { self._focused = true; },
    contains: function () { return false; }, scrollIntoView: function () {},
    querySelector: function (sel) { if (!self._q[sel]) { self._q[sel] = stubEl(); } return self._q[sel]; },
    querySelectorAll: function () { return []; }
  };
  return self;
}
var document = {
  readyState: "complete",
  title: "",
  body: stubEl(),
  documentElement: stubEl(),
  querySelector: function () { return null; },
  querySelectorAll: function () { return []; },
  addEventListener: function () {},
  createElement: function () { return stubEl(); }
};
document.body.getAttribute = function () { return "index"; };
document.activeElement = stubEl();
"""

TESTS = r"""
var api = window.__XWK_TEST__;
var results = [];
function check(name, condition, detail) {
  results.push({ name: name, ok: !!condition, detail: detail === undefined ? "" : String(detail) });
}

check("index size", api.PART_INDEX.length === 939, api.PART_INDEX.length);

var r0603 = api.searchAll("0603", 8);
check("search 0603 returns parts", r0603.parts.length > 0, r0603.total);

var rStm = api.searchAll("STM32F103C8T6", 8);
check("exact model ranks first", rStm.parts.length > 0 && rStm.parts[0].model === "STM32F103C8T6",
  rStm.parts.length ? rStm.parts[0].model : "none");

var rZh = api.searchAll("电阻", 8);
var rZhCats = rZh.cats.map(function (x) { return x.cat.id; });
check("chinese category keyword", rZhCats.indexOf("resistors") >= 0, rZhCats.join(","));

var rBrand = api.searchAll("国巨", 8);
check("brand keyword 国巨 -> yageo", rBrand.brands.length > 0 && rBrand.brands[0].id === "yageo",
  rBrand.brands.length ? rBrand.brands[0].id : "none");

var rMos = api.searchAll("MOS", 8);
check("MOS keyword hits", rMos.total > 20, rMos.total);

var rSma = api.searchAll("SMA", 8);
check("package keyword SMA hits", rSma.total > 0, rSma.total);

var rPack = api.searchAll("SOT-23", 8);
check("package keyword SOT-23 hits", rPack.total > 10, rPack.total);

check("filter by category", api.filterParts({ cat: "resistors" }).length === 100,
  api.filterParts({ cat: "resistors" }).length);
check("filter by brand", api.filterParts({ brand: "yageo" }).length > 20,
  api.filterParts({ brand: "yageo" }).length);
check("filter by package", api.filterParts({ pkg: "0805" }).length > 20,
  api.filterParts({ pkg: "0805" }).length);
check("filter case-insensitive", api.filterParts({ q: "type-c" }).length === api.filterParts({ q: "TYPE-C" }).length,
  api.filterParts({ q: "type-c" }).length);

api.writeInquiry([]);
api.addToInquiry("SS34");
check("inquiry add", api.readInquiry().length === 1, api.readInquiry().length);
api.addToInquiry("SS34");
check("inquiry quantity increments", api.readInquiry()[0].qty === "2", api.readInquiry()[0].qty);
api.addToInquiry("STM32F103C8T6");
var text = api.inquiryText();
check("inquiry text contains models", text.indexOf("SS34") >= 0 && text.indexOf("STM32F103C8T6") >= 0, "");
check("inquiry text contains address", text.indexOf("都会电子城") >= 0, "");
api.writeInquiry([]);
check("inquiry cleared", api.readInquiry().length === 0, api.readInquiry().length);

check("zh dictionary", api.t("nav.home") === "首页", api.t("nav.home"));
api.setLang("en");
check("en dictionary", api.t("nav.home") === "Home", api.t("nav.home"));
check("en search label", api.t("search.placeholder").indexOf("Search") === 0, api.t("search.placeholder"));
check("en placeholders filled", api.t("home.catLead").indexOf("{") < 0 && api.t("home.catLead").indexOf("119") >= 0,
  api.t("home.catLead").slice(0, 60));
check("en products lead filled", api.t("products.lead").indexOf("939") >= 0, api.t("products.lead").slice(0, 40));
api.setLang("zh");
check("back to zh", api.t("nav.home") === "首页", api.t("nav.home"));
check("zh placeholders filled", api.t("home.catLead").indexOf("{") < 0 && api.t("home.catLead").indexOf("119") >= 0,
  api.t("home.catLead").slice(0, 42));
check("zh products lead filled", api.t("products.lead").indexOf("939") >= 0, api.t("products.lead").slice(0, 30));
check("zh about data filled", api.t("about.dataText").indexOf("{") < 0 && api.t("about.dataText").indexOf("939") >= 0, "");
check("inquiry note email filled", api.t("inquiry.note").indexOf("17317103@qq.com") >= 0, "");

/* ---------- product illustrations ---------- */
var ART = window.XWK_PART_ART;
check("art api present", !!ART && typeof ART.svgFor === "function" && typeof ART.html === "function", "");
check("art shape library", ART && ART.shapeIds.length >= 45, ART ? ART.shapeIds.length : 0);

var artEmpty = 0, artMissing = 0, artShapes = {};
var typeSet = {};
window.XWK_DATA.types.forEach(function (x) { typeSet[x.id] = true; });
api.PART_INDEX.forEach(function (p) {
  var svg = ART.svgFor(p, { size: "lg", typeLabel: "类型" });
  if (!svg || svg.length < 200 || svg.indexOf("<svg") !== 0) { artEmpty += 1; }
  if (svg.indexOf(p.model) < 0) { artMissing += 1; }
  var shape = ART.shapeFor(p);
  artShapes[shape] = (artShapes[shape] || 0) + 1;
  if (ART.typeShapes[p.type] === undefined) { artMissing += 1000; }
});
check("every part renders an illustration", artEmpty === 0, artEmpty);
check("illustration contains its model", artMissing === 0, artMissing);
check("all shapes in use exist", Object.keys(artShapes).every(function (s) { return ART.shapeIds.indexOf(s) >= 0; }),
  Object.keys(artShapes).join(",").slice(0, 60));

var unmapped = Object.keys(typeSet).filter(function (id) { return !ART.typeShapes[id]; });
check("all 123 type keys mapped", unmapped.length === 0, unmapped.join(","));

var samplePart = api.PART_INDEX[7];
check("illustration is deterministic",
  ART.svgFor(samplePart, { size: "lg" }) === ART.svgFor(samplePart, { size: "lg" }), "");
check("thumbnail size has no caption", ART.svgFor(samplePart, { size: "sm" }).indexOf("<text") < 0, "");
check("large size shows package", ART.svgFor(samplePart, { size: "lg" }).indexOf(samplePart.pkg) >= 0, samplePart.pkg);

var photo = ART.html({ model: "C25804", pkg: "SOT-223", type: "ldo", img: "assets/img/parts/c25804.jpg" }, { size: "sm" });
check("img override renders a photo", photo.indexOf("<img") === 0 && photo.indexOf("assets/img/parts/c25804.jpg") >= 0, "");
check("photo carries model and size hooks", photo.indexOf('data-model="C25804"') >= 0 && photo.indexOf('data-art-size="sm"') >= 0, "");

var risky = ART.svgFor({ model: "<b>a&b</b>", pkg: "0402", type: "res-thick", catId: "resistors" }, { size: "lg" });
check("model text is escaped", risky.indexOf("<b>a&b</b>") < 0 && risky.indexOf("&lt;b&gt;") >= 0, "");

var rowHtml = api.partRowHtml(samplePart, "", true);
check("row includes thumbnail button",
  rowHtml.indexOf("data-open-art") >= 0 && (rowHtml.indexOf("<svg") >= 0 || rowHtml.indexOf("<img") >= 0), "");
check("row thumbnail is accessible", rowHtml.indexOf("aria-label") >= 0, "");

var tableHtml = api.partsTableHtml([samplePart], "", true);
check("table has image column", tableHtml.indexOf(api.t("common.image")) >= 0, "");
check("table carries the art disclaimer", tableHtml.indexOf("art-note") >= 0, "");
check("thumbnail helper returns markup", api.thumbHtml(samplePart).indexOf("part-thumb") >= 0, "");

/* ---------- category page rows keep the photo field ---------- */
var catPhotos = 0, catRows = 0;
window.XWK_DATA.categories.forEach(function (c) {
  c.subs.forEach(function (s) {
    var query = "";
    s.parts.forEach(function () { catRows += 1; });
    var withImg = s.parts.filter(function (p) { return p.img; }).length;
    catPhotos += withImg;
  });
});
check("catalogue keeps photos on category pages", catPhotos > 0, catPhotos + "/" + catRows);

/* ---------- photos from LCSC + fallback ---------- */
var photoParts = api.PART_INDEX.filter(function (p) { return p.img; });
check("catalogue carries synced photos", photoParts.length > 0, photoParts.length);
if (photoParts.length) {
  var pp = photoParts[0];
  var rowPhoto = api.partRowHtml(pp, "", true);
  check("photo row renders an img tag", rowPhoto.indexOf("<img") >= 0 && rowPhoto.indexOf(pp.img) >= 0, pp.img);
  var lbPhoto = api.artHtml(pp, "lg");
  check("large photo uses lg size hook", lbPhoto.indexOf('data-art-size="lg"') >= 0, "");
  check("photo part carries a credit", !!pp.imgCredit, pp.imgCredit);

  var ccPart = api.PART_INDEX.filter(function (p) { return p.img && /Commons/i.test(p.imgCredit || ""); })[0];
  if (ccPart) {
    api.openArt(ccPart.model);
    var ccWrap = (document.body._children || [])[0];
    var ccNote = ccWrap && ccWrap._q ? ccWrap._q["[data-art-source]"] : null;
    check("lightbox shows the CC credit", !!ccNote && ccNote.textContent.indexOf("Commons") >= 0,
      ccNote ? ccNote.textContent : "n/a");
    api.closeArt();
  }
  var lcscPart = api.PART_INDEX.filter(function (p) { return p.img && /立创/.test(p.imgCredit || ""); })[0];
  if (lcscPart) {
    api.openArt(lcscPart.model);
    var lcWrap = (document.body._children || [])[0];
    var lcNote = lcWrap && lcWrap._q ? lcWrap._q["[data-art-source]"] : null;
    check("lightbox shows the LCSC credit", !!lcNote && lcNote.textContent.indexOf("立创") >= 0,
      lcNote ? lcNote.textContent : "n/a");
    api.closeArt();
  }

  var fakeImg = stubEl();
  fakeImg.tagName = "IMG";
  fakeImg._classes["part-art"] = true;
  fakeImg.setAttribute("data-model", pp.model);
  fakeImg.setAttribute("data-art-size", "sm");
  var holder = stubEl();
  holder.appendChild(fakeImg);
  fakeImg.parentNode = holder;
  api.handleArtError({ target: fakeImg });
  var swapped = holder._replaced ? holder._replaced.next : null;
  check("broken photo falls back to a vector illustration",
    !!swapped && String(swapped.innerHTML).indexOf("<svg") >= 0, "");
}

/* ---------- lightbox behaviour (DOM shim) ---------- */
var lbModel = "STM32F103C8T6";
api.openArt(lbModel);
var lbWrap = (document.body._children || [])[0] || null;
var figure = lbWrap && lbWrap._q ? lbWrap._q["[data-art-figure]"] : null;
var title = lbWrap && lbWrap._q ? lbWrap._q["[data-art-title]"] : null;
var meta = lbWrap && lbWrap._q ? lbWrap._q["[data-art-meta]"] : null;
var actions = lbWrap && lbWrap._q ? lbWrap._q["[data-art-actions]"] : null;
check("lightbox created", !!lbWrap && lbWrap.hidden === false, "hidden=" + (lbWrap ? lbWrap.hidden : "n/a"));
check("lightbox shows the large image", !!figure &&
  (figure.innerHTML.indexOf("<svg") >= 0 || figure.innerHTML.indexOf("<img") >= 0) &&
  figure.innerHTML.indexOf(lbModel) >= 0, "");
check("lightbox title is the model", !!title && title.textContent === lbModel, title ? title.textContent : "n/a");
check("lightbox lists parameters", !!meta && meta.innerHTML.indexOf("LQFP-48") >= 0, "");
check("lightbox offers inquiry actions",
  !!actions && actions.innerHTML.indexOf("data-add-part") >= 0 && actions.innerHTML.indexOf("category.html?cat=") >= 0, "");
check("lightbox locks page scroll", document.body._classes["no-scroll"] === true, "");
api.closeArt();
check("lightbox closes", lbWrap.hidden === true, "");
check("scroll lock released", document.body._classes["no-scroll"] !== true, "");
var lbHtml = api.lightboxHtml ? api.lightboxHtml() : "";
check("lightbox markup is a modal dialog", lbHtml.indexOf('role="dialog"') >= 0 && lbHtml.indexOf('aria-modal="true"') >= 0,
  lbHtml.slice(0, 40));

var row = api.partRowHtml({ model: "<b>x</b>", brand: "tsc", pkg: "SMA", params: "1A & 2A", type: "diode-rect", catId: "diodes" }, "x");
check("html escaping", row.indexOf("&lt;b&gt;") >= 0 && row.indexOf("&amp;") >= 0, "");

var rendered = 0;
api.PART_INDEX.forEach(function (p) {
  var html = api.partRowHtml(p, "0603", true);
  if (html.indexOf(p.model) >= 0) { rendered += 1; }
});
check("every part renders a row", rendered === api.PART_INDEX.length, rendered);

var failed = 0;
results.forEach(function (r) {
  if (!r.ok) { failed += 1; }
  print((r.ok ? "PASS " : "FAIL ") + r.name + (r.detail ? "  [" + r.detail + "]" : ""));
});
print("---- " + (results.length - failed) + "/" + results.length + " passed");
if (failed > 0) { quit(1); }
"""


def main():
    app_path = os.path.join(SITE, "assets", "js", "app.js")
    with open(app_path, encoding="utf-8") as fh:
        app = fh.read()
    marker = "})();"
    if marker not in app:
        print("cannot find IIFE terminator in app.js")
        return 1
    export = ("  window.__XWK_TEST__ = { searchAll: searchAll, filterParts: filterParts, "
              "PART_INDEX: PART_INDEX, readInquiry: readInquiry, writeInquiry: writeInquiry, "
              "addToInquiry: addToInquiry, inquiryText: inquiryText, t: t, setLang: setLang, "
              "partRowHtml: partRowHtml, partsTableHtml: partsTableHtml, thumbHtml: thumbHtml, "
              "artHtml: artHtml, openArt: openArt, closeArt: closeArt, lightboxHtml: lightboxHtml, "
              "handleArtError: handleArtError };\n})();")
    app_test = app.replace(marker, export)
    with tempfile.TemporaryDirectory() as tmp:
        app_file = os.path.join(tmp, "app_test.js")
        with open(app_file, "w", encoding="utf-8") as fh:
            fh.write(app_test)
        script = (
            SHIM +
            'load("%s");\n' % os.path.join(SITE, "assets", "js", "data.js") +
            'load("%s");\n' % os.path.join(SITE, "assets", "js", "i18n.js") +
            'load("%s");\n' % os.path.join(SITE, "assets", "js", "part-art.js") +
            'load("%s");\n' % app_file +
            TESTS
        )
        script_file = os.path.join(tmp, "run.js")
        with open(script_file, "w", encoding="utf-8") as fh:
            fh.write(script)
        proc = subprocess.run([JSC, script_file], capture_output=True, text=True)
    sys.stdout.write(proc.stdout)
    if proc.stderr.strip():
        sys.stderr.write(proc.stderr)
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())

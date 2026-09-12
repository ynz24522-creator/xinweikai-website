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
  return {
    style: {}, hidden: false, value: "", textContent: "", innerHTML: "",
    classList: { add: function () {}, remove: function () {}, toggle: function () {} },
    setAttribute: function () {}, getAttribute: function () { return null; },
    appendChild: function () {}, removeChild: function () {}, select: function () {},
    addEventListener: function () {}, click: function () {}, focus: function () {},
    contains: function () { return false; }, scrollIntoView: function () {}
  };
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
              "partRowHtml: partRowHtml };\n})();")
    app_test = app.replace(marker, export)
    with tempfile.TemporaryDirectory() as tmp:
        app_file = os.path.join(tmp, "app_test.js")
        with open(app_file, "w", encoding="utf-8") as fh:
            fh.write(app_test)
        script = (
            SHIM +
            'load("%s");\n' % os.path.join(SITE, "assets", "js", "data.js") +
            'load("%s");\n' % os.path.join(SITE, "assets", "js", "i18n.js") +
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

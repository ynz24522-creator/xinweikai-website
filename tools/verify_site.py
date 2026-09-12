# -*- coding: utf-8 -*-
"""Static verification for the generated site.

Checks tag balance, internal links/assets, i18n key coverage, JSON-LD validity
and product-data integrity. Run: python3 verify_site.py
"""

import json
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
SITE = PARENT if os.path.isfile(os.path.join(PARENT, "index.html")) \
    else os.path.join(os.path.dirname(PARENT), "outputs", "xinweikai-website")
PAGES = ["index.html", "products.html", "category.html", "brands.html",
         "about.html", "contact.html", "inquiry.html", "404.html"]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr"}

errors = []
warnings = []


class Balance(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.stack = []
        self.problems = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.problems.append("extra </%s>" % tag)
            return
        if self.stack[-1] == tag:
            self.stack.pop()
            return
        if tag in self.stack:
            while self.stack and self.stack[-1] != tag:
                self.problems.append("unclosed <%s>" % self.stack.pop())
            if self.stack:
                self.stack.pop()
        else:
            self.problems.append("stray </%s>" % tag)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def load_js_payload(filename, varname):
    text = read(os.path.join(SITE, "assets", "js", filename))
    prefix = "window.%s = " % varname
    start = text.index(prefix) + len(prefix)
    end = text.rindex(";")
    return json.loads(text[start:end])


def check_pages():
    for page in PAGES:
        path = os.path.join(SITE, page)
        if not os.path.exists(path):
            errors.append("missing page %s" % page)
            continue
        html = read(path)
        parser = Balance()
        parser.feed(html)
        for leftover in parser.stack:
            parser.problems.append("unclosed <%s>" % leftover)
        for problem in parser.problems:
            errors.append("%s: %s" % (page, problem))
        for marker in ("data-header", "data-search-form", "data-inquiry-count",
                       "assets/js/data.js", "assets/js/i18n.js", "assets/js/app.js",
                       'class="site-footer"', "data-lang-btn"):
            if marker not in html:
                errors.append("%s: missing %s" % (page, marker))
        # internal references
        for ref in re.findall(r'(?:href|src)="([^"]+)"', html):
            if ref.startswith(("http", "tel:", "mailto:", "#", "data:", "//")):
                continue
            target = ref.split("?")[0].split("#")[0]
            if not target:
                continue
            if not os.path.exists(os.path.join(SITE, target)):
                errors.append("%s: broken reference %s" % (page, ref))
        # JSON-LD
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            try:
                data = json.loads(block)
            except ValueError as exc:
                errors.append("%s: invalid JSON-LD (%s)" % (page, exc))
                continue
            if data.get("@type") != "LocalBusiness":
                warnings.append("%s: JSON-LD type is %s" % (page, data.get("@type")))


def check_i18n():
    i18n = load_js_payload("i18n.js", "XWK_I18N")
    zh_keys = set(i18n["zh"].keys())
    en_keys = set(i18n["en"].keys())
    if zh_keys != en_keys:
        errors.append("i18n key mismatch: %s" % sorted(zh_keys ^ en_keys))
    used = set()
    for page in PAGES:
        html = read(os.path.join(SITE, page))
        used |= set(re.findall(r'data-i18n(?:-placeholder|-title|-aria)?="([^"]+)"', html))
    app = read(os.path.join(SITE, "assets", "js", "app.js"))
    used |= set(re.findall(r'(?<![A-Za-z0-9_])t\("([A-Za-z0-9_.]+)"', app))
    missing = sorted(k for k in used if k not in zh_keys)
    if missing:
        errors.append("i18n keys used but undefined: %s" % missing)
    unused = sorted(k for k in zh_keys if k not in used and not k.startswith("meta."))
    if unused:
        warnings.append("i18n keys defined but unused: %s" % unused)
    return i18n


def check_data():
    data = load_js_payload("data.js", "XWK_DATA")
    brands = {b["id"] for b in data["brands"]}
    types = {x["id"] for x in data["types"]}
    cat_ids = set()
    sub_ids = set()
    total = 0
    models = {}
    for cat in data["categories"]:
        cat_ids.add(cat["id"])
        count = 0
        for sub in cat["subs"]:
            sub_ids.add("%s/%s" % (cat["id"], sub["id"]))
            for part in sub["parts"]:
                total += 1
                count += 1
                if part["b"] not in brands:
                    errors.append("unknown brand key %s on %s" % (part["b"], part["m"]))
                if part["t"] not in types:
                    errors.append("unknown type key %s on %s" % (part["t"], part["m"]))
                models[part["m"]] = models.get(part["m"], 0) + 1
        if count != cat["count"]:
            errors.append("category %s count mismatch %s != %s" % (cat["id"], count, cat["count"]))
    dups = [m for m, n in models.items() if n > 1]
    if dups:
        warnings.append("duplicate model numbers: %s" % dups[:10])
    for hot in data["hot"]:
        if hot not in models:
            errors.append("hot model %s not in catalogue" % hot)
    if total != data["meta"]["parts"]:
        errors.append("meta parts %s != actual %s" % (data["meta"]["parts"], total))
    if len(data["categories"]) != data["meta"]["categories"]:
        errors.append("meta categories mismatch")
    if len(data["icons"]) != len(data["categories"]):
        warnings.append("icon count %s vs categories %s" % (len(data["icons"]), len(data["categories"])))
    for cat in data["categories"]:
        if cat["id"] not in data["icons"]:
            errors.append("category %s has no icon" % cat["id"])
    return data, total


def check_seo():
    sitemap = read(os.path.join(SITE, "sitemap.xml"))
    urls = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    if len(urls) < len(PAGES) + len(PAGES):
        warnings.append("sitemap has %d urls" % len(urls))
    robots = read(os.path.join(SITE, "robots.txt"))
    if "Sitemap:" not in robots:
        errors.append("robots.txt has no sitemap line")


def main():
    check_pages()
    check_i18n()
    data, total = check_data()
    check_seo()
    print("pages=%d categories=%d subs=%d parts=%d brands=%d"
          % (len(PAGES), len(data["categories"]),
             sum(len(c["subs"]) for c in data["categories"]), total, len(data["brands"])))
    for w in warnings:
        print("WARN: %s" % w)
    if errors:
        for e in errors:
            print("ERROR: %s" % e)
        sys.exit(1)
    print("OK: static checks passed")


if __name__ == "__main__":
    main()

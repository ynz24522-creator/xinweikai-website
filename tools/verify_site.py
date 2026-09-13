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
                       "assets/js/part-art.js",
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


def check_assets():
    """Illustration engine, styles and lightbox hooks must ship with the site."""
    art_js = os.path.join(SITE, "assets", "js", "part-art.js")
    if not os.path.exists(art_js):
        errors.append("missing assets/js/part-art.js")
    else:
        text = read(art_js)
        for needle in ("window.XWK_PART_ART", "svgFor", "shapeFor", "paletteFor", "TYPE_SHAPE"):
            if needle not in text:
                errors.append("part-art.js: missing %s" % needle)
    css = read(os.path.join(SITE, "assets", "css", "style.css"))
    for needle in (".part-thumb", ".lightbox", ".art-note", ".art-cell"):
        if needle not in css:
            errors.append("style.css: missing %s" % needle)
    app = read(os.path.join(SITE, "assets", "js", "app.js"))
    for needle in ("openArt", "closeArt", "data-open-art", "common.imageNote"):
        if needle not in app:
            errors.append("app.js: missing %s" % needle)
    # 分类页与询价清单也要带上实物图字段（曾经漏过，导致分类页只显示示意图）
    if 'img: p.img || ""' not in app:
        errors.append("app.js: category rows drop the photo field")
    if "img: part.img || \"\"" not in app:
        errors.append("app.js: inquiry rows drop the photo field")


def check_art_coverage():
    """Every catalogue type key must have an explicit shape mapping entry."""
    data = load_js_payload("data.js", "XWK_DATA")
    art = read(os.path.join(SITE, "assets", "js", "part-art.js"))
    unmapped = [entry["id"] for entry in data["types"] if '"%s"' % entry["id"] not in art]
    if unmapped:
        errors.append("part-art.js: types without a shape mapping: %s" % unmapped)


def check_part_photos():
    """Synced LCSC photos: every referenced file must exist and stay small."""
    data = load_js_payload("data.js", "XWK_DATA")
    photos = []
    for cat in data["categories"]:
        for sub in cat["subs"]:
            for part in sub["parts"]:
                if part.get("img"):
                    photos.append((part["m"], part["img"]))
    missing = [p for _, p in photos if not os.path.exists(os.path.join(SITE, p))]
    if missing:
        errors.append("data.js references %d missing photos, e.g. %s" % (len(missing), missing[:3]))
    too_big = []
    for _, rel in photos:
        path = os.path.join(SITE, rel)
        if os.path.exists(path) and os.path.getsize(path) > 60 * 1024:
            too_big.append(rel)
    if too_big:
        warnings.append("%d photos exceed 60KB: %s" % (len(too_big), too_big[:3]))

    manifest_path = os.path.join(SITE, "assets", "img", "parts", "manifest.json")
    if os.path.exists(manifest_path):
        manifest = json.loads(read(manifest_path))
        entries = manifest.get("entries", [])
        bad = [e["file"] for e in entries if not os.path.exists(os.path.join(SITE, e["file"]))]
        if bad:
            errors.append("manifest lists %d missing files, e.g. %s" % (len(bad), bad[:3]))
        covered = sum(len(e.get("models", [])) for e in entries)
        shared = len(photos) - covered
        print("manifest: %d photos, %d exact models, %d shared-family models" % (len(entries), covered, shared))
    else:
        warnings.append("no assets/img/parts/manifest.json yet (photos not synced)")
    global PHOTO_STATS
    PHOTO_STATS = (len(photos), sum(1 for c in data["categories"] for s in c["subs"] for p in s["parts"]))
    return photos


def main():
    check_pages()
    check_i18n()
    data, total = check_data()
    check_seo()
    check_assets()
    check_art_coverage()
    photos = check_part_photos()
    print("photos=%d/%d models (%d files)" % (len(photos), total,
          len({p for _, p in photos})))
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

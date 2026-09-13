#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合并两类图源，生成站点用的图片清单（assets/img/parts/manifest.json）。

来源：
  1. 立创商城抓取结果  work/lcsc/index.json + work/lcsc/raw/<立创编号>.jpg
  2. 外部图源抓取结果  work/webimg/index.json + assets/img/parts/web/*.jpg
     （Wikimedia Commons / 品牌官网 / 必应检索，带来源页与许可）

产物：
  assets/img/parts/<立创编号>.jpg     立创图（900×900 → 300×300）
  assets/img/parts/manifest.json      统一清单：型号 / 文件 / 来源 / 许可 / 匹配方式

用法：
  python3 tools/sync_images.py             # 增量：已存在的图片不重复压缩
  python3 tools/sync_images.py --force     # 重新压缩全部立创图
"""

import argparse
import collections
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
PROJECT = os.path.dirname(os.path.dirname(SITE))

PARTS_DIR = os.path.join(SITE, "assets", "img", "parts")
LCSC_INDEX = os.path.join(PROJECT, "work", "lcsc", "index.json")
LCSC_RAW = os.path.join(PROJECT, "work", "lcsc", "raw")
WEB_INDEX = os.path.join(PROJECT, "work", "webimg", "index.json")
BLOCKLIST = os.path.join(PROJECT, "work", "webimg", "blocklist.txt")

MAX_BYTES = 60 * 1024


def resize(src, dest, size=300, quality=78):
    base = dest + ".base.jpg"
    subprocess.run(["sips", "-Z", str(size), "-s", "format", "jpeg",
                    "-s", "formatOptions", str(quality), src, "--out", base],
                   capture_output=True, text=True)
    if not os.path.exists(base):
        return False
    for q in (quality, 62, 48, 36):
        subprocess.run(["sips", "-p", str(size), str(size), "--padColor", "FFFFFF",
                        "-s", "format", "jpeg", "-s", "formatOptions", str(q),
                        base, "--out", dest], capture_output=True, text=True)
        if os.path.exists(dest) and os.path.getsize(dest) <= MAX_BYTES:
            break
    if os.path.exists(base):
        os.remove(base)
    return os.path.exists(dest)


def host_of(url):
    from urllib.parse import urlparse
    try:
        return urlparse(url).netloc.lower()
    except Exception:  # noqa: BLE001
        return ""


def write_review_sheet(entries):
    """生成人工复核用页面：列出非立创来源的图片与许可，便于快速挑错。"""
    rows = []
    for e in entries:
        if e["source"] == "lcsc":
            continue
        models = "、".join(e["models"])
        src = e.get("sourceUrl") or e.get("imageUrl") or ""
        lic = e.get("license") or "—"
        author = (e.get("author") or "—")[:60]
        link = ('<a href="%s" target="_blank" rel="noopener">来源页</a>' % src) if src else "—"
        rows.append(
            '<tr><td><img src="../%s" alt="%s" loading="lazy"></td>'
            "<td><b>%s</b><br><span class='muted'>%s</span></td>"
            "<td>%s<br><span class='muted'>%s</span></td>"
            "<td>%s</td><td>%s</td></tr>"
            % (e["file"], models, models, e["source"], e.get("credit", ""), lic, author, link))
    html = """<!DOCTYPE html><meta charset="utf-8"><title>图片复核</title>
<style>
body{font-family:system-ui,-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;margin:24px;color:#10233c}
h1{font-size:20px} .muted{color:#6b7d93;font-size:12px}
table{border-collapse:collapse;width:100%%} td{border-bottom:1px solid #e2e9f2;padding:10px;vertical-align:top;font-size:13px}
img{width:120px;height:120px;object-fit:contain;background:#fff;border:1px solid #e2e9f2;border-radius:8px}
code{background:#f5f8fc;padding:1px 4px;border-radius:4px}
</style>
<h1>外部图源图片复核（%d 张）</h1>
<p class="muted">如发现图片与型号不符，把对应型号写进 <code>work/webimg/blocklist.txt</code>（每行一个），
然后重新执行 <code>python3 tools/sync_images.py &amp;&amp; python3 tools/build.py</code> 即可恢复为矢量示意图。</p>
<table>%s</table>""" % (len(rows), "".join(rows))
    path = os.path.join(SITE, "docs", "图片复核.html")
    open(path, "w", encoding="utf-8").write(html)
    print("复核页面：%s（%d 张外部图源）" % (path, len(rows)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    os.makedirs(PARTS_DIR, exist_ok=True)
    blocked = set()
    if os.path.exists(BLOCKLIST):
        blocked = {ln.strip() for ln in open(BLOCKLIST, encoding="utf-8") if ln.strip()}

    entries = []
    converted = reused = failed = 0

    # ---------- 立创商城 ----------
    if os.path.exists(LCSC_INDEX):
        index = json.load(open(LCSC_INDEX, encoding="utf-8"))
        for rec in index.values():
            raw, code = rec.get("raw"), rec.get("code")
            models = [m for m in (rec.get("models") or []) if m not in blocked]
            if not raw or not code or not models:
                if rec.get("error"):
                    failed += 1
                continue
            src = os.path.join(LCSC_RAW, os.path.basename(raw))
            if not os.path.exists(src):
                failed += 1
                continue
            name = "%s.jpg" % code
            dest = os.path.join(PARTS_DIR, name)
            if os.path.exists(dest) and not args.force:
                reused += 1
            elif not resize(src, dest):
                failed += 1
                continue
            else:
                converted += 1
            entries.append({
                "file": "assets/img/parts/%s" % name,
                "code": code,
                "models": models,
                "source": "lcsc",
                "credit": "立创商城",
                "sourceUrl": "https://www.lcsc.com/product-detail/%s.html" % code,
                "matched": rec.get("matched") or "",
                "matchedVia": rec.get("fallbackQuery") or "model",
                "matchType": "exact" if not rec.get("fallbackQuery") else "generic",
                "bytes": os.path.getsize(dest),
            })

    # ---------- 外部图源 ----------
    web_ok = 0
    if os.path.exists(WEB_INDEX):
        windex = json.load(open(WEB_INDEX, encoding="utf-8"))
        for model, rec in windex.items():
            if rec.get("status") != "ok" or model in blocked:
                continue
            rel = rec.get("file")
            if not rel or not os.path.exists(os.path.join(SITE, rel)):
                continue
            source = rec.get("source", "web")
            if source == "commons":
                credit = "Wikimedia Commons" + (" / " + rec["license"] if rec.get("license") else "")
            else:
                credit = host_of(rec.get("imageUrl", "")) or "网络"
            entries.append({
                "file": rel,
                "code": "",
                "models": [model],
                "source": source,
                "credit": credit,
                "sourceUrl": rec.get("pageUrl", ""),
                "imageUrl": rec.get("imageUrl", ""),
                "license": rec.get("license", ""),
                "licenseUrl": rec.get("licenseUrl", ""),
                "author": rec.get("author", ""),
                "matchType": rec.get("matchType", "generic"),
                "bytes": os.path.getsize(os.path.join(SITE, rel)),
            })
            web_ok += 1

    entries.sort(key=lambda e: (e["source"] != "lcsc", e["file"]))
    manifest = {
        "note": "图片来自立创商城、Wikimedia Commons（CC 授权，含作者与许可）或品牌官网/网络检索，"
                "仅作型号识别参考；实际以品牌与批次包装为准。替换为自有实拍图时覆盖同名文件即可。",
        "count": len(entries),
        "bySource": dict(collections.Counter(e["source"] for e in entries)),
        "entries": entries,
    }
    json.dump(manifest, open(os.path.join(PARTS_DIR, "manifest.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    covered = sum(len(e["models"]) for e in entries)
    print("图片 %d 个（立创新压缩 %d / 复用 %d / 失败 %d；外部图源 %d）"
          % (len(entries), converted, reused, failed, web_ok))
    print("来源构成：%s" % manifest["bySource"])
    print("覆盖型号 %d 个，合计 %.1f MB" % (covered, sum(e["bytes"] for e in entries) / 1048576.0))
    print("清单：%s" % os.path.join(PARTS_DIR, "manifest.json"))
    write_review_sheet(entries)
    return 0


if __name__ == "__main__":
    sys.exit(main())

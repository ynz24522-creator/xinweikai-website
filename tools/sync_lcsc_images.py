#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把立创商城抓取结果同步进站点。

输入（抓取阶段的产物）：
  <项目>/work/lcsc/index.json  每次抓取的记录：searchKey / code / raw / matched / models / error
  <项目>/work/lcsc/raw/<C>.jpg 立创商品原图（900×900）

输出：
  assets/img/parts/<C>.jpg          统一压缩为 300×300 的站点用图
  assets/img/parts/manifest.json    来源清单（型号 → 立创编号 → 图片文件 → 原图地址）

用法：
  python3 tools/sync_lcsc_images.py                 # 默认路径
  python3 tools/sync_lcsc_images.py --index <index.json> --raw <raw 目录>
"""

import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
PROJECT = os.path.dirname(os.path.dirname(SITE))  # <项目>/outputs/<站点> → <项目>

DEFAULT_INDEX = os.path.join(PROJECT, "work", "lcsc", "index.json")
DEFAULT_RAW = os.path.join(PROJECT, "work", "lcsc", "raw")
PARTS_DIR = os.path.join(SITE, "assets", "img", "parts")


def resize(src, dest, size=300, quality=78):
    """用 macOS 自带的 sips 等比缩放并转成 JPEG。"""
    cmd = ["sips", "-Z", str(size), "-s", "format", "jpeg",
           "-s", "formatOptions", str(quality), src, "--out", dest]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode == 0 and os.path.exists(dest)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=DEFAULT_INDEX)
    ap.add_argument("--raw", default=DEFAULT_RAW)
    ap.add_argument("--size", type=int, default=300)
    ap.add_argument("--quality", type=int, default=78)
    ap.add_argument("--force", action="store_true", help="重新压缩已存在的图片")
    args = ap.parse_args()

    if not os.path.exists(args.index):
        print("找不到抓取索引：%s" % args.index)
        return 1

    os.makedirs(PARTS_DIR, exist_ok=True)
    with open(args.index, encoding="utf-8") as fh:
        index = json.load(fh)

    entries = []
    converted = reused = failed = 0
    for rec in index.values():
        raw = rec.get("raw")
        code = rec.get("code")
        models = rec.get("models") or []
        if not raw or not code or not models:
            if rec.get("error"):
                failed += 1
            continue
        src = os.path.join(args.raw, os.path.basename(raw))
        if not os.path.exists(src):
            failed += 1
            continue
        name = "%s.jpg" % code
        dest = os.path.join(PARTS_DIR, name)
        if os.path.exists(dest) and not args.force:
            reused += 1
        else:
            if not resize(src, dest, args.size, args.quality):
                failed += 1
                continue
            converted += 1
        entries.append({
            "file": "assets/img/parts/%s" % name,
            "code": code,
            "matched": rec.get("matched") or "",
            "sourceUrl": rec.get("sourceUrl") or "",
            "matchedVia": rec.get("fallbackQuery") or "model",
            "models": models,
            "bytes": os.path.getsize(dest),
        })

    entries.sort(key=lambda e: e["code"])
    manifest = {
        "note": "商品图片来自立创商城（lcsc.com），仅作型号识别参考；如需替换为自有实拍图，"
                "覆盖 assets/img/parts/ 下同名文件或在 data.js 中改 img 字段即可。",
        "count": len(entries),
        "imageCount": len(entries),
        "entries": entries,
    }
    with open(os.path.join(PARTS_DIR, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)

    covered = sum(len(e["models"]) for e in entries)
    total_bytes = sum(e["bytes"] for e in entries)
    print("图片文件 %d 个（新压缩 %d，复用 %d，失败 %d）" % (len(entries), converted, reused, failed))
    print("覆盖型号 %d 个，合计 %.1f MB" % (covered, total_bytes / 1048576.0))
    print("清单：%s" % os.path.join(PARTS_DIR, "manifest.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为「还没有实物图」的型号从外部图源补齐图片。

图源优先级：
  1. Wikimedia Commons（CC0 / Public domain / CC BY / CC BY-SA，带作者与许可）
  2. 品牌官网 / 授权分销（经必应限定站点检索，来源页标题需含型号）
  3. 必应图片兜底（来源页标题或图片地址含型号）

产物：
  assets/img/parts/web/<slug>.jpg   300×300 白底 JPEG
  work/webimg/index.json            抓取记录（来源页 / 图片地址 / 许可 / 作者 / 匹配方式）
  work/webimg/blocklist.txt         人工复核后要撤掉的型号（每行一个）

用法：
  python3 tools/fetch_web_images.py --limit 20              # 先跑 20 个型号
  python3 tools/fetch_web_images.py                         # 跑完剩余全部
  python3 tools/fetch_web_images.py --only HC-05,NEO-6M     # 只跑指定型号
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(HERE)
PROJECT = os.path.dirname(os.path.dirname(SITE))

DATA_JS = os.path.join(SITE, "assets", "js", "data.js")
WEB_DIR = os.path.join(SITE, "assets", "img", "parts", "web")
WORK_DIR = os.path.join(PROJECT, "work", "webimg")
INDEX_PATH = os.path.join(WORK_DIR, "index.json")
BLOCKLIST = os.path.join(WORK_DIR, "blocklist.txt")

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 通用件（工具 / 耗材 / 五金 / 电池 / 散热）优先用 Commons 的 CC 图，查询词按类型映射
COMMONS_TERMS = {
    "tool-solder": "soldering iron",
    "tool-meter": "digital multimeter",
    "tool-hand": "wire stripper",
    "tool-esd": "anti static wrist strap",
    "cons-heat": "heat shrink tubing",
    "cons-clean": "solder flux",
    "cons-breadboard": "breadboard",
    "thermal-heatsink": "aluminium heatsink",
    "thermal-fan": "computer fan",
    "thermal-paste": "thermal grease",
    "hardware-standoff": "hex standoff",
    "hardware-screw": "screw assortment",
    "battery": "coin cell battery",
    "adapter": "power adapter",
    "power-module": "dc dc converter module",
    "led-tht": "LED 5mm red",
    "ir-emitter": "infrared LED",
    "ir-receiver": "infrared receiver module",
    "led-addressable": "ws2812b led",
    "opto-coupler": "optocoupler",
    "antenna": "whip antenna sma",
    "sw-slide": "slide switch",
    "relay-ssr": "solid state relay",
    "resonator": "ceramic resonator",
    "osc": "crystal oscillator smd",
    "conn-wire": "jst connector",
}

# 型号级检索词（Commons 找不到时用于必应）
TYPE_KEYWORDS = {
    "ble-module": "bluetooth module",
    "lora-module": "lora module",
    "cellular-module": "cellular module",
    "gnss-module": "gps module",
    "wifi-module": "wifi module",
    "wireless-module": "wireless module",
    "ind-chip": "power inductor",
    "igbt": "igbt transistor",
    "dram": "dram chip",
    "tvs-array": "tvs diode array",
    "ptc-resettable": "resettable fuse",
    "cap-electrolytic": "electrolytic capacitor",
    "cap-film": "film capacitor",
    "cap-super": "supercapacitor",
    "res-ptc": "pt100 temperature sensor",
    "xfmr": "isolation transformer module",
    "sensor-motion": "mpu6050 module",
    "pmic": "power mux ic",
    "conn-usb": "usb connector",
}

# 必应候选优先来源（品牌官网 / 授权分销 / 常见电子社区）
PREFERRED_HOSTS = (
    "espressif.com", "espressif.cn", "quectel.com", "u-blox.com", "ublox.com",
    "everlight.com", "waveshare.net", "waveshare.com", "seeedstudio.com",
    "ai-thinker.com", "aithinker.com", "nordicsemi.com", "ti.com", "st.com",
    "infineon.com", "onsemi.com", "microchip.com", "mouser.com", "mouser.cn",
    "digikey.com", "digikey.cn", "lcsc.com", "szlcsc.com", "hqchip.com",
    "ickey.cn", "components101.com", "lastminuteengineers.com",
    "randomnerdtutorials.com", "electronicwings.com", "arduino.cc",
    "instructables.com", "sparkfun.com", "adafruit.com",
)

SKIP_IMAGE_HOSTS = ("bing.com", "msn.com", "facebook.com", "instagram.com", "tiktok.com")


def log(msg):
    print(msg, flush=True)


def http_get(url, timeout=25, headers=None, binary=False):
    req = urllib.request.Request(url, headers=headers or {})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    return data if binary else data.decode("utf-8", "replace")


def load_parts():
    text = open(DATA_JS, encoding="utf-8").read()
    payload = json.loads(text[text.index("= ") + 2:text.rindex(";")])
    out = []
    for cat in payload["categories"]:
        for sub in cat["subs"]:
            for part in sub["parts"]:
                if part.get("img"):
                    continue
                out.append({
                    "model": part["m"], "brand": part["b"], "pkg": part["k"],
                    "params": part["p"], "type": part["t"], "catId": cat["id"],
                    "subId": sub["id"], "catZh": cat["zh"], "subZh": sub["zh"],
                })
    return out


def commons_search(term, limit=4):
    """返回 Commons 候选：{imageUrl, pageUrl, license, author, title}"""
    url = ("https://commons.wikimedia.org/w/api.php?action=query&generator=search"
           "&gsrsearch=" + urllib.parse.quote("filetype:bitmap " + term) +
           "&gsrnamespace=6&gsrlimit=%d&prop=imageinfo&iiprop=url|extmetadata"
           "&iiurlwidth=800&format=json" % limit)
    try:
        raw = http_get(url, headers={"User-Agent": "xinweikai-site/1.0 (17317103@qq.com)"})
        data = json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        log("  commons api error: %s" % str(exc)[:70])
        return []
    out = []
    for page in (data.get("query", {}).get("pages", {}) or {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata", {})
        title = page.get("title", "")
        out.append({
            "title": title.replace("File:", ""),
            "imageUrl": info.get("thumburl") or info.get("url"),
            "pageUrl": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(" ", "_")),
            "license": (meta.get("LicenseShortName", {}) or {}).get("value", ""),
            "licenseUrl": (meta.get("LicenseUrl", {}) or {}).get("value", ""),
            "author": re.sub("<[^>]+>", "", (meta.get("Artist", {}) or {}).get("value", ""))[:80],
        })
    return [c for c in out if c["imageUrl"]]


def bing_search(query, limit=12):
    """返回必应图片候选：{imageUrl, pageUrl, pageTitle}"""
    url = "https://www.bing.com/images/search?q=" + urllib.parse.quote(query) + "&form=HDRSC2"
    try:
        raw = http_get(url, headers={
            "User-Agent": UA,
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        })
    except Exception as exc:  # noqa: BLE001
        log("  bing error: %s" % str(exc)[:70])
        return []
    items = []
    for chunk in raw.split('murl&quot;:&quot;')[1:limit + 4]:
        img = html.unescape(chunk.split("&quot;")[0])
        before = raw[:raw.index(chunk)]
        m = re.findall(r'purl&quot;:&quot;([^&]+)&quot;', before)
        page = html.unescape(m[-1]) if m else ""
        titles = re.findall(r'&quot;t&quot;:&quot;([^&]{2,120})&quot;', before)
        items.append({"imageUrl": img, "pageUrl": page,
                      "pageTitle": html.unescape(titles[-1]) if titles else ""})
    return items


def norm(text):
    return re.sub(r"[^a-z0-9]", "", str(text or "").lower())


def host_of(url):
    try:
        return urllib.parse.urlparse(url).netloc.lower()
    except Exception:  # noqa: BLE001
        return ""


def choose_commons(part, candidates):
    if not candidates:
        return None
    best = candidates[0]
    exact = norm(part["model"]) in norm(best["title"])
    return dict(best, matchType="exact" if exact else "generic", source="commons")


def choose_bing(part, candidates, extra_words):
    model_key = norm(part["model"])
    scored = []
    for idx, c in enumerate(candidates):
        if not c["imageUrl"].startswith("http"):
            continue
        host = host_of(c["imageUrl"])
        if any(skip in host for skip in SKIP_IMAGE_HOSTS):
            continue
        if not re.search(r"\.(jpg|jpeg|png|webp)(\?|$)", c["imageUrl"], re.I):
            continue
        hay = norm(c["pageTitle"]) + norm(c["pageUrl"]) + norm(c["imageUrl"])
        score = 0
        if model_key and model_key in hay:
            score += 6
        if any(h in host for h in PREFERRED_HOSTS):
            score += 4
        if re.search(r"(module|sensor|led|battery|tool|socket|connector|fan|heatsink)", c["pageTitle"], re.I):
            score += 1
        score -= idx * 0.2
        if score > 0:
            scored.append((score, c, host))
    if not scored:
        return None
    scored.sort(key=lambda x: -x[0])
    score, best, host = scored[0]
    exact = bool(model_key) and model_key in (norm(best["pageTitle"]) + norm(best["imageUrl"]))
    return dict(best, matchType="exact" if exact else "generic", source="brand" if any(
        h in host for h in PREFERRED_HOSTS) else "web", host=host)


def download(url, referer, dest):
    cmd = ["curl", "-sS", "-L", "--max-time", "25", "-A", UA, "-o", dest,
           "-w", "%{http_code} %{size_download} %{content_type}"]
    if referer:
        cmd += ["-e", referer]
    cmd.append(url)
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    parts = proc.stdout.strip().split()
    if len(parts) < 3 or parts[0] != "200":
        return None
    size = int(parts[1])
    if size < 4000 or size > 6 * 1024 * 1024 or "image" not in parts[2]:
        return None
    return size


MAX_BYTES = 60 * 1024


def to_300(src, dest, quality=78):
    """等比缩到 300 内、补白到 300×300，并控制单张体积 < 60KB。"""
    base = dest + ".base.jpg"
    # 第一步：先转成 JPEG 并缩到 300 以内（某些来源实际是 PNG/WebP，必须显式转码）
    subprocess.run(["sips", "-Z", "300", "-s", "format", "jpeg",
                    "-s", "formatOptions", str(quality), src, "--out", base],
                   capture_output=True, text=True)
    if not os.path.exists(base):
        return False
    for q in (quality, 62, 48, 36):
        # 第二步：白底补边成 300×300（输入已是 JPEG，输出保持 JPEG）
        subprocess.run(["sips", "-p", "300", "300", "--padColor", "FFFFFF",
                        "-s", "format", "jpeg", "-s", "formatOptions", str(q),
                        base, "--out", dest], capture_output=True, text=True)
        if os.path.exists(dest) and os.path.getsize(dest) <= MAX_BYTES:
            break
        if not os.path.exists(dest):
            return False
    if os.path.exists(base):
        os.remove(base)
    return os.path.exists(dest) and os.path.getsize(dest) <= MAX_BYTES


def reencode_oversized(quality=78):
    """把已存在但超过 60KB 的图片重新压一遍（保持文件名，便于复用索引）。"""
    fixed = 0
    for folder in (WEB_DIR, os.path.join(SITE, "assets", "img", "parts")):
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            path = os.path.join(folder, name)
            if not name.endswith(".jpg") or not os.path.isfile(path):
                continue
            if os.path.getsize(path) <= MAX_BYTES:
                continue
            src = path + ".src.jpg"
            os.rename(path, src)
            if to_300(src, path, quality) and os.path.getsize(path) <= MAX_BYTES:
                fixed += 1
            else:
                os.replace(src, path)
                continue
            os.remove(src)
    return fixed


def slugify(model):
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", model).strip("-").lower()
    return (slug or "part")[:48]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="本次最多处理多少个型号")
    ap.add_argument("--only", default="", help="只处理这些型号（逗号分隔）")
    ap.add_argument("--min-commons", type=int, default=1)
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--reencode", action="store_true", help="只把超过 60KB 的图片重新压缩")
    args = ap.parse_args()

    os.makedirs(WEB_DIR, exist_ok=True)
    os.makedirs(WORK_DIR, exist_ok=True)
    if args.reencode:
        log("重新压缩超标图片：%d 张" % reencode_oversized())
        return 0
    index = {}
    if os.path.exists(INDEX_PATH):
        index = json.load(open(INDEX_PATH, encoding="utf-8"))
    blocked = set()
    if os.path.exists(BLOCKLIST):
        blocked = {ln.strip() for ln in open(BLOCKLIST, encoding="utf-8") if ln.strip()}

    parts = load_parts()
    if args.only:
        wanted = {m.strip() for m in args.only.split(",") if m.strip()}
        parts = [p for p in parts if p["model"] in wanted]
    todo = [p for p in parts if p["model"] not in index or index[p["model"]].get("status") != "ok"]
    todo = [p for p in todo if p["model"] not in blocked]
    if args.limit:
        todo = todo[:args.limit]
    log("待处理型号 %d 个（已有记录 %d，黑名单 %d）" % (len(todo), len(index), len(blocked)))

    ok = fail = 0
    for i, part in enumerate(todo, 1):
        model, typ = part["model"], part["type"]
        record = {"model": model, "type": typ, "pkg": part["pkg"], "brand": part["brand"],
                  "catZh": part["catZh"], "subZh": part["subZh"], "status": "fail"}
        chosen = None

        # 1) Commons（授权图源）
        term = COMMONS_TERMS.get(typ) or (TYPE_KEYWORDS.get(typ, "") + " " + part["pkg"])
        if term.strip():
            commons = commons_search(term.strip(), 4)
            chosen = choose_commons(part, commons)
            record["commonsQuery"] = term.strip()
            if chosen:
                record["candidates"] = len(commons)

        # 2/3) 必应：先用型号+类型词，再用类型词
        if not chosen:
            queries = [" ".join(x for x in [model, TYPE_KEYWORDS.get(typ, ""), "product"] if x)]
            queries.append(TYPE_KEYWORDS.get(typ, "") + " " + part["pkg"])
            for q in queries:
                if not q.strip():
                    continue
                cands = bing_search(q, 12)
                chosen = choose_bing(part, cands, None)
                time.sleep(args.sleep)
                if chosen:
                    record["bingQuery"] = q
                    break

        if not chosen:
            record["error"] = "no-candidate"
            index[model] = record
            fail += 1
            log("[%d/%d] ✗ %s（未找到候选）" % (i, len(todo), model))
        else:
            name = slugify(model) + ".jpg"
            dest = os.path.join(WEB_DIR, name)
            tmp = dest + ".raw"
            size = download(chosen["imageUrl"], chosen.get("pageUrl", ""), tmp)
            if size and to_300(tmp, dest):
                os.remove(tmp)
                record.update({
                    "status": "ok",
                    "file": "assets/img/parts/web/" + name,
                    "source": chosen["source"],
                    "matchType": chosen.get("matchType", "generic"),
                    "pageUrl": chosen.get("pageUrl", ""),
                    "imageUrl": chosen["imageUrl"],
                    "license": chosen.get("license", ""),
                    "licenseUrl": chosen.get("licenseUrl", ""),
                    "author": chosen.get("author", ""),
                    "title": chosen.get("title") or chosen.get("pageTitle", ""),
                    "bytes": os.path.getsize(dest),
                })
                ok += 1
                log("[%d/%d] ✓ %s ← %s (%s, %s)" % (i, len(todo), model,
                                                    host_of(chosen["imageUrl"]),
                                                    chosen["source"], record["matchType"]))
            else:
                if os.path.exists(tmp):
                    os.remove(tmp)
                record["error"] = "download-failed"
                record["imageUrl"] = chosen["imageUrl"]
                record["pageUrl"] = chosen.get("pageUrl", "")
                fail += 1
                log("[%d/%d] ✗ %s（下载失败）" % (i, len(todo), model))
        index[model] = record
        json.dump(index, open(INDEX_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        time.sleep(args.sleep)

    log("本轮完成：成功 %d，失败 %d；累计记录 %d" % (ok, fail, len(index)))
    log("下一步：python3 tools/sync_images.py  →  python3 tools/build.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())

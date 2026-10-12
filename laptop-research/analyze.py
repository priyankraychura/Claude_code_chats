#!/usr/bin/env python3
"""Parse specs out of the scraped listings and rank them for heavy dev work.

Workload being scored: Android Studio + emulators, Flutter, .NET, Java, MERN,
Cursor / Claude Code, with frontend + backend + emulator running together.
That workload is bound by (in order): RAM, sustained multi-core CPU, SSD space,
then platform compatibility (x86 Windows/Linux runs everything; Apple Silicon
runs nearly everything; Windows-on-ARM still has gaps for Android emulators and
some x86-only toolchains).

Reads data/flipkart.json, data/amazon.json, data/cpu_scores.json, and if
present data/cpu_single.json (cpu_single_thread.py) and data/overrides.json
(facts verified on product pages, keyed by listing URL).
Writes data/ranked.csv, data/ranked.json and data/shortlist.json
"""
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")


def load(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


CPU_SCORES = load("cpu_scores.json") or {}
CPU_SINGLE = load("cpu_single.json") or {}
OVERRIDES = load("overrides.json") or {}


# ---------------------------------------------------------------- spec parsing

def parse_cpu(text):
    """Return a canonical CPU name (PassMark style) or None."""
    t = re.sub(r"\s+", " ", text.replace("™", "").replace("®", ""))
    m = re.search(r"Ryzen\s*AI\s*(?:MAX\+?\s*)?([3579])\s*(?:(?:Octa|Hexa|Quad|Deca|12)\s*Core\s*)?(?:[3579]\s+)?(HX\s*)?(\d{3})\b", t, re.I)
    if m:
        hx = "HX " if m.group(2) else ""
        return f"AMD Ryzen AI {m.group(1)} {hx}{m.group(3)}"
    m = re.search(r"Ryzen\s*([3579])\s*(?:(?:Octa|Hexa|Quad)\s*Core\s*)?(?:\d{1,2}th\s*Gen\s*)?[-\s]*(\d{4}[A-Z]{0,3}|\d{3}\b)", t, re.I)
    if m:
        return f"AMD Ryzen {m.group(1)} {m.group(2).upper()}"
    m = re.search(r"(?:Core\s*)?Ultra\s*([3579])\s*(?:Processor\s*)?(?:Series\s*\d\s*)?[-\s]*(\d{3}[A-Z]{0,2})\b", t, re.I)
    if m:
        return f"Intel Core Ultra {m.group(1)} {m.group(2).upper()}"
    # i5-13420H, i7 1355U, "i5 13th Gen 1334U", "i3 13th Gen -1305U", 1165G7
    m = re.search(r"\bi([3579])\s*[- ]?\s*(?:\d{1,2}th\s+Gen\s*[-\s]*)?(1[0-4]\d{2,3}(?:G\d|[A-Z]{0,2}))\b", t, re.I)
    if m:
        return f"Intel Core i{m.group(1)}-{m.group(2).upper()}"
    # Core 7 240H, Core5-210H, "Core 5 14th Gen 120U", "Core 7 Series 2 240H", Core 5 320
    m = re.search(r"\bCore\s*([3579])\s*(?:Processor\s*)?(?:Series\s*\d\s*)?(?:\d{1,2}th\s*Gen\s*)?[-\s]*(\d{3}[A-Z]{0,2})\b", t, re.I)
    if m:
        return f"Intel Core {m.group(1)} {m.group(2).upper()}"
    m = re.search(r"\b(?:Apple\s*)?(M[1-5])\s*(Pro|Max)?\s*(?:chip)?", t)
    if m and re.search(r"MacBook|Apple", t, re.I):
        return f"Apple {m.group(1)}" + (f" {m.group(2)}" if m.group(2) else "")
    m = re.search(r"Snapdragon\s*X\s*(Elite|Plus)?\s*[-\s]*(X1[EP]?[-\s]?\d{2}[-\s]?\d{3})?", t, re.I)
    if m:
        return ("Qualcomm Snapdragon X " + (m.group(1) or "") + " " + (m.group(2) or "")).strip()
    return None


def cpu_score(cpu):
    if not cpu:
        return None
    if cpu in CPU_SCORES:
        return CPU_SCORES[cpu]
    if cpu.startswith("Apple M"):
        # MacBook Air/Pro base chips are listed by core count; take the
        # 10-core part (what the Air/Pro ship with in this price band).
        base = cpu.replace("Apple ", "")
        cands = {k: v for k, v in CPU_SCORES.items()
                 if re.fullmatch(rf"Apple {re.escape(base)} \d+ Core( \d+ MHz)?", k)}
        return max(cands.values()) if cands else None
    if cpu.startswith("Qualcomm"):
        # "Qualcomm Snapdragon X Elite X1E-78-100" → match on the hyphen-less
        # part number; a bare "Snapdragon X" is the 8-core X1-26-100.
        m = re.search(r"(X\d[EP]?)[-\s]?(\d{2})[-\s]?(\d{3})", cpu)
        part = "".join(m.groups()) if m else {"Elite": "X1E78100", "Plus": "X1P42100"}.get(cpu.split()[-1], "X126100")
        cands = [v for k, v in CPU_SCORES.items() if "Snapdragon X" in k and part in re.sub(r"[-\s]", "", k)]
        return max(cands) if cands else None
    # PassMark sometimes appends iGPU names ("AMD Ryzen 7 7735HS with Radeon Graphics").
    cands = [(k, v) for k, v in CPU_SCORES.items() if k.startswith(cpu + " ")]
    if cands:
        return max(v for _, v in cands)
    return None


def parse_ram(rec, text):
    m = re.search(r"\((\d{1,3})\s*GB\s*/\s*\d+\s*(?:GB|TB)", rec["title"])  # Flipkart "(32 GB/1 TB SSD/..."
    if m:
        return int(m.group(1))
    # Explicit "RAM"/"Memory" first so GPU VRAM ("RTX 3050 6GB", "4GB GDDR6")
    # isn't mistaken for system memory.
    for pat in [r"(\d{1,3})\s*GB\s*(?:Unified\s*)?(?:RAM|Memory)\b", r"(\d{1,3})\s*GB\s*Unified",
                r"(\d{1,3})\s*GB\s*(?:LP)?DDR\s*[45]", r"\b(\d{1,3})GB\s*/\s*\d+\s*(?:GB|TB)"]:
        m = re.search(pat, text, re.I)
        if m:
            return int(m.group(1))
    return None


def parse_ram_type(text):
    m = re.search(r"\b(LPDDR\s*\dX?|DDR\s*\d)\b", text, re.I)
    if m:
        return m.group(1).upper().replace(" ", "")
    if re.search(r"unified memory|MacBook", text, re.I):
        return "Unified"
    return None


def parse_storage(rec, text):
    m = re.search(r"\(\d{1,3}\s*GB\s*/\s*(\d+)\s*(GB|TB)", rec["title"])
    if not m:
        m = re.search(r"(\d+(?:\.\d)?)\s*(TB|GB)\s*(?:PCIe\s*)?(?:Gen\s*\d\s*)?(?:NVMe\s*)?(?:M\.2\s*)?SSD", text, re.I)
    if not m:
        m = re.search(r"(\d+)\s*(TB|GB)\s*(?:storage|internal)", text, re.I)
    if not m:
        return None
    n = float(m.group(1))
    return int(n * 1024) if m.group(2).upper() == "TB" else int(n)


def parse_gpu(text):
    m = re.search(r"RTX\s*(\d{4})\s*(Ti)?", text, re.I)
    if m:
        return f"RTX {m.group(1)}" + (" Ti" if m.group(2) else "")
    m = re.search(r"\b(RX\s*\d{4}[MS]?|Arc\s*A\d{3}M)\b", text, re.I)
    if m:
        return m.group(1)
    return "Integrated"


def parse_display(text):
    size = None
    m = re.search(r"(\d{2}(?:\.\d)?)\s*(?:inch|\"|”|-inch|″)", text, re.I)
    if m:
        size = float(m.group(1))
    else:
        m = re.search(r"\((\d{2}\.\d{1,2})\s*cm\)|(\d{2}\.\d{1,2})\s*cm", text)
        if m:
            size = round(float(m.group(1) or m.group(2)) / 2.54, 1)
    hz = None
    m = re.search(r"(\d{2,3})\s*Hz", text, re.I)
    if m:
        hz = int(m.group(1))
    res = None
    for key in ["3.2K", "3K", "2.8K", "2.5K", "2.2K", "QHD+", "QHD", "WQXGA", "WUXGA", "FHD+", "FHD", "OLED"]:
        if key.lower() in text.lower():
            res = key
            break
    oled = "oled" in text.lower()
    return size, hz, res, oled


def parse_weight(text):
    m = re.search(r"(\d(?:\.\d{1,2})?)\s*kg", text, re.I)
    return float(m.group(1)) if m else None


def platform(cpu, text):
    if cpu and cpu.startswith("Apple") or re.search(r"MacBook", text, re.I):
        return "macOS (Apple Silicon)"
    if cpu and cpu.startswith("Qualcomm") or re.search(r"Snapdragon", text, re.I):
        return "Windows on ARM"
    if re.search(r"Chromebook|Chrome OS", text, re.I):
        return "ChromeOS"
    return "x86 (Windows/Linux)"


def brand(title):
    first = title.split()[0].upper()
    return {"APPLE": "Apple", "MACBOOK": "Apple"}.get(first, first.capitalize())


# -------------------------------------------------------------------- scoring

def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def score(r):
    parts = {}
    # CPU: PassMark multi-thread (builds, emulator, indexing) blended with
    # single-thread (IDE/TS-server responsiveness). 10k multi ≈ old quad-core,
    # 35k ≈ HX-class; 2.5k single ≈ Zen 2, 4.5k ≈ current flagships.
    if r["cpu_mark"]:
        multi = clamp((r["cpu_mark"] - 10000) / 25000)
        single = clamp(((r["cpu_single"] or 3000) - 2500) / 2000)
        parts["cpu"] = 0.65 * multi + 0.35 * single
        # 15 W U-series / ARM parts drop furthest below their burst score
        # during multi-minute Gradle/Flutter builds.
        if re.search(r"\d+U$|Snapdragon", r["cpu"]):
            parts["cpu"] *= 0.85
    else:
        parts["cpu"] = 0.15
    # RAM: the hard ceiling for IDE + emulator + Docker + browser. With DDR5
    # SO-DIMMs at ~₹22.5k per 16 GB stick (Flipkart, Oct 2026), "buy 16 GB and
    # upgrade" no longer fits the budget, so RAM that ships in the box counts most.
    ram, soldered = r["ram_gb"] or 0, r["ram_soldered"]
    if ram >= 32:
        parts["ram"] = 1.0
    elif ram >= 24:
        parts["ram"] = 0.8
    elif ram >= 16:
        parts["ram"] = 0.15 if soldered else 0.35
    else:
        parts["ram"] = 0.0
    if r["ram_type"] == "DDR4":
        parts["ram"] -= 0.05
    if r.get("single_channel"):
        parts["ram"] -= 0.1  # one stick: half the memory bandwidth
    st = r["storage_gb"] or 0
    parts["ssd"] = 1.0 if st >= 1000 else 0.55 if st >= 500 else 0.1
    parts["platform"] = {"x86 (Windows/Linux)": 1.0, "macOS (Apple Silicon)": 0.75,
                         "Windows on ARM": 0.25, "ChromeOS": 0.0}[r["platform"]]
    size = r["screen_in"] or 15
    parts["display"] = clamp(0.5 + (0.25 if size >= 15.5 else 0.1 if size >= 14 else 0)
                             + (0.25 if r["resolution"] in ("3.2K", "3K", "2.8K", "2.5K", "QHD+", "QHD", "WQXGA", "2.2K") else 0))
    # Bayesian-shrunk rating so a 5.0 from 2 buyers doesn't beat 4.4 from 2,000.
    rating, n = r["rating"] or 0, r["rating_count"] or 0
    prior, k = 4.0, 30
    parts["rating"] = clamp(((rating * n + prior * k) / (n + k) - 3.5) / 1.3)

    weights = {"cpu": 0.30, "ram": 0.35, "ssd": 0.10, "platform": 0.12, "display": 0.05, "rating": 0.08}
    total = sum(parts[k] * w for k, w in weights.items())
    return round(100 * total, 1), parts


# ----------------------------------------------------------------------- main

def enrich(rec):
    text = " ".join([rec.get("title") or "", rec.get("subtitle") or "", " ".join(rec.get("key_specs") or [])])
    cpu = parse_cpu(text)
    ram_type = parse_ram_type(text)
    size, hz, res, oled = parse_display(text)
    r = {
        "store": rec["store"],
        "title": rec["title"],
        "brand": brand(rec["title"]),
        "price": rec["price"],
        "mrp": rec.get("mrp"),
        "rating": rec.get("rating") or None,
        "rating_count": rec.get("rating_count") or 0,
        "cpu": cpu,
        "cpu_mark": cpu_score(cpu),
        "ram_gb": parse_ram(rec, text),
        "ram_type": ram_type,
        # LPDDR and Apple unified memory are always soldered. Amazon titles
        # often say "(Upgradeable)" explicitly.
        "ram_soldered": bool(ram_type and (ram_type.startswith("LPDDR") or ram_type == "Unified"))
                        and not re.search(r"upgrad", text, re.I),
        "storage_gb": parse_storage(rec, text),
        "gpu": parse_gpu(text),
        "screen_in": size,
        "refresh_hz": hz,
        "resolution": res,
        "oled": oled,
        "weight_kg": parse_weight(text),
        "platform": platform(cpu, text),
        "in_stock": rec.get("in_stock", True),
        "sponsored": rec.get("sponsored", False),
        "url": rec["url"],
    }
    r["cpu_single"] = CPU_SINGLE.get(cpu)
    # Facts checked on the product page beat whatever the title claims.
    r.update(OVERRIDES.get(rec["url"], {}))
    r["score"], r["parts"] = score(r)
    return r


def main():
    raw = load("flipkart.json") + load("amazon.json")
    rows = [enrich(r) for r in raw if r.get("title") and r.get("price")]
    # Drop accessories / refurbished / non-laptops that leak into searches.
    junk = re.compile(r"refurbished|renewed|bag|sleeve|charger|adapter|stand\b|keyboard only|skin", re.I)
    rows = [r for r in rows if not junk.search(r["title"]) and r["in_stock"] and not r.get("exclude")]
    rows.sort(key=lambda r: (-r["score"], r["price"]))

    with open(os.path.join(DATA, "ranked.json"), "w") as f:
        json.dump(rows, f, indent=1, ensure_ascii=False)
    cols = ["score", "store", "price", "brand", "cpu", "cpu_mark", "cpu_single", "ram_gb", "ram_type",
            "ram_soldered", "single_channel", "storage_gb", "gpu", "screen_in", "refresh_hz", "resolution",
            "weight_kg", "platform", "rating", "rating_count", "note", "title", "url"]
    with open(os.path.join(DATA, "ranked.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # Shortlist for the detail-page pass: best listing per distinct config
    # (brand + CPU + RAM + SSD), top 16 by score.
    seen, shortlist = set(), []
    for r in rows:
        key = (r["brand"], r["cpu"], r["ram_gb"], r["storage_gb"], r["store"])
        if r["cpu_mark"] and key not in seen:
            seen.add(key)
            shortlist.append(r)
        if len(shortlist) == 16:
            break
    with open(os.path.join(DATA, "shortlist.json"), "w") as f:
        json.dump(shortlist, f, indent=1, ensure_ascii=False)

    unparsed_cpu = sum(1 for r in rows if not r["cpu_mark"])
    print(f"{len(rows)} listings ranked ({unparsed_cpu} without a CPU benchmark match)")
    for r in rows[:60]:
        print(f'{r["score"]:5.1f} {r["store"][:2]} ₹{r["price"]:>6} | {str(r["cpu"])[:26]:26} {str(r["cpu_mark"] or "?"):>6} | '
              f'{r["ram_gb"]}GB {r["ram_type"] or "?":7}{"(s)" if r["ram_soldered"] else "   "} | {r["storage_gb"]}GB | '
              f'{r["gpu"][:9]:9} | {r["rating"] or "-"}({r["rating_count"]}) | {r["title"][:70]}')


if __name__ == "__main__":
    main()

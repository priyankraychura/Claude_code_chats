#!/usr/bin/env python3
"""Fetch PassMark single-thread ratings for every CPU that appears in the listings.

The vendor lists only carry the multi-thread CPU Mark; single-thread speed
(IDE responsiveness, Gradle configuration, TypeScript server) needs each
CPU's own page. Run after analyze.py once (it needs data/ranked.json), then
re-run analyze.py to fold the scores in.

Writes data/cpu_single.json  {"Intel Core i7-13620H": 3549, ...}
"""
import html
import json
import os
import re
import subprocess
import time
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")


def passmark_ids():
    """Map PassMark CPU name -> id from the cached vendor list pages."""
    ids = {}
    for vendor in ("intel", "amd", "other"):
        body = subprocess.run(["curl", "-sL", "--compressed", "-m", "60", "-A", UA,
                               f"https://www.cpubenchmark.net/cpu-list/{vendor}"],
                              capture_output=True).stdout.decode("utf-8", "ignore")
        for cid, name in re.findall(r'<tr id="cpu(\d+)"><td><a href="[^"]*">([^<]*)</a>', body):
            ids[html.unescape(name).strip()] = cid
    return ids


def single_thread(name, cid):
    url = f"https://www.cpubenchmark.net/cpu.php?cpu={urllib.parse.quote_plus(name)}&id={cid}"
    body = subprocess.run(["curl", "-sL", "--compressed", "-m", "40", "-A", UA, url],
                          capture_output=True).stdout.decode("utf-8", "ignore")
    text = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", body)))
    m = re.search(r"Single Thread Rating ([0-9,]+)", text)
    return int(m.group(1).replace(",", "")) if m else None


def main():
    with open(os.path.join(DATA, "ranked.json")) as f:
        rows = json.load(f)
    with open(os.path.join(DATA, "cpu_scores.json")) as f:
        multi = json.load(f)
    out_path = os.path.join(DATA, "cpu_single.json")
    out = json.load(open(out_path)) if os.path.exists(out_path) else {}
    ids = passmark_ids()
    # Resolve each listing CPU to the PassMark entry analyze.py matched it to
    # (same multi-thread score), then fetch that entry's page.
    for cpu in sorted({r["cpu"] for r in rows if r["cpu"] and r["cpu_mark"]}):
        if cpu in out:
            continue
        mark = next(r["cpu_mark"] for r in rows if r["cpu"] == cpu)
        names = [n for n in ids if n == cpu] or [n for n, v in multi.items() if v == mark and n in ids]
        if not names:
            print(f"  ? {cpu}: no PassMark page")
            continue
        st = single_thread(names[0], ids[names[0]])
        out[cpu] = st
        print(f"  {cpu:34} -> {names[0]:40} single={st}")
        time.sleep(0.5)
    with open(out_path, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(f"saved {len(out)} single-thread ratings to {out_path}")


if __name__ == "__main__":
    main()

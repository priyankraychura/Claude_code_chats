#!/usr/bin/env python3
"""Fetch the full spec sheet for shortlisted Flipkart listings.

Search cards only carry ~6 key specs; the product page has the full table
(RAM type/frequency, expandable memory, weight, battery, panel, ports...).
The table lives in the page's __INITIAL_STATE__ as label_0 (name) /
label_1|label_2 (value) widgets.

Usage: python3 details_flipkart.py URL [URL ...]   (or reads data/shortlist.json)
Writes data/details_flipkart.json  {url: {spec name: value}}
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "data", "details_flipkart.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")


def text_of(node):
    v = (node or {}).get("value") or {}
    t = v.get("text")
    if isinstance(t, list):
        return ", ".join(str(x) for x in t)
    return t


def spec_pairs(o, out):
    if isinstance(o, dict):
        if "label_0" in o and ("label_1" in o or "label_2" in o):
            k = text_of(o["label_0"])
            v = text_of(o.get("label_2")) or text_of(o.get("label_1"))
            if k and v and k not in out:
                out[k.strip()] = v.strip()
        for v in o.values():
            spec_pairs(v, out)
    elif isinstance(o, list):
        for v in o:
            spec_pairs(v, out)


def fetch_specs(url):
    for attempt in range(3):
        body = subprocess.run(["curl", "-sL", "--compressed", "-m", "45", "-A", UA, url],
                              capture_output=True).stdout.decode("utf-8", "ignore")
        if "__INITIAL_STATE__" in body:
            s = body[body.find("window.__INITIAL_STATE__"):]
            s = s[s.find("{"):]
            state = json.loads(s[:s.find("</script>")].rstrip().rstrip(";"))
            specs = {}
            spec_pairs(state, specs)
            return specs
        time.sleep(2 ** (attempt + 1))
    return {}


def main():
    urls = sys.argv[1:]
    if not urls:
        with open(os.path.join(HERE, "data", "shortlist.json")) as f:
            urls = [r["url"] for r in json.load(f) if r["store"] == "flipkart"]
    existing = {}
    if os.path.exists(OUT):
        with open(OUT) as f:
            existing = json.load(f)
    for url in urls:
        specs = fetch_specs(url)
        existing[url] = specs
        print(f"{len(specs):3d} specs  {url[:100]}", file=sys.stderr)
        time.sleep(1)
    with open(OUT, "w") as f:
        json.dump(existing, f, indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()

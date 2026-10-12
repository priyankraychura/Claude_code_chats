#!/usr/bin/env python3
"""Scrape every laptop listed on Flipkart inside a price band.

Flipkart server-renders search pages and embeds the full result set as JSON in
`window.__INITIAL_STATE__`, so no browser is needed: we fetch each results page
with curl (which already honours the session proxy + CA bundle) and read the
product records out of that JSON.

Usage: python3 scrape_flipkart.py [min_price] [max_price]
Writes data/flipkart.json
"""
import json
import os
import subprocess
import sys
import time
import urllib.parse

MIN_PRICE = int(sys.argv[1]) if len(sys.argv) > 1 else 80000
MAX_PRICE = int(sys.argv[2]) if len(sys.argv) > 2 else 96000
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "flipkart.json")

# The laptops category browse page (sid=6bo,b5g) plus a few searches that
# surface listings the category ranking buries (high-RAM / H-class CPUs).
# The default "relevance" order reshuffles between requests, so the category is
# also walked in both price orders (deterministic) to avoid missing listings.
SOURCES = [
    ("category", "https://www.flipkart.com/laptops/pr?sid=6bo%2Cb5g"),
    ("category:price_asc", "https://www.flipkart.com/laptops/pr?sid=6bo%2Cb5g&sort=price_asc"),
    ("category:price_desc", "https://www.flipkart.com/laptops/pr?sid=6bo%2Cb5g&sort=price_desc"),
    ("category:popularity", "https://www.flipkart.com/laptops/pr?sid=6bo%2Cb5g&sort=popularity"),
    ("search:32gb", "https://www.flipkart.com/search?q=laptop+32gb+ram"),
    ("search:gaming", "https://www.flipkart.com/search?q=gaming+laptop"),
    ("search:ryzen7", "https://www.flipkart.com/search?q=ryzen+7+laptop"),
    ("search:ultra7", "https://www.flipkart.com/search?q=intel+core+ultra+7+laptop"),
    ("search:macbook", "https://www.flipkart.com/search?q=macbook"),
]
MAX_PAGES = {"category": 40}
DEFAULT_MAX_PAGES = 12


def fetch(url):
    for attempt in range(4):
        r = subprocess.run(
            ["curl", "-sL", "--compressed", "-m", "45", "-A", UA,
             "-H", "Accept-Language: en-IN,en;q=0.9", url],
            capture_output=True)
        body = r.stdout.decode("utf-8", "ignore")
        if r.returncode == 0 and "__INITIAL_STATE__" in body:
            return body
        time.sleep(2 ** (attempt + 1))
    return None


def initial_state(html):
    s = html[html.find("window.__INITIAL_STATE__"):]
    s = s[s.find("{"):]
    return json.loads(s[:s.find("</script>")].rstrip().rstrip(";"))


def iter_products(state):
    """Yield productInfo.value dicts from every widget on the page."""
    slots = state.get("pageDataV4", {}).get("page", {}).get("data", {})
    for slot_list in slots.values():
        for slot in slot_list or []:
            data = (slot.get("widget") or {}).get("data") or {}
            for p in data.get("products") or []:
                v = ((p or {}).get("productInfo") or {}).get("value")
                if v and v.get("titles"):
                    yield v


def to_record(v, source):
    prices = (v.get("pricing") or {}).get("prices") or []
    price = next((p["value"] for p in prices if not p.get("strikeOff")), None)
    mrp = next((p["value"] for p in prices if p.get("strikeOff")), None)
    rating = v.get("rating") or {}
    return {
        "store": "flipkart",
        "id": v.get("id"),
        "title": v["titles"].get("title"),
        "subtitle": v["titles"].get("subtitle"),
        "key_specs": v.get("keySpecs") or [],
        "price": price,
        "mrp": mrp,
        "rating": rating.get("average"),
        "rating_count": rating.get("count"),
        "review_count": rating.get("reviewCount"),
        "in_stock": (v.get("availability") or {}).get("displayState") == "IN_STOCK",
        "warranty": v.get("warrantySummary"),
        "url": "https://www.flipkart.com" + (v.get("baseUrl") or ""),
        "source": source,
    }


def main():
    products = {}
    for name, base in SOURCES:
        max_pages = MAX_PAGES.get(name.split(":")[0], DEFAULT_MAX_PAGES)
        for page in range(1, max_pages + 1):
            qs = urllib.parse.urlencode([
                ("p[]", f"facets.price_range.from={MIN_PRICE}"),
                ("p[]", f"facets.price_range.to={MAX_PRICE}"),
                ("page", page),
            ])
            html = fetch(f"{base}&{qs}")
            if not html:
                print(f"[{name}] page {page}: fetch failed", file=sys.stderr)
                break
            found = [to_record(v, name) for v in iter_products(initial_state(html))]
            new = 0
            for rec in found:
                if rec["id"] and rec["id"] not in products:
                    products[rec["id"]] = rec
                    new += 1
            print(f"[{name}] page {page}: {len(found)} products, {new} new", file=sys.stderr)
            if not found:
                break
            time.sleep(1.0)

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    in_band = [p for p in products.values()
               if p["price"] and MIN_PRICE <= p["price"] <= MAX_PRICE]
    with open(OUT, "w") as f:
        json.dump(in_band, f, indent=1, ensure_ascii=False)
    print(f"saved {len(in_band)} in-budget laptops ({len(products)} seen) to {OUT}",
          file=sys.stderr)


if __name__ == "__main__":
    main()

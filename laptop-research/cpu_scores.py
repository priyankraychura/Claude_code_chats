#!/usr/bin/env python3
"""Download PassMark CPU Mark (multi-thread) scores for every CPU.

PassMark splits its list by vendor: /cpu-list/intel, /cpu-list/amd and
/cpu-list/other (Apple, Qualcomm, ...). Writes data/cpu_scores.json as
{"AMD Ryzen 7 8845HS": 28263, ...}.
"""
import html
import json
import os
import re
import subprocess

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/129.0 Safari/537.36")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "cpu_scores.json")
ROW = re.compile(r'<tr id="cpu\d+"><td><a href="[^"]*">([^<]*)</a></td><td>([0-9,]+)')


def main():
    scores = {}
    for vendor in ("intel", "amd", "other"):
        body = subprocess.run(
            ["curl", "-sL", "--compressed", "-m", "60", "-A", UA,
             f"https://www.cpubenchmark.net/cpu-list/{vendor}"],
            capture_output=True, check=True).stdout.decode("utf-8", "ignore")
        rows = ROW.findall(body)
        print(f"{vendor}: {len(rows)} CPUs")
        for name, score in rows:
            scores[html.unescape(name).strip()] = int(score.replace(",", ""))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(scores, f, indent=0, sort_keys=True)
    print(f"saved {len(scores)} CPU scores to {OUT}")


if __name__ == "__main__":
    main()

# Best dev laptop on Flipkart + Amazon, ₹80k–₹96k

Prices are a snapshot from **12 Oct 2026**. They change often, so re-check them before buying.

The workload: Android Studio with emulators, Flutter, .NET, Java, MERN, Cursor and Claude Code, with frontend, backend and emulator all running at once.

## Recommendation

| | Laptop | Price | Why |
|---|---|---|---|
| **Best pick** | **Lenovo V15 (2026), listed as "Lenovo 15"**: Core i7‑13620H (10C/16T), **24 GB DDR5‑5600** in 2 SO‑DIMM slots, 512 GB SSD, 15.6" FHD 300‑nit matte, 1.5 kg | **₹91,880** on [Amazon](https://www.amazon.in/dp/B0HJRPY8RY) | The only in‑budget laptop that pairs an H‑class 10‑core CPU with 24 GB of fast, dual‑channel RAM. Upgradeable to 32 GB. Ships from Amazon (FBA) with a 10‑day return. |
| Best value / safest | **Lenovo IdeaPad Slim 3 15IRH10**: Core i5‑13420H (8C/12T), **24 GB DDR5** (8 GB soldered + 16 GB SO‑DIMM), **1 TB SSD + a spare M.2 slot**, 15.3" WUXGA 16:10, 50 Wh | **₹86,990** on [Flipkart](https://www.flipkart.com/lenovo-ideapad-slim-3-backlit-keyboard-mso-2024-intel-core-i5-13th-gen-13420h-24-gb-1-tb-ssd-windows-11-home-15irh10-thin-light-laptop/p/itm0d5d0630f37d2?pid=COMHDYG7TFGZRMFZ) (₹95,500 on Amazon) | Same RAM as the V15, twice the SSD, bigger battery, and a proven listing (4.4★, 161 ratings). The trade‑off is a CPU that is ~28% slower on multi‑core, and RAM capped at 24 GB. |
| Fastest CPU | **ASUS ExpertBook P3 (P3406)**: Core Ultra 7 255H (16 cores), 16 GB DDR5, 2× SO‑DIMM (up to 64 GB), Thunderbolt 4, 14" WUXGA, 1.49 kg | **₹88,990** on [Flipkart](https://www.flipkart.com/asus-expertbook-p3-ai-pc-1-yr-adp-intel-core-ultra-7-255h-16-gb-512-gb-ssd-windows-11-home-p3406ccap-ly0161ws-thin-light-laptop/p/itm4e82eadf48819?pid=COMHHT9G9QC9CABY) | Builds run +33% faster than the i7 and +84% faster than the i5. But 16 GB is tight with an emulator running, and adding RAM now costs ~₹22.5k. Pick this only if you will upgrade later or test on a physical phone. |
| Stretch (+₹2k) | Lenovo V15 (2026) i7‑13620H with **32 GB** DDR5 | ₹97,989 on Amazon (per a price tracker; not checked on the listing itself) | Same machine as the best pick, without the RAM compromise. |

## Why RAM decides it

* **Memory is expensive right now.** One 16 GB DDR5‑5600 laptop stick (Crucial or Kingston) costs about **₹22,500** on Flipkart, versus about ₹14k for DDR4. "Buy 16 GB and upgrade" therefore pushes every 16 GB laptop well past ₹96k. RAM that ships in the box is what counts.
* **A typical session uses about 20 GB on Windows 11:**

  | Component | RAM |
  |---|---|
  | Windows | ~4 GB |
  | Android Studio + Gradle daemons | 3–6 GB |
  | Emulator | 2–4 GB |
  | Cursor | 1.5–3 GB |
  | Chrome | 2 GB |
  | Node/Java/.NET backend + dev server | 1–3 GB |
  | Docker / WSL2 (if used) | 2–6 GB |

  With 16 GB this swaps, 24 GB is workable, and 32 GB is comfortable.
* **No laptop in this band has both a top CPU and 24–32 GB.** Out of 412 in‑budget listings, every 32 GB option pairs it with a slow 15 W U‑series CPU (or DDR4). Every fast‑CPU option (Core Ultra 5/7 2xxH, Ryzen 7 260) ships with 16 GB.

## Avoid

* **"Lenovo IdeaPad Slim 3 14", 32 GB/1 TB" ([Amazon B0G4DHT2C4](https://www.amazon.in/dp/B0G4DHT2C4), ₹89,991).** The listing's own spec table says **16 GB/512 GB from the factory** (8 GB soldered + 8 GB SO‑DIMM, max 24 GB). A third‑party seller has modified or mislabelled it.
* **HP 14/15 Smartchoice "24 GB" (Core Ultra 5 125H).** HP's spec says **1 × 24 GB**, a single stick, so the memory runs single‑channel. The CPU is also slower.
* **32 GB laptops with U‑series CPUs:** HP Professional 14 (Core 5 120U / Core 7 150U), HP 240R G9 (i5‑1334U), Acer Professional 14, Acer TravelLite (Ryzen 7 7730U, DDR4). They have plenty of RAM, but the 15 W CPUs slow down Gradle and Flutter builds and the emulator.
* **Snapdragon X laptops** (HP OmniBook, Zenbook A14, IdeaPad Slim 3 Snapdragon). On Windows on ARM, the Android emulator, .NET Framework and some x86‑only native tooling still cause trouble.
* **Gaming laptops in this band** (RTX 2050/3050 with an i5‑12450H/13420H and 16 GB). The GPU doesn't help this workload, and they ship with weaker CPUs and less RAM than the picks above.
* **MacBooks.** The MacBook Air M5 starts at ₹1.4L, and the MacBook Neo at ₹89,900 has only 8 GB.

## Finalists

CPU scores are PassMark ratings (multi‑thread / single‑thread).

| Laptop | CPU (multi / single) | RAM | SSD | Price | Rating |
|---|---|---|---|---|---|
| Lenovo V15 (2026) | i7‑13620H (23,170 / 3,549) | 24 GB DDR5‑5600, 2 slots | 512 GB | ₹91,880 (Amazon) | new listing |
| IdeaPad Slim 3 15IRH10 | i5‑13420H (16,751 / 3,345) | 24 GB DDR5‑4800 (8 GB soldered) | 1 TB + spare M.2 | ₹86,990 (Flipkart) | 4.4★ (161) |
| Acer TravelLite TL05‑41M | Ryzen 7 7730U (16,875 / 2,909) | 32 GB DDR4 | 1 TB | ₹89,490 (Amazon) | new listing |
| ASUS ExpertBook P3 | Core Ultra 7 255H (30,786 / 4,311) | 16 GB DDR5, 2 slots | 512 GB | ₹88,990 (Flipkart) | 4.3★ (187) |
| ASUS Vivobook 16 (X1607CA) | Core Ultra 5 225H (28,017 / 4,248) | 16 GB DDR5 soldered + 1 free slot | 512 GB | ₹88,990 (Flipkart) | 4.3★ (179) |
| Motorola Motobook 60 | Core 7 240H (23,982 / 3,782) | 16 GB DDR5 | 1 TB | ₹92,899 (Flipkart) | 4.4★ (1,301); 2.8K OLED 120 Hz |

The full ranking of all 412 listings is in [`data/ranked.csv`](data/ranked.csv).

## How it was done

| Step | Script | What it does |
|---|---|---|
| 1 | `scrape_flipkart.py` | Walks Flipkart's laptop category (relevance, price‑ascending, price‑descending and popularity orders) plus targeted searches, filtered to ₹80–96k. It reads the product JSON embedded in each page. Output: `data/flipkart.json` (204 laptops). |
| 2 | `scrape_amazon.js` | Drives headless Chromium (Playwright) over 15 searches inside Amazon's Laptops category with a price filter. It uses a fresh browser session per page, because Amazon throttles long sessions. Output: `data/amazon.json` (220 laptops). |
| 3 | `cpu_scores.py`, `cpu_single_thread.py` | Download PassMark multi‑thread scores for about 6,000 CPUs, and single‑thread scores for every CPU in the listings. |
| 4 | `analyze.py` | Parses CPU, RAM, RAM type, SSD, GPU and screen from each title, matches the CPU to its benchmark, and scores the laptop. Facts verified on product pages (`data/overrides.json`) override the titles. |
| 5 | `details_flipkart.py`, `details_amazon.js` | Pull the full spec sheets of the shortlisted laptops: memory layout, slots, seller, battery and display. |

The score is out of 100 and uses these weights:

| Factor | Weight | Details |
|---|---|---|
| CPU | 30% | 65% multi‑thread, 35% single‑thread; ×0.85 for 15 W U‑series and ARM chips |
| RAM | 35% | 32 GB = 1.0, 24 GB = 0.8, 16 GB upgradeable = 0.35, 16 GB soldered = 0.15; DDR4 −0.05; single‑channel −0.1 |
| SSD | 10% | |
| Platform | 12% | x86 = 1.0, macOS = 0.75, Windows on ARM = 0.25 |
| Display | 5% | |
| Rating | 8% | Bayesian‑shrunk, so a few 5★ reviews don't outrank hundreds of 4.4★ ones |

The scores are a filter. The final picks above are a judgement call made from the verified details.

### Re-run

```bash
python3 scrape_flipkart.py 80000 96000
NODE_PATH=$(npm root -g) node scrape_amazon.js 80000 96000
python3 cpu_scores.py
python3 analyze.py && python3 cpu_single_thread.py && python3 analyze.py
python3 details_flipkart.py && NODE_PATH=$(npm root -g) node details_amazon.js
```

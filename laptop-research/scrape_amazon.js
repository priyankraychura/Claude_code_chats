#!/usr/bin/env node
// Scrape laptops listed on Amazon.in inside a price band.
//
// Amazon answers plain HTTP clients with a bot-check interstitial, so this
// drives headless Chromium (Playwright) through the session proxy. Each query
// is restricted to the Laptops browse node (n:1375424031) and the price band
// (p_36, in paise), then paged until Amazon stops returning results.
//
// Usage: node scrape_amazon.js [min_price] [max_price] [query ...]
// Writes data/amazon.json (merged with any previous run)
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const MIN_PRICE = Number(process.argv[2] || 80000);
const MAX_PRICE = Number(process.argv[3] || 96000);
const OUT = path.join(__dirname, 'data', 'amazon.json');
const MAX_PAGES = 20;
const RUN = new Date().toISOString();
const QUERIES = [
  'laptop',
  'laptop 32gb ram',
  'gaming laptop',
  'laptop ryzen 7',
  'laptop ryzen ai',
  'laptop intel core ultra 7',
  'laptop intel core i7',
  'laptop 1tb ssd',
  'macbook',
];

function searchUrl(q, page) {
  const rh = `n:1375424031,p_36:${MIN_PRICE * 100}-${MAX_PRICE * 100}`;
  return `https://www.amazon.in/s?k=${encodeURIComponent(q)}&rh=${encodeURIComponent(rh)}&page=${page}`;
}

async function extract(page) {
  return page.$$eval('div[data-component-type="s-search-result"]', (els) =>
    els.map((e) => {
      const text = (sel) => (e.querySelector(sel)?.textContent || '').trim();
      const num = (s) => (s ? Number(s.replace(/[^0-9.]/g, '')) || null : null);
      const asin = e.getAttribute('data-asin');
      // Some cards render the brand in its own <h2> ahead of the product
      // title, so take the longest heading text on the card.
      const title = [...e.querySelectorAll('h2')]
        .flatMap((h) => [h.getAttribute('aria-label') || '', h.textContent || ''])
        .map((s) => s.trim().replace(/^Sponsored Ad - /, ''))
        .reduce((a, b) => (b.length > a.length ? b : a), '');
      const ratingTxt = text('span.a-icon-alt'); // "4.2 out of 5 stars"
      const countEl = e.querySelector('a[href*="#customerReviews"] span, span[aria-label$="ratings"]');
      return {
        store: 'amazon',
        id: asin,
        title,
        price: num(text('.a-price:not(.a-text-price) .a-offscreen')),
        mrp: num(text('.a-price.a-text-price .a-offscreen')),
        rating: ratingTxt ? Number(ratingTxt.split(' ')[0]) : null,
        rating_count: num(countEl?.getAttribute('aria-label') || countEl?.textContent || ''),
        sponsored: !!e.querySelector('.puis-sponsored-label-text, .s-sponsored-label-text'),
        url: asin ? `https://www.amazon.in/dp/${asin}` : null,
      };
    })
  );
}

// Amazon flags a session after a few result pages, so each page is loaded in
// a fresh browser context (new cookies) — the same as a first-time visitor.
async function fetchPage(browser, q, p) {
  const ctx = await browser.newContext({
    locale: 'en-IN',
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    viewport: { width: 1366, height: 900 },
  });
  const page = await ctx.newPage();
  try {
    await page.goto(searchUrl(q, p), { waitUntil: 'domcontentloaded', timeout: 60000 });
    try {
      await page.waitForSelector('div[data-component-type="s-search-result"]', { timeout: 25000 });
    } catch (err) {
      // Past the last page Amazon shows "No results"; anything else is a
      // bot-check interstitial or captcha.
      const exhausted = !!(await page.$('text=/No results for/i').catch(() => null));
      return { found: [], hasNext: false, blocked: !exhausted };
    }
    const found = await extract(page);
    const hasNext = !!(await page.$('a.s-pagination-next:not(.s-pagination-disabled)'));
    return { found, hasNext, blocked: false };
  } catch (err) {
    return { found: [], hasNext: false, blocked: true };
  } finally {
    await ctx.close().catch(() => {});
  }
}

function save(products) {
  const inBand = [...products.values()].filter((r) => r.price && r.price >= MIN_PRICE && r.price <= MAX_PRICE);
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(inBand, null, 1));
  return inBand.length;
}

(async () => {
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  // Merge with a previous run so a re-run only has to fill gaps left by
  // pages Amazon temporarily blocked.
  const products = new Map(
    fs.existsSync(OUT) ? JSON.parse(fs.readFileSync(OUT)).map((r) => [r.id, r]) : []
  );
  const queries = process.argv.slice(4).length ? process.argv.slice(4) : QUERIES;

  for (const q of queries) {
    for (let p = 1; p <= MAX_PAGES; p++) {
      let res = { found: [], hasNext: false, blocked: true };
      for (let attempt = 0; attempt < 4 && res.blocked; attempt++) {
        if (attempt) {
          console.error(`[${q}] page ${p}: blocked (attempt ${attempt}), backing off`);
          await new Promise((r) => setTimeout(r, 10000 * attempt));
        }
        res = await fetchPage(browser, q, p);
      }
      let added = 0;
      for (const rec of res.found) {
        if (!rec.id || !rec.title) continue;
        rec.source = q;
        if (!products.has(rec.id) || products.get(rec.id).scraped_at !== RUN) added++;
        rec.scraped_at = RUN;
        products.set(rec.id, rec); // latest price/title wins over a previous run
      }
      console.error(`[${q}] page ${p}: ${res.found.length} results, ${added} new${res.blocked ? ' (gave up: blocked)' : ''}`);
      if (!res.found.length || !res.hasNext) break;
      await new Promise((r) => setTimeout(r, 1500));
    }
    save(products);
  }
  await browser.close();
  const n = save(products);
  console.error(`saved ${n} in-budget laptops (${products.size} seen) to ${OUT}`);
})();

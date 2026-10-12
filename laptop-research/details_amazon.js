#!/usr/bin/env node
// Fetch the full spec sheet for shortlisted Amazon.in listings.
//
// Usage: node details_amazon.js URL [URL ...]   (or reads data/shortlist.json)
// Writes data/details_amazon.json  {url: {spec name: value, _bullets: [...]}}
const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const OUT = path.join(__dirname, 'data', 'details_amazon.json');

(async () => {
  let urls = process.argv.slice(2);
  if (!urls.length) {
    urls = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'shortlist.json')))
      .filter((r) => r.store === 'amazon').map((r) => r.url);
  }
  const existing = fs.existsSync(OUT) ? JSON.parse(fs.readFileSync(OUT)) : {};
  const browser = await chromium.launch({ proxy: { server: process.env.HTTPS_PROXY } });
  for (const url of urls) {
    let specs = {};
    for (let attempt = 0; attempt < 3 && !Object.keys(specs).length; attempt++) {
      // Fresh context (cookies) per attempt: Amazon throttles long sessions.
      const ctx = await browser.newContext({
        locale: 'en-IN',
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
      });
      const page = await ctx.newPage();
      try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
        await page.waitForSelector('#productTitle', { timeout: 25000 });
        specs = await page.evaluate(() => {
          const out = {};
          const rows = document.querySelectorAll(
            '#productDetails_techSpec_section_1 tr, #productDetails_detailBullets_sections1 tr, .prodDetTable tr, #productOverview_feature_div tr');
          for (const tr of rows) {
            const k = tr.querySelector('th, td:first-child')?.innerText.trim();
            const v = tr.querySelector('td:last-child')?.innerText.trim().replace(/^‎/, '');
            if (k && v && k !== v && !(k in out)) out[k] = v;
          }
          out._title = document.querySelector('#productTitle')?.innerText.trim();
          out._price = document.querySelector('#corePriceDisplay_desktop_feature_div .a-price:not(.a-text-price) .a-offscreen, #corePrice_feature_div .a-offscreen')?.textContent.trim();
          out._bullets = [...document.querySelectorAll('#feature-bullets li, #featurebullets_feature_div li')]
            .map((li) => li.innerText.trim()).filter(Boolean);
          out._availability = document.querySelector('#availability')?.innerText.trim();
          out._seller = document.querySelector('#merchantInfoFeature_feature_div .offer-display-feature-text, #sellerProfileTriggerId')?.innerText.trim();
          out._rating = document.querySelector('#acrPopover')?.getAttribute('title');
          out._rating_count = document.querySelector('#acrCustomerReviewText')?.innerText.trim();
          return out;
        });
      } catch (err) {
        await new Promise((r) => setTimeout(r, 8000 * (attempt + 1)));
      } finally {
        await ctx.close().catch(() => {});
      }
    }
    existing[url] = specs;
    console.error(`${String(Object.keys(specs).length).padStart(3)} specs  ${url}`);
    await new Promise((r) => setTimeout(r, 1500));
  }
  await browser.close();
  fs.writeFileSync(OUT, JSON.stringify(existing, null, 1));
})();

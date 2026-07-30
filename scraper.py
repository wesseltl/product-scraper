#!/usr/bin/env python3
"""Product-catalog scraper — collects every product's title, price, rating and stock into a clean CSV.

Demo target: books.toscrape.com — a public website built specifically for scraping practice, so this
runs cleanly and legally out of the box. To adapt it to a real client's catalog you change one URL and
the four field patterns in `parse_products()`; everything else (paging, retries, politeness, CSV output)
stays the same.

Good-citizen behaviour by default: it identifies itself with a User-Agent, retries failed requests with
backoff, and pauses between pages so it never hammers a server.

Usage:
    python3 scraper.py                 # scrape all pages -> products.csv
    python3 scraper.py --max-pages 5   # just the first 5 pages (quick test)

Dependencies: only `requests`.  (HTML parsing uses the Python standard library.)
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import time

import requests

BASE_URL = "https://books.toscrape.com/catalogue/page-{}.html"
HEADERS = {"User-Agent": "portfolio-scraper/1.0 (+https://example.com/contact)"}
RATING_WORDS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
FIELDS = ["title", "price_gbp", "rating", "availability"]


def fetch(url: str, retries: int = 3) -> str | None:
    """Return page HTML, or None if the page doesn't exist (404 = we've run past the last page).
    Retries transient network/server errors with increasing backoff before giving up."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=20)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
            return resp.text
        except requests.RequestException:
            if attempt == retries - 1:
                raise
            time.sleep(2 * (attempt + 1))
    return None


def parse_products(html: str) -> list[dict]:
    """Extract one record per product from a catalog page. Each product lives in a block marked
    `product_pod`; within it we pull the four fields we care about. Adapt these four patterns to a
    client's markup and the rest of the pipeline is unchanged."""
    rows: list[dict] = []
    for block in html.split('class="product_pod"')[1:]:      # one chunk per product on the page
        title = re.search(r'title="([^"]+)"', block)
        price = re.search(r'price_color">[^\d]*([\d.]+)', block)   # tolerate any currency symbol/encoding
        rating = re.search(r'star-rating (\w+)', block)
        if not (title and price):
            continue
        rows.append({
            "title": title.group(1).strip(),
            "price_gbp": float(price.group(1)),
            "rating": RATING_WORDS.get(rating.group(1), "") if rating else "",
            "availability": "In stock" if "In stock" in block else "Out of stock",
        })
    return rows


def scrape(max_pages: int = 100, delay: float = 0.4) -> list[dict]:
    """Walk the catalog page by page until a page 404s or returns no products."""
    all_rows: list[dict] = []
    for page in range(1, max_pages + 1):
        html = fetch(BASE_URL.format(page))
        if html is None:
            break
        rows = parse_products(html)
        if not rows:
            break
        all_rows.extend(rows)
        print(f"page {page:>3}: +{len(rows):>2} products  (running total {len(all_rows)})")
        time.sleep(delay)                                     # be polite between requests
    return all_rows


def save_csv(rows: list[dict], path: str = "products.csv") -> str:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description="Scrape a product catalog into a clean CSV.")
    ap.add_argument("--max-pages", type=int, default=100, help="stop after this many pages")
    ap.add_argument("--out", default="products.csv", help="output CSV path")
    args = ap.parse_args()

    rows = scrape(max_pages=args.max_pages)
    if not rows:
        print("No products found — check the site is reachable and the patterns still match.")
        sys.exit(1)
    path = save_csv(rows, args.out)
    prices = [r["price_gbp"] for r in rows]
    print(f"\nDone: {len(rows)} products written to {path}")
    print(f"Price range £{min(prices):.2f}–£{max(prices):.2f}  ·  average £{sum(prices)/len(prices):.2f}")


if __name__ == "__main__":
    main()

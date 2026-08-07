# Product-Catalog Scraper

A small, dependency-light Python tool that scrapes a product catalog and delivers a clean, ready-to-use
**CSV**: one row per product with **title, price, rating, and stock status**.

Built as a demonstration on [books.toscrape.com](https://books.toscrape.com) (a public site made for
scraping practice), it collects the full **1,000-product** catalog across all 50 pages in a few seconds.

## What you get

```
title,price_gbp,rating,availability
A Light in the Attic,51.77,3,In stock
Tipping the Velvet,53.74,1,In stock
Soumission,50.1,1,In stock
...
```

Open it in Excel, Google Sheets, or load it into any database, no cleanup needed.

## Run it

```bash
pip install requests
python3 scraper.py                 # full catalog -> products.csv
python3 scraper.py --max-pages 5   # quick test (first 5 pages)
```

Only dependency is `requests`; HTML parsing uses the Python standard library, so it runs anywhere.

## How it's built to be reliable

- **Paging**: walks every catalog page automatically and stops on its own at the end.
- **Retries**: transient network/server errors are retried with backoff instead of crashing a long run.
- **Polite**: sends a proper User-Agent and pauses between pages so it never overloads the site.
- **Tolerant extraction**: handles currency symbols and minor markup quirks.

## Adapting it to another site

Change one line (`BASE_URL`) and the four field patterns inside `parse_products()` to match the target
site's markup. Everything else, paging, retries, politeness, CSV output, stays the same. Typical
add-ons clients ask for: extra fields (SKU, image URL, category), Excel/Google-Sheets output, scheduled
daily runs, or de-duplication against a previous run. All straightforward extensions of this base.

## A note on responsible scraping

This demo targets a site that explicitly permits scraping. For any real target I check the site's terms
and `robots.txt`, scrape only public data, and keep request rates gentle.

---

*Built by **Wessel ter Laak**: Python automation & data extraction. Need a scraper or data pipeline for
your own site or data source? I adapt this kind of tool to order.*

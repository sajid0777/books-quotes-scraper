"""Books to Scrape parser with next-link pagination."""
import logging
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

from .base_scraper import BaseScraper

START_URL = "https://books.toscrape.com/"
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


class BooksScraper(BaseScraper):
    def scrape(self):
        records, url, page = [], START_URL, 1
        while url:
            self.logger.info("Books page %d: %s", page, url)
            try:
                soup = BeautifulSoup(self.get(url).text, "lxml")
            except requests.RequestException as exc:
                self.logger.error("Books request failed at %s: %s", url, exc)
                break
            for article in soup.select("article.product_pod"):
                try:
                    link = article.select_one("h3 > a")
                    price = article.select_one("p.price_color")
                    rating = article.select_one("p.star-rating")
                    if not link:
                        raise ValueError("missing title link")
                    title = link.get("title") or link.get_text(" ", strip=True)
                    records.append({
                        "source": "Books to Scrape", "source_url": urljoin(url, link.get("href", "")),
                        "name_or_title": title, "category": None,
                        "price": price.get_text(" ", strip=True) if price else None,
                        "rating": next((RATING_MAP[c] for c in (rating.get("class", []) if rating else []) if c in RATING_MAP), None),
                        "author": None, "tags": None, "description": None,
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    })
                except Exception as exc:
                    logging.getLogger(__name__).warning("Skipping malformed book: %s", exc)
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page += 1
        return records


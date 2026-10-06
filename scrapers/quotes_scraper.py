"""Quotes to Scrape parser with next-link pagination."""
import logging
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests

from .base_scraper import BaseScraper

START_URL = "https://quotes.toscrape.com/"


class QuotesScraper(BaseScraper):
    def scrape(self):
        records, url, page = [], START_URL, 1
        while url:
            self.logger.info("Quotes page %d: %s", page, url)
            try:
                soup = BeautifulSoup(self.get(url).text, "lxml")
            except requests.RequestException as exc:
                self.logger.error("Quotes request failed at %s: %s", url, exc)
                break
            for quote in soup.select("div.quote"):
                try:
                    text = quote.select_one("span.text")
                    author = quote.select_one("small.author")
                    if not text or not author:
                        raise ValueError("missing quote text or author")
                    author_link = quote.select_one('a[href^="/author/"]')
                    tags = [tag.get_text(" ", strip=True) for tag in quote.select("a.tag")]
                    records.append({
                        "source": "Quotes to Scrape",
                        "source_url": urljoin(url, author_link["href"]) if author_link and author_link.get("href") else url,
                        "name_or_title": text.get_text(" ", strip=True), "category": None,
                        "price": None, "rating": None, "author": author.get_text(" ", strip=True),
                        "tags": tags, "description": None,
                        "scraped_at": datetime.now(timezone.utc).isoformat(),
                    })
                except Exception as exc:
                    logging.getLogger(__name__).warning("Skipping malformed quote: %s", exc)
            next_link = soup.select_one("li.next > a")
            url = urljoin(url, next_link["href"]) if next_link and next_link.get("href") else None
            page += 1
        return records


import logging
from typing import List, Dict, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
import config

logger = logging.getLogger("ScraperPipeline")


class BooksScraper(BaseScraper):
    def __init__(self):
        super().__init__(name="Books to Scrape", base_url=config.BOOKS_BASE_URL)

    def scrape(self) -> List[Dict[str, Any]]:
        records = []
        current_url = urljoin(self.base_url, "catalogue/page-1.html")
        page_count = 0

        logger.info(f"[{self.name}] Starting scraping pipeline...")

        while current_url:
            page_count += 1
            logger.info(f"[{self.name}] Scraping page {page_count}: {current_url}")
            html = self.fetch_page(current_url)
            if not html:
                logger.warning(f"[{self.name}] Skipping unreachable page: {current_url}")
                break

            soup = BeautifulSoup(html, "lxml")
            articles = soup.find_all("article", class_="product_pod")

            for article in articles:
                try:
                    record = self._parse_book(article, current_url)
                    if record:
                        records.append(record)
                except Exception as e:
                    logger.error(f"[{self.name}] Error parsing book card on page {page_count}: {e}")

            # Pagination check
            next_btn = soup.find("li", class_="next")
            if next_btn and next_btn.find("a"):
                next_rel_path = next_btn.find("a")["href"]
                # Resolve relative URL against current page URL structure
                if "catalogue/" in current_url and not next_rel_path.startswith("catalogue/"):
                    current_url = urljoin(current_url, next_rel_path)
                else:
                    current_url = urljoin(self.base_url, f"catalogue/{next_rel_path}")
            else:
                current_url = None

        logger.info(f"[{self.name}] Scraping completed. Total records harvested: {len(records)}")
        return records

    def _parse_book(self, article: BeautifulSoup, page_url: str) -> Dict[str, Any]:
        # Title & Product Link
        title_tag = article.h3.find("a") if article.h3 else None
        title = title_tag.get("title") or title_tag.text if title_tag else None
        rel_link = title_tag.get("href") if title_tag else ""
        source_url = urljoin(page_url, rel_link) if rel_link else page_url

        # Price
        price_tag = article.find("p", class_="price_color")
        raw_price = price_tag.text if price_tag else None

        # Rating
        rating_tag = article.find("p", class_="star-rating")
        rating_val = None
        if rating_tag:
            classes = rating_tag.get("class", [])
            for c in classes:
                if c.lower() in config.RATING_MAP:
                    rating_val = config.RATING_MAP[c.lower()]
                    break

        # Availability / Stock
        avail_tag = article.find("p", class_="instock availability")
        availability = avail_tag.text.strip() if avail_tag else None

        return {
            "source": self.name,
            "source_url": source_url,
            "name_or_title": title,
            "category": "Books",
            "price": raw_price,
            "rating": rating_val,
            "author": None,
            "tags": None,
            "description": f"Availability: {availability}" if availability else None
        }
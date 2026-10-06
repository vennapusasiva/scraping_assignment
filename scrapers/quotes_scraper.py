import logging
from typing import List, Dict, Any
from urllib.parse import urljoin
from bs4 import BeautifulSoup

from scrapers.base_scraper import BaseScraper
import config

logger = logging.getLogger("ScraperPipeline")


class QuotesScraper(BaseScraper):
    def __init__(self):
        super().__init__(name="Quotes to Scrape", base_url=config.QUOTES_BASE_URL)

    def scrape(self) -> List[Dict[str, Any]]:
        records = []
        current_url = self.base_url
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
            quote_divs = soup.find_all("div", class_="quote")

            for q_div in quote_divs:
                try:
                    record = self._parse_quote(q_div, current_url)
                    if record:
                        records.append(record)
                except Exception as e:
                    logger.error(f"[{self.name}] Error parsing quote card on page {page_count}: {e}")

            # Pagination check
            next_btn = soup.find("li", class_="next")
            if next_btn and next_btn.find("a"):
                next_rel_path = next_btn.find("a")["href"]
                current_url = urljoin(self.base_url, next_rel_path)
            else:
                current_url = None

        logger.info(f"[{self.name}] Scraping completed. Total records harvested: {len(records)}")
        return records

    def _parse_quote(self, quote_div: BeautifulSoup, page_url: str) -> Dict[str, Any]:
        # Text/Quote
        text_tag = quote_div.find("span", class_="text")
        raw_text = text_tag.text if text_tag else None

        # Author
        author_tag = quote_div.find("small", class_="author")
        author = author_tag.text if author_tag else None

        # Tags
        tag_elements = quote_div.find_all("a", class_="tag")
        tags_list = [t.text.strip() for t in tag_elements if t.text]
        tags_str = ", ".join(tags_list) if tags_list else None

        # Author profile link
        author_link = quote_div.find("a", href=True)
        source_url = urljoin(page_url, author_link["href"]) if author_link and "author" in author_link["href"] else page_url

        return {
            "source": self.name,
            "source_url": source_url,
            "name_or_title": raw_text,
            "category": "Quotes",
            "price": None,
            "rating": None,
            "author": author,
            "tags": tags_str,
            "description": None
        }
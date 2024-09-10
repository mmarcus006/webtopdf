from playwright.sync_api import sync_playwright
from urllib.parse import urljoin, urlparse
from typing import List, Set
import logging
import time

class Crawler:
    def __init__(self, base_url: str, rate_limit: float = 1.0):
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.visited: Set[str] = set()
        self.to_visit: Set[str] = set([base_url])
        self.domain = urlparse(base_url).netloc

    def crawl(self) -> List[str]:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            while self.to_visit:
                url = self.to_visit.pop()
                try:
                    time.sleep(self.rate_limit)
                    page.goto(url, wait_until="networkidle")
                    self.visited.add(url)
                    logging.info("Crawled: %s", url)
                    
                    # Extract links from the rendered page
                    links = page.eval_on_selector_all("a[href]", "elements => elements.map(el => el.href)")
                    for link in links:
                        full_url = urljoin(url, link)
                        if self.domain in full_url and full_url not in self.visited:
                            self.to_visit.add(full_url)
                except Exception as e:
                    logging.error(f"Error crawling {url}: {e}")

            browser.close()
        
        return list(self.visited)
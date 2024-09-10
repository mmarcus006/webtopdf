from playwright.sync_api import sync_playwright
from typing import Optional
import logging

class PDFGenerator:
    def __init__(self, options: Optional[dict] = None):
        self.options = options or {}

    def generate_pdf(self, url: str, output_path: str) -> bool:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.goto(url, wait_until="networkidle")
                page.pdf(path=output_path, **self.options)
                browser.close()
            logging.info(f"Generated PDF for {url} at {output_path}")
            return True
        except Exception as e:
            logging.error(f"Error generating PDF for {url}: {e}")
            return False
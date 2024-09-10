import asyncio
import logging
from typing import List, Optional, Dict
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, Page
from aiolimiter import AsyncLimiter

class NetworkError(Exception):
    """Exception raised for network-related errors."""
    pass

class RenderingError(Exception):
    """Exception raised for page rendering errors."""
    pass

class PDFConversionError(Exception):
    """Exception raised for PDF conversion errors."""
    pass

class WebToPDFConverter:
    def __init__(self, concurrency_limit: int = 5, rate_limit: float = 1.0):
        """
        Initialize the WebToPDFConverter.

        :param concurrency_limit: Maximum number of concurrent tasks
        :param rate_limit: Maximum number of requests per second
        """
        self.semaphore = asyncio.Semaphore(concurrency_limit)
        self.rate_limiter = AsyncLimiter(rate_limit)
        self.browser = None

    async def __aenter__(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.browser.close()

    async def crawl_and_convert(self, base_url: str, output_dir: str, css_selector: Optional[str] = None) -> List[str]:
        """
        Crawl the website and convert pages to PDF.

        :param base_url: The starting URL for crawling
        :param output_dir: Directory to save PDF files
        :param css_selector: CSS selector for selective rendering
        :return: List of processed URLs
        """
        domain = urlparse(base_url).netloc
        to_visit = set([base_url])
        visited = set()

        while to_visit:
            url = to_visit.pop()
            if url in visited:
                continue

            try:
                async with self.semaphore:
                    async with self.rate_limiter:
                        page = await self.browser.new_page()
                        await self._process_page(page, url, domain, to_visit, visited, output_dir, css_selector)
                        await page.close()
            except Exception as e:
                logging.error(f"Error processing {url}: {str(e)}")

        return list(visited)

    async def _process_page(self, page: Page, url: str, domain: str, to_visit: set, visited: set, output_dir: str, css_selector: Optional[str]):
        """
        Process a single page: load, extract links, and convert to PDF.

        :param page: Playwright Page object
        :param url: URL to process
        :param domain: Domain of the website being crawled
        :param to_visit: Set of URLs to visit
        :param visited: Set of visited URLs
        :param output_dir: Directory to save PDF files
        :param css_selector: CSS selector for selective rendering
        """
        try:
            await page.goto(url, wait_until="networkidle")
        except Exception as e:
            raise NetworkError(f"Failed to load {url}: {str(e)}")

        visited.add(url)
        logging.info(f"Crawled: {url}")

        try:
            links = await page.eval_on_selector_all("a[href]", "elements => elements.map(el => el.href)")
            for link in links:
                full_url = urljoin(url, link)
                if domain in full_url and full_url not in visited:
                    to_visit.add(full_url)
        except Exception as e:
            logging.warning(f"Error extracting links from {url}: {str(e)}")

        try:
            await self._generate_pdf(page, url, output_dir, css_selector)
        except PDFConversionError as e:
            logging.error(f"PDF conversion failed for {url}: {str(e)}")

    async def _generate_pdf(self, page: Page, url: str, output_dir: str, css_selector: Optional[str]):
        """
        Generate a PDF from the given page.

        :param page: Playwright Page object
        :param url: URL of the page
        :param output_dir: Directory to save the PDF
        :param css_selector: CSS selector for selective rendering
        """
        try:
            if css_selector:
                await page.wait_for_selector(css_selector, state="attached")
                element_handle = await page.query_selector(css_selector)
                if not element_handle:
                    raise RenderingError(f"Element not found: {css_selector}")
                await element_handle.screenshot(path=f"{output_dir}/{urlparse(url).path.strip('/').replace('/', '_') or 'index'}.pdf", type="pdf")
            else:
                await page.pdf(path=f"{output_dir}/{urlparse(url).path.strip('/').replace('/', '_') or 'index'}.pdf")
            logging.info(f"Generated PDF for {url}")
        except Exception as e:
            raise PDFConversionError(f"Failed to generate PDF for {url}: {str(e)}")

async def main(url: str, output_dir: str, concurrency_limit: int = 5, rate_limit: float = 1.0, css_selector: Optional[str] = None):
    """
    Main function to run the web-to-PDF converter.

    :param url: The starting URL for crawling
    :param output_dir: Directory to save PDF files
    :param concurrency_limit: Maximum number of concurrent tasks
    :param rate_limit: Maximum number of requests per second
    :param css_selector: CSS selector for selective rendering
    """
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    async with WebToPDFConverter(concurrency_limit, rate_limit) as converter:
        processed_urls = await converter.crawl_and_convert(url, output_dir, css_selector)
        logging.info(f"Processed {len(processed_urls)} URLs")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Convert web pages to PDF")
    parser.add_argument("url", help="The base URL to crawl and convert")
    parser.add_argument("--output", "-o", default="output", help="Output directory for PDFs")
    parser.add_argument("--concurrency", "-c", type=int, default=5, help="Maximum number of concurrent tasks")
    parser.add_argument("--rate", "-r", type=float, default=1.0, help="Maximum number of requests per second")
    parser.add_argument("--selector", "-s", help="CSS selector for selective rendering")
    args = parser.parse_args()

    asyncio.run(main(args.url, args.output, args.concurrency, args.rate, args.selector))
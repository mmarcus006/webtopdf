import pytest
from unittest.mock import MagicMock, patch
from src.crawler import Crawler

@pytest.fixture
def mock_playwright():
    with patch('src.crawler.sync_playwright') as mock_playwright:
        mock_browser = MagicMock()
        mock_page = MagicMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright.return_value.__enter__.return_value.chromium.launch.return_value = mock_browser
        yield mock_page

def test_crawler_initialization():
    crawler = Crawler('https://example.com')
    assert crawler.base_url == 'https://example.com'
    assert crawler.domain == 'example.com'

def test_crawler_crawl(mock_playwright):
    mock_playwright.eval_on_selector_all.return_value = [
        'https://example.com/page1',
        'https://example.com/page2',
        'https://external.com'
    ]

    crawler = Crawler('https://example.com')
    result = crawler.crawl()

    assert set(result) == {'https://example.com', 'https://example.com/page1', 'https://example.com/page2'}
    assert mock_playwright.goto.call_count == 3
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from src.web_to_pdf_converter import WebToPDFConverter, NetworkError, RenderingError, PDFConversionError

@pytest.fixture
def mock_page():
    page = AsyncMock()
    page.goto = AsyncMock()
    page.eval_on_selector_all = AsyncMock(return_value=['https://example.com/page1', 'https://example.com/page2'])
    page.pdf = AsyncMock()
    page.query_selector = AsyncMock()
    return page

@pytest.fixture
def mock_browser(mock_page):
    browser = AsyncMock()
    browser.new_page = AsyncMock(return_value=mock_page)
    return browser

@pytest.fixture
async def converter(mock_browser):
    async with patch('src.web_to_pdf_converter.async_playwright') as mock_playwright:
        mock_playwright.return_value.start = AsyncMock()
        mock_playwright.return_value.chromium.launch = AsyncMock(return_value=mock_browser)
        converter = WebToPDFConverter()
        await converter.__aenter__()
        yield converter
        await converter.__aexit__(None, None, None)

@pytest.mark.asyncio
async def test_crawl_and_convert(converter, mock_page):
    result = await converter.crawl_and_convert('https://example.com', 'output')
    assert set(result) == {'https://example.com', 'https://example.com/page1', 'https://example.com/page2'}
    assert mock_page.goto.call_count == 3
    assert mock_page.pdf.call_count == 3

@pytest.mark.asyncio
async def test_crawl_and_convert_with_selector(converter, mock_page):
    mock_element = AsyncMock()
    mock_page.query_selector.return_value = mock_element
    mock_element.screenshot = AsyncMock()

    await converter.crawl_and_convert('https://example.com', 'output', css_selector='#content')
    
    assert mock_page.wait_for_selector.call_count == 3
    assert mock_element.screenshot.call_count == 3

@pytest.mark.asyncio
async def test_network_error(converter, mock_page):
    mock_page.goto.side_effect = Exception("Network error")
    
    with pytest.raises(NetworkError):
        await converter._process_page(mock_page, 'https://example.com', 'example.com', set(), set(), 'output', None)

@pytest.mark.asyncio
async def test_rendering_error(converter, mock_page):
    mock_page.query_selector.return_value = None
    
    with pytest.raises(RenderingError):
        await converter._generate_pdf(mock_page, 'https://example.com', 'output', '#non-existent')

@pytest.mark.asyncio
async def test_pdf_conversion_error(converter, mock_page):
    mock_page.pdf.side_effect = Exception("PDF conversion failed")
    
    with pytest.raises(PDFConversionError):
        await converter._generate_pdf(mock_page, 'https://example.com', 'output', None)
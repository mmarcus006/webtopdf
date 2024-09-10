import pytest
from unittest.mock import patch
from src.pdf_generator import PDFGenerator

@pytest.fixture
def pdf_generator():
    return PDFGenerator()

def test_pdf_generator_initialization():
    generator = PDFGenerator({'option1': 'value1'})
    assert generator.options == {'option1': 'value1'}

@patch('src.pdf_generator.pdfkit.from_url')
def test_generate_pdf_success(mock_from_url, pdf_generator):
    result = pdf_generator.generate_pdf('https://example.com', 'output.pdf')
    assert result is True
    mock_from_url.assert_called_once_with('https://example.com', 'output.pdf', options={})

@patch('src.pdf_generator.pdfkit.from_url')
def test_generate_pdf_failure(mock_from_url, pdf_generator):
    mock_from_url.side_effect = Exception("PDF generation failed")
    result = pdf_generator.generate_pdf('https://example.com', 'output.pdf')
    assert result is False
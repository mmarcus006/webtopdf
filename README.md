# Web Page to PDF Converter

This Python project crawls a website and converts each page to a PDF file.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/web_to_pdf.git
   cd web_to_pdf
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Install wkhtmltopdf (required by pdfkit):
   - On Ubuntu: `sudo apt-get install wkhtmltopdf`
   - On macOS: `brew install wkhtmltopdf`
   - On Windows: Download and install from https://wkhtmltopdf.org/downloads.html

## Usage

Run the script with a URL as an argument:

```
python src/main.py https://example.com
```

This will crawl the website and save PDFs in the `output` directory.

To specify a custom output directory:

```
python src/main.py https://example.com --output custom_directory
```

## Running Tests

To run the tests, use pytest:

```
pytest
```

## License

This project is licensed under the MIT License.
import asyncio
import argparse
import logging
from pathlib import Path
from web_to_pdf_converter import main as converter_main
import sys
from gui import main as gui_main

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def cli_main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Convert web pages to PDF")
    parser.add_argument("url", help="The base URL to crawl and convert")
    parser.add_argument("--output", "-o", default="output", help="Output directory for PDFs")
    parser.add_argument("--concurrency", "-c", type=int, default=5, help="Maximum number of concurrent tasks")
    parser.add_argument("--rate", "-r", type=float, default=1.0, help="Maximum number of requests per second")
    parser.add_argument("--selector", "-s", help="CSS selector for selective rendering")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(exist_ok=True)

    asyncio.run(converter_main(args.url, str(output_dir), args.concurrency, args.rate, args.selector))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        gui_main()
    else:
        cli_main()
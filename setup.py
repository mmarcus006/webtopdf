from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="web_to_pdf",
    version="0.1.0",
    author="Miller Marcus",
    author_email="mm@franchiseportal.io",
    description="A tool to convert web pages to PDF",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/web_to_pdf",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=[
        "requests",
        "beautifulsoup4",
        "pdfkit",
    ],
    entry_points={
        "console_scripts": [
            "web_to_pdf=main:main",
        ],
    },
)
# Oda Product Metadata Scraper

This project is a web scraping tool that extracts product metadata from a specified website's sitemaps and saves the data in a CSV file. The tool respects the site's `robots.txt` file and only scrapes URLs that are allowed for your specified user agent.

## Features

- Extracts specific product metadata fields (e.g., price, name, description) based on user-specified options.
- Saves the extracted metadata into a timestamped CSV file.
- Implemented on and respects `robots.txt` rules to avoid restricted pages.

## Requirements

- Python 3.10 or later
- The following Python libraries (included in `requirements.txt`):
  - `requests`
  - `beautifulsoup4`
  - `click`
  - `lxml`

## Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/mathiaswetterhus/odascraper.git
    cd odascraper/v2/

2. **Create and activate a virtual environment**:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On macOS/Linux
    .venv\Scripts\activate     # On Windows

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt

## Usage
- Run the script using the following command:
  ```bash
  python script.py <main_sitemap_url> [OPTIONS]
  
### Positional Arguments
- <main_sitemap_url>: The URL of the main sitemap to begin scraping.

### Options
- --gross-unit-price: Extracts the gross unit price.
- --full-name: Extracts the full name of the product.
- --description-from-supplier: Extracts the description from the supplier.
- --language-name: Extracts the language name.

## Example
```bash
python script.py "https://oda.com/sitemap.xml" --gross-unit-price --full-name
```

## Output
The extracted data is saved in a CSV file named product_report_<date>_<timestamp>.csv in the current directory.


## Improvements:
- Use urllib to parse robot.txt files
- Use the parsed robot.txt object to only make allowed requests and adhere to "good citizen" principles
- Abstract the parsing of the script tag (json with metadata) to better handle multiple vendors
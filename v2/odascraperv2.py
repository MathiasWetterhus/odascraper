import requests
import csv
import time
import re
import click
from typing import List
from datetime import datetime
from bs4 import BeautifulSoup


# Custom User-Agent header
HEADERS = {
    "User-Agent": "mono-bot iamengineertask/1.0 (mathiaswetterhus@gmail.com)"
}

# Exponential backoff parameters
INITIAL_BACKOFF = 1  # initial wait time in seconds
MAX_RETRIES = 5      # maximum number of retries

def fetch_url_with_backoff(url):
    """
    Fetch a URL with error handling, exponential backoff, and respect for the Retry-After header.
    """
    backoff = INITIAL_BACKOFF
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            response = requests.get(url, headers=HEADERS)
            
            if response.status_code == 200:
                return response
            
            elif response.status_code in [429] + list(range(500, 600)):
                retry_after = int(response.headers.get("Retry-After", backoff))
                print(f"Received {response.status_code}, retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                backoff *= 2
                retries += 1
            else:
                response.raise_for_status()
        
        except requests.exceptions.RequestException as e:
            print(f"Error fetching {url}: {e}")
            time.sleep(backoff)
            backoff *= 2
            retries += 1
    
    print(f"Failed to fetch {url} after {MAX_RETRIES} retries.")
    return None

def get_product_sitemap_urls(sitemap_url: str) -> List[str]:
    """
    Parse the main sitemap XML to get URLs of product-specific sitemaps.
    """
    response = fetch_url_with_backoff(sitemap_url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.content, 'xml')
    # Extract URLs of product-specific sitemap files
    product_sitemap_urls = [loc.text for loc in soup.find_all("loc") if "/products" in loc.text]
    return product_sitemap_urls

def get_product_urls(product_sitemap_url: str) -> List[str]:
    """
    Parse a product-specific sitemap XML to get individual product URLs.
    """
    response = fetch_url_with_backoff(product_sitemap_url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.content, 'xml')
    # Extract individual product URLs
    product_urls = [loc.text for loc in soup.find_all("loc")]
    return product_urls

def fetch_product_metadata(url: str, gross_unit_price: bool, full_name: bool, description_from_supplier: bool, language_name: bool):
    """
    Fetch and extract specified product metadata from a given product page URL.
    """
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    metadata = {}

    # Find the <script> tag containing the JSON data
    script_tag = soup.find("script", {"type": "application/json"})
    if script_tag:
        # Extract specified metadata fields using regex
        if gross_unit_price:
            gross_unit_price_match = re.search(r'"grossUnitPrice":"([\d\.]+)"', script_tag.string)
            metadata["grossUnitPrice"] = gross_unit_price_match.group(1) if gross_unit_price_match else None
        
        if full_name:
            full_name_match = re.search(r'"fullName":"(.*?)"', script_tag.string)
            metadata["fullName"] = full_name_match.group(1) if full_name_match else None
        
        if description_from_supplier:
            description_from_supplier_match = re.search(r'"descriptionFromSupplier":"(.*?)"', script_tag.string)
            metadata["descriptionFromSupplier"] = description_from_supplier_match.group(1) if description_from_supplier_match else None
        
        if language_name:
            language_name_match = re.search(r'"languageName":"(.*?)"', script_tag.string)
            metadata["languageName"] = language_name_match.group(1) if language_name_match else None
    else:
        print("Couldn't find the data script tag.")

    print(metadata)
    return metadata

@click.command()
@click.argument("main_sitemap_url")
@click.option("--gross-unit-price", "-g", default=False, is_flag=True, help="Extract gross unit price of the product.")
@click.option("--full-name", "-n", default=False, is_flag=True, help="Extracts the products full name.")
@click.option("--description-from-supplier", "-d", default=False, is_flag=True, help="Extract description from supplier.")
@click.option("--language-name", "-l", default=False, is_flag=True, help="Extract language name.")
def main(main_sitemap_url, gross_unit_price, full_name, description_from_supplier, language_name):
    # Step 1: Get product-specific sitemap URLs from the main sitemap
    product_sitemap_urls = get_product_sitemap_urls(main_sitemap_url)
    
    print(f"Found {len(product_sitemap_urls)} product-specific sitemaps.")

    products_data = []

    # Step 2: For each product-specific sitemap, get product URLs
    for product_sitemap_url in product_sitemap_urls:
        product_urls = get_product_urls(product_sitemap_url)
        print(f"Found {len(product_urls)} products in sitemap: {product_sitemap_url}")
        
        # Step 3: Fetch metadata for each product URL with specified fields
        for url in product_urls:
            metadata = fetch_product_metadata(url, gross_unit_price, full_name, description_from_supplier, language_name)
            if metadata:
                products_data.append(metadata)
                print(f"Fetched metadata for product: {metadata.get('fullName', 'Unnamed Product')}")

    # Step 4: Write the collected product data to a CSV file
    if products_data:
        # Generate filename with date and timestamp
        now = datetime.now()
        filename = f"product_report_{now.strftime('%Y%m%d_%H%M%S')}.csv"

        # Get the fieldnames for the CSV from the first product's keys
        fieldnames = products_data[0].keys()

        # Write to CSV file
        with open(filename, mode="w", newline='', encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products_data)

        print(f"Product data has been saved to {filename}")
    else:
        print("No product data to save.")

if __name__ == "__main__":
    main()
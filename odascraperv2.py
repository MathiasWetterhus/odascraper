import requests
from bs4 import BeautifulSoup
import time
import re

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

def get_product_sitemap_urls(sitemap_url):
    """
    Parse the main sitemap XML to get URLs of product-specific sitemaps.
    """
    response = fetch_url_with_backoff(sitemap_url)
    if not response:
        return []
    
    soup = BeautifulSoup(response.content, 'xml')
    # Extract URLs of product-specific sitemap files
    product_sitemap_urls = [loc.text for loc in soup.find_all("loc") if "/products/" in loc.text]
    return product_sitemap_urls

def get_product_urls(product_sitemap_url):
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

def fetch_product_metadata(url):
    """
    Fetch and extract product metadata from a given product page URL,
    including properties from both <meta> tags and JSON-like data using regex.
    """
    response = requests.get(url, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to fetch the page. Status code: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Initialize metadata dictionary
    metadata = {}
    

    # Find the <script> tag containing the JSON data
    script_tag = soup.find("script", {"id": "__NEXT_DATA__", "type": "application/json"})
    if script_tag:
        # Use regex to extract relevant properties
        gross_unit_price_match = re.search(r'"grossUnitPrice":"([\d\.]+)"', script_tag.string)
        full_name_match = re.search(r'"fullName":"(.*?)"', script_tag.string)
        description_from_supplier_match = re.search(r'"descriptionFromSupplier":"(.*?)"', script_tag.string)
        language_name_match = re.search(r'"languageName":"(.*?)"', script_tag.string)

        # Extract values if matches were found
        metadata["grossUnitPrice"] = gross_unit_price_match.group(1) if gross_unit_price_match else None
        metadata["fullName"] = full_name_match.group(1) if full_name_match else None
        metadata["descriptionFromSupplier"] = description_from_supplier_match.group(1) if description_from_supplier_match else None
        metadata["languageName"] = language_name_match.group(1) if language_name_match else None
    else:
        print("Couldn't find the data script tag.")
        metadata["grossUnitPrice"] = None
        metadata["fullName"] = None
        metadata["descriptionFromSupplier"] = None
        metadata["languageName"] = None
    print(metadata)
    return metadata

def main():
    # Step 1: Get product-specific sitemap URLs from the main sitemap
    main_sitemap_url = "https://oda.com/sitemap.xml"
    product_sitemap_urls = get_product_sitemap_urls(main_sitemap_url)
    
    print(f"Found {len(product_sitemap_urls)} product-specific sitemaps.")

    products_data = []
    
    # Step 2: For each product-specific sitemap, get product URLs
    for product_sitemap_url in product_sitemap_urls:
        product_urls = get_product_urls(product_sitemap_url)
        print(f"Found {len(product_urls)} products in sitemap: {product_sitemap_url}")
        
        # Step 3: Fetch metadata for each product URL
        for url in product_urls:
            metadata = fetch_product_metadata(url)
            if metadata:
                products_data.append(metadata)
                print(f"Fetched metadata for product: {metadata['fullName']}")

    # Do something with products_data, e.g., save to a file or database
    print("Completed fetching all product metadata.")

if __name__ == "__main__":
    main()
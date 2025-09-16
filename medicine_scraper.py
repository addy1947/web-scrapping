# Medicine Scraper for VS Code
# Save this as: medicine_scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import logging
from urllib.parse import urljoin
import os
import json
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def scrape_medicine(url, delay=2):
    """
    Scrape medicine information from 1mg URL
    
    Args:
        url (str): Medicine page URL
        delay (int): Delay between requests in seconds
    
    Returns:
        dict: Medicine data
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }
    
    try:
        # Respectful delay
        time.sleep(delay)
        logger.info(f"Scraping: {url}")
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Extract medicine name
        name = extract_field(soup, [
            # 1mg.com specific selectors
            ".DrugHeader__title",
            ".DrugHeader__name",
            ".ProductInfo__title",
            ".ProductInfo__name",
            "h1[class*='DrugHeader']",
            "h1[class*='ProductInfo']",
            "h1[class*='title']",
            "h1[class*='name']",
            # Generic selectors
            "h1",
            ".style__product-name",
            ".medicine-name",
            ".drug-name",
            ".product-title",
            "[class*='title']",
            "[class*='name']"
        ])
        
        # Extract image
        image = extract_image(soup, url)
        
        # Extract additional info
        manufacturer = extract_field(soup, [
            # 1mg.com specific selectors
            ".DrugHeader__manufacturer",
            ".DrugHeader__brand-name",
            ".DrugHeader__company",
            ".ProductInfo__manufacturer",
            ".ProductInfo__brand",
            ".manufacturer",
            ".brand-name", 
            ".company-name",
            ".drug-manufacturer",
            ".medicine-brand",
            "[class*='manufacturer']",
            "[class*='brand']",
            "[class*='company']"
        ])
        
        composition = extract_field(soup, [
            # 1mg.com specific selectors
            ".DrugHeader__salt-info",
            ".DrugHeader__composition",
            ".ProductInfo__composition",
            ".ProductInfo__salt",
            ".salt-info",
            ".composition",
            ".medicine-composition",
            ".drug-composition",
            ".salt-composition",
            "[class*='salt']",
            "[class*='composition']",
            "[class*='ingredient']"
        ])
        
        # Extract quantity information
        quantity = extract_quantity(soup)
        
        # Extract both MRP and discounted price
        price_info = extract_price_info(soup)
        
        # Get the main price for logging (use discounted price if available, otherwise MRP)
        price = price_info.get("discounted_price", price_info.get("mrp", "N/A"))
        
        result = {
            "name": name,
            "mrp": price_info.get("mrp", "N/A"),
            "discounted_price": price_info.get("discounted_price", "N/A"),
            "price": price_info.get("discounted_price", "N/A"),  # Keep for backward compatibility
            "quantity": quantity,
            "image": image,
            "manufacturer": manufacturer,
            "composition": composition,
            "url": url,
            "status": "Success"
        }
        
        logger.info(f"✅ Successfully scraped: {name} - {price}")
        return result
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Network error for {url}: {e}")
        return create_error_record(url, f"Network error: {e}")
    except Exception as e:
        logger.error(f"❌ Parsing error for {url}: {e}")
        return create_error_record(url, f"Parsing error: {e}")

def extract_quantity(soup):
    """Extract quantity information (number of tablets/strips)"""
    
    # Common quantity selectors
    quantity_selectors = [
        # 1mg.com specific selectors
        ".DrugHeader__pack-size",
        ".DrugHeader__quantity",
        ".ProductInfo__pack-size",
        ".ProductInfo__quantity",
        ".pack-size",
        ".quantity",
        ".tablet-count",
        ".strip-count",
        # Generic selectors
        "[class*='pack']",
        "[class*='quantity']",
        "[class*='count']",
        "[class*='size']"
    ]
    
    for selector in quantity_selectors:
        try:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and text != "":
                    # Look for patterns like "10 tablets", "1 Strip", "20 tabs", etc.
                    quantity_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:tablets?|tabs?|strips?|capsules?|pills?)', text, re.IGNORECASE)
                    if quantity_match:
                        quantity_num = quantity_match.group(1)
                        # If it's a decimal like 15.0, convert to integer
                        if quantity_num.endswith('.0'):
                            quantity_num = quantity_num[:-2]
                        return f"{quantity_num} tablets"
                    
                    # If no specific pattern, return the text if it contains numbers
                    if re.search(r'\d+', text):
                        return text
        except Exception:
            continue
    
    # Try to find quantity in the price text or other areas
    try:
        # Look in all text for quantity patterns
        all_text = soup.get_text()
        quantity_patterns = [
            r'(\d+(?:\.\d+)?)\s*tablets?\s*in\s*\d+\s*strip',  # "15.0 tablets in 1 strip"
            r'(\d+(?:\.\d+)?)\s*tablets?',  # "15 tablets"
            r'(\d+(?:\.\d+)?)\s*tabs?',  # "15 tabs"
            r'(\d+(?:\.\d+)?)\s*strips?',  # "1 strip"
            r'(\d+(?:\.\d+)?)\s*capsules?',  # "15 capsules"
            r'(\d+(?:\.\d+)?)\s*pills?',  # "15 pills"
            r'(\d+(?:\.\d+)?)\s*pieces?'  # "15 pieces"
        ]
        
        for pattern in quantity_patterns:
            match = re.search(pattern, all_text, re.IGNORECASE)
            if match:
                quantity_num = match.group(1)
                # If it's a decimal like 15.0, convert to integer
                if quantity_num.endswith('.0'):
                    quantity_num = quantity_num[:-2]
                return f"{quantity_num} tablets"
    except Exception:
        pass
    
    return "N/A"

def extract_price_info(soup):
    """Extract both MRP and discounted price information"""
    
    # First, try to find price containers that might have both MRP and discounted price
    price_containers = [
        # 1mg.com specific selectors for price containers
        ".DrugPriceBox",
        ".PriceBox", 
        ".DrugPrice",
        ".PriceBoxPlanOption",
        ".SubstituteItem__unit-price___MIbLo",
        # Generic price containers
        "[class*='price']",
        "[class*='Price']",
        "[class*='cost']",
        ".price-display",
        ".price-container",
        ".pricing"
    ]
    
    for container_selector in price_containers:
        try:
            container = soup.select_one(container_selector)
            if container:
                # Get all text from the container
                container_text = container.get_text(strip=True)
                if container_text and ('₹' in container_text or 'Rs' in container_text):
                    price_info = parse_price_info(container_text)
                    if price_info.get("discounted_price") != "N/A" or price_info.get("mrp") != "N/A":
                        return price_info
        except Exception:
            continue
    
    # If no container found, try individual price selectors
    individual_selectors = [
        # 1mg.com specific selectors
        ".DrugPriceBox__best-price___32JXw",
        ".DrugPriceBox__price",
        ".PriceBox__price",
        ".PriceBox__best-price",
        ".SubstituteItem__unit-price___MIbLo",
        ".PriceBoxPlanOption__offerPrice",
        ".PriceBoxPlanOption__price",
        ".DrugPrice__price",
        ".DrugPrice__best-price",
        # Generic selectors
        ".style__price-tag",
        ".price-display",
        ".price",
        ".best-price",
        ".offer-price",
        "[class*='price']",
        "[class*='Price']",
        "[class*='cost']"
    ]
    
    for selector in individual_selectors:
        try:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and text != "":
                    price_info = parse_price_info(text)
                    if price_info.get("discounted_price") != "N/A" or price_info.get("mrp") != "N/A":
                        return price_info
        except Exception:
            continue
    
    return {"mrp": "N/A", "discounted_price": "N/A"}

def parse_price_info(price_text):
    """Parse price text to extract both MRP and discounted price"""
    
    # Remove extra whitespace
    price_text = " ".join(price_text.split())
    
    mrp = "N/A"
    discounted_price = "N/A"
    
    # Look for MRP first
    mrp_patterns = [
        r'MRP\s*₹\s*(\d+(?:\.\d+)?)',
        r'MRP\s*Rs\.?\s*(\d+(?:\.\d+)?)',
        r'Maximum Retail Price\s*₹\s*(\d+(?:\.\d+)?)'
    ]
    
    for pattern in mrp_patterns:
        match = re.search(pattern, price_text, re.IGNORECASE)
        if match:
            mrp_value = match.group(1)
            # Clean up decimal places (e.g., 34.274 -> 34.27)
            if '.' in mrp_value and len(mrp_value.split('.')[1]) > 2:
                mrp_value = f"{float(mrp_value):.2f}"
            mrp = f"₹{mrp_value}"
            break
    
    # Look for discounted price
    discounted_patterns = [
        r'Discounted Price:\s*₹\s*(\d+(?:\.\d+)?)',
        r'Offer Price:\s*₹\s*(\d+(?:\.\d+)?)',
        r'Best Price:\s*₹\s*(\d+(?:\.\d+)?)',
        r'Final Price:\s*₹\s*(\d+(?:\.\d+)?)',
        r'₹\s*(\d+(?:\.\d+)?)\s*\(.*?off.*?\)',
        r'₹\s*(\d+(?:\.\d+)?)\s*after.*?discount'
    ]
    
    for pattern in discounted_patterns:
        match = re.search(pattern, price_text, re.IGNORECASE)
        if match:
            discounted_price = f"₹{match.group(1)}"
            break
    
    # If we have both MRP and discounted price in the text, extract both
    if 'MRP' in price_text and '₹' in price_text:
        prices = re.findall(r'₹\s*(\d+(?:\.\d+)?)', price_text)
        if len(prices) >= 2:
            if mrp == "N/A":
                mrp = f"₹{prices[0]}"
            if discounted_price == "N/A":
                discounted_price = f"₹{prices[1]}"
    
    # If no discounted price found, use the first price as both
    if discounted_price == "N/A" and mrp != "N/A":
        discounted_price = mrp
    elif mrp == "N/A" and discounted_price != "N/A":
        mrp = discounted_price
    
    return {
        "mrp": mrp,
        "discounted_price": discounted_price
    }

def extract_price_comprehensive(soup):
    """Extract price with comprehensive approach to get both MRP and discounted price"""
    
    # First, try to find price containers that might have both MRP and discounted price
    price_containers = [
        # 1mg.com specific selectors for price containers
        ".DrugPriceBox",
        ".PriceBox", 
        ".DrugPrice",
        ".PriceBoxPlanOption",
        ".SubstituteItem__unit-price___MIbLo",
        # Generic price containers
        "[class*='price']",
        "[class*='Price']",
        "[class*='cost']",
        ".price-display",
        ".price-container",
        ".pricing"
    ]
    
    for container_selector in price_containers:
        try:
            container = soup.select_one(container_selector)
            if container:
                # Get all text from the container
                container_text = container.get_text(strip=True)
                if container_text and ('₹' in container_text or 'Rs' in container_text):
                    cleaned_price = clean_price_text(container_text)
                    if cleaned_price != "N/A":
                        return cleaned_price
        except Exception:
            continue
    
    # If no container found, try individual price selectors
    individual_selectors = [
        # 1mg.com specific selectors
        ".DrugPriceBox__best-price___32JXw",
        ".DrugPriceBox__price",
        ".PriceBox__price",
        ".PriceBox__best-price",
        ".SubstituteItem__unit-price___MIbLo",
        ".PriceBoxPlanOption__offerPrice",
        ".PriceBoxPlanOption__price",
        ".DrugPrice__price",
        ".DrugPrice__best-price",
        # Generic selectors
        ".style__price-tag",
        ".price-display",
        ".price",
        ".best-price",
        ".offer-price",
        "[class*='price']",
        "[class*='Price']",
        "[class*='cost']"
    ]
    
    for selector in individual_selectors:
        try:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and text != "":
                    cleaned_price = clean_price_text(text)
                    if cleaned_price != "N/A":
                        return cleaned_price
        except Exception:
            continue
    
    return "N/A"

def extract_field(soup, selectors):
    """Extract text from first matching selector"""
    for selector in selectors:
        try:
            element = soup.select_one(selector)
            if element:
                text = element.get_text(strip=True)
                if text and text != "":
                    # Special handling for price fields
                    if "price" in selector.lower() or "Price" in selector:
                        # Clean up price text - extract only the price value
                        text = clean_price_text(text)
                        if text and text != "N/A":
                            return text
                    return text
        except Exception:
            continue
    return "N/A"

def clean_price_text(price_text):
    """Clean and extract the best price value, prioritizing discounted price over MRP"""
    
    # Remove extra whitespace
    price_text = " ".join(price_text.split())
    
    # First, try to find discounted price (this should be prioritized)
    discounted_patterns = [
        r'Discounted Price:\s*₹\s*(\d+(?:\.\d+)?)',  # Discounted Price: ₹50.1
        r'Offer Price:\s*₹\s*(\d+(?:\.\d+)?)',  # Offer Price: ₹50.1
        r'Best Price:\s*₹\s*(\d+(?:\.\d+)?)',  # Best Price: ₹50.1
        r'Final Price:\s*₹\s*(\d+(?:\.\d+)?)',  # Final Price: ₹50.1
        r'₹\s*(\d+(?:\.\d+)?)\s*\(.*?off.*?\)',  # ₹50.1 (9% off)
        r'₹\s*(\d+(?:\.\d+)?)\s*after.*?discount',  # ₹50.1 after discount
    ]
    
    for pattern in discounted_patterns:
        match = re.search(pattern, price_text, re.IGNORECASE)
        if match:
            price_value = match.group(1)
            return f"₹{price_value}"
    
    # Special handling for the specific pattern: MRP₹55Discount Percentage:9% off₹Discounted Price:50.1
    if 'Discounted Price:' in price_text:
        discount_match = re.search(r'Discounted Price:\s*(\d+(?:\.\d+)?)', price_text, re.IGNORECASE)
        if discount_match:
            price_value = discount_match.group(1)
            return f"₹{price_value}"
    
    # If we have both MRP and discounted price, extract the discounted one
    if 'MRP' in price_text and '₹' in price_text:
        # Look for pattern: MRP₹55...₹50.1 (extract the second price)
        prices = re.findall(r'₹\s*(\d+(?:\.\d+)?)', price_text)
        if len(prices) >= 2:
            # Return the second price (usually the discounted one)
            return f"₹{prices[1]}"
        elif len(prices) == 1:
            # If only one price found, check if it's after MRP
            mrp_match = re.search(r'MRP.*?₹\s*(\d+(?:\.\d+)?)', price_text, re.IGNORECASE)
            if mrp_match:
                # This is MRP, look for another price
                other_prices = re.findall(r'(?:after|off|discount|offer).*?₹\s*(\d+(?:\.\d+)?)', price_text, re.IGNORECASE)
                if other_prices:
                    return f"₹{other_prices[0]}"
    
    # If no discounted price found, look for any price that's not explicitly MRP
    non_mrp_patterns = [
        r'₹\s*(\d+(?:\.\d+)?)(?!.*MRP)',  # ₹50.1 but not if followed by MRP
        r'Rs\.?\s*(\d+(?:\.\d+)?)(?!.*MRP)',  # Rs 50 but not if followed by MRP
        r'INR\s*(\d+(?:\.\d+)?)(?!.*MRP)',  # INR 50 but not if followed by MRP
    ]
    
    for pattern in non_mrp_patterns:
        match = re.search(pattern, price_text, re.IGNORECASE)
        if match:
            price_value = match.group(1)
            return f"₹{price_value}"
    
    # Fallback: try to find any price pattern
    currency_match = re.search(r'[₹Rs]\.?\s*(\d+(?:\.\d+)?)', price_text, re.IGNORECASE)
    if currency_match:
        price_value = currency_match.group(1)
        return f"₹{price_value}"
    
    # If still no match, return the original text if it's short and contains currency
    if len(price_text) < 20 and ('₹' in price_text or 'Rs' in price_text):
        return price_text
    
    return "N/A"

def extract_image(soup, base_url):
    """Extract image URL with comprehensive fallbacks for 1mg.com"""
    image_selectors = [
        # 1mg.com specific selectors
        "img[class*='product-image']",
        "img[class*='ProductImage']", 
        "img[class*='medicine-image']",
        "img[class*='drug-image']",
        ".ProductImage img",
        ".ProductImage__image img",
        ".DrugImage img",
        ".MedicineImage img",
        ".product-photo img",
        ".product-image img",
        ".medicine-photo img",
        ".drug-photo img",
        # Generic selectors
        "img.style__product-image___3CRoG",
        ".product-image img",
        ".medicine-image",
        ".product-photo img",
        # Additional fallbacks
        "img[src*='1mg']",
        "img[data-src*='1mg']",
        "img[alt*='medicine']",
        "img[alt*='drug']",
        "img[alt*='product']"
    ]
    
    for selector in image_selectors:
        try:
            img_tag = soup.select_one(selector)
            if img_tag:
                # Try multiple attributes for image source
                img_src = (img_tag.get("src") or 
                          img_tag.get("data-src") or 
                          img_tag.get("data-lazy-src") or
                          img_tag.get("data-original"))
                
                if img_src:
                    # Clean up the URL
                    if img_src.startswith('//'):
                        img_src = 'https:' + img_src
                    elif img_src.startswith('/'):
                        img_src = urljoin(base_url, img_src)
                    elif not img_src.startswith('http'):
                        img_src = urljoin(base_url, img_src)
                    
                    # Validate it's a proper image URL
                    if any(ext in img_src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                        return img_src
        except Exception:
            continue
    
    # If no specific selectors work, try to find any img tag with 1mg domain
    try:
        all_images = soup.find_all('img')
        for img in all_images:
            src = img.get("src") or img.get("data-src")
            if src and '1mg' in src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp', '.gif']):
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    src = urljoin(base_url, src)
                return src
    except Exception:
        pass
    
    # Try to extract from JSON-LD structured data
    try:
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            import json
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'image' in data:
                    img_url = data['image']
                    if isinstance(img_url, str):
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = urljoin(base_url, img_url)
                        return img_url
                    elif isinstance(img_url, list) and len(img_url) > 0:
                        img_url = img_url[0]
                        if img_url.startswith('//'):
                            img_url = 'https:' + img_url
                        elif img_url.startswith('/'):
                            img_url = urljoin(base_url, img_url)
                        return img_url
            except (json.JSONDecodeError, KeyError):
                continue
    except Exception:
        pass
    
    # Try to find image in meta tags
    try:
        meta_image = soup.find('meta', property='og:image')
        if meta_image and meta_image.get('content'):
            img_url = meta_image.get('content')
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = urljoin(base_url, img_url)
            return img_url
    except Exception:
        pass
    
    return "N/A"

def create_error_record(url, error_msg):
    """Create error record for failed scrapes"""
    return {
        "name": "Error",
        "mrp": "Error",
        "discounted_price": "Error",
        "price": "Error",
        "quantity": "Error",
        "image": "Error", 
        "manufacturer": "Error",
        "composition": "Error",
        "url": url,
        "status": error_msg
    }

def scrape_medicines_batch(urls, delay=2, save_progress=True):
    """
    Scrape multiple medicine URLs with progress tracking
    
    Args:
        urls (list): List of URLs to scrape
        delay (int): Delay between requests
        save_progress (bool): Save intermediate results
        
    Returns:
        pd.DataFrame: Scraped data
    """
    if not urls:
        logger.warning("No URLs provided!")
        return pd.DataFrame()
    
    logger.info(f"🚀 Starting batch scrape of {len(urls)} URLs")
    logger.info(f"⏰ Using {delay}s delay between requests")
    
    results = []
    total = len(urls)
    
    for i, url in enumerate(urls, 1):
        logger.info(f"📊 Progress: {i}/{total}")
        
        try:
            result = scrape_medicine(url, delay)
            results.append(result)
            
            # Progress saving
            if save_progress and i % 5 == 0:
                temp_df = pd.DataFrame(results)
                progress_file = f"progress_backup_{i}.csv"
                temp_df.to_csv(progress_file, index=False)
                logger.info(f"💾 Progress saved: {progress_file}")
                
                # Also save progress as JSON
                try:
                    progress_json = f"progress_backup_{i}.json"
                    json_data = temp_df.to_dict('records')
                    with open(progress_json, 'w', encoding='utf-8') as f:
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                    logger.info(f"📄 Progress JSON saved: {progress_json}")
                except Exception as e:
                    logger.warning(f"Could not save progress JSON: {e}")
                
        except Exception as e:
            logger.error(f"Unexpected error processing {url}: {e}")
            results.append(create_error_record(url, str(e)))
    
    return pd.DataFrame(results)

def display_summary(df):
    """Display scraping summary statistics"""
    total = len(df)
    successful = len(df[df['status'] == 'Success'])
    failed = total - successful
    
    print("\n" + "="*50)
    print("📋 SCRAPING SUMMARY")
    print("="*50)
    print(f"Total URLs processed: {total}")
    print(f"✅ Successful extractions: {successful}")
    print(f"❌ Failed extractions: {failed}")
    
    if failed > 0:
        print(f"\n🔍 Failed URLs:")
        failed_df = df[df['status'] != 'Success']
        for _, row in failed_df.iterrows():
            print(f"  - {row['url']}: {row['status']}")
    
    print("="*50)

def save_results(df, filename="medicines_scraped.csv"):
    """Save results to CSV, Excel, and JSON with error handling"""
    try:
        # Save as CSV
        df.to_csv(filename, index=False)
        logger.info(f"💾 CSV results saved to: {filename}")
        
        # Save as Excel if possible
        try:
            excel_file = filename.replace('.csv', '.xlsx')
            df.to_excel(excel_file, index=False)
            logger.info(f"📊 Excel file saved: {excel_file}")
        except ImportError:
            logger.info("📝 Install openpyxl for Excel export: pip install openpyxl")
        
        # Save as JSON
        try:
            json_file = filename.replace('.csv', '.json')
            # Convert DataFrame to list of dictionaries for better JSON structure
            json_data = df.to_dict('records')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 JSON file saved: {json_file}")
        except Exception as json_error:
            logger.error(f"Error saving JSON file: {json_error}")
            
        return filename
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return None

def main():
    """Main function - Configure your URLs here and run"""
    
    # 🔹 ADD YOUR MEDICINE URLS HERE
    urls = [
        "https://www.1mg.com/drugs/dolo-650-tablet-74467",
        "https://www.1mg.com/drugs/crocin-pain-relief-tablet-323789",
        "https://www.1mg.com/otc/new-saridon-tablet-for-pain-relief-provides-fast-headache-relief-otc123063",
        "https://www.1mg.com/drugs/crocin-advance-500mg-tablet-600468",
        # Add more URLs here...
    ]
    
    # Configuration
    DELAY_SECONDS = 0  # No delay between requests
    OUTPUT_FILE = "medicines_final.csv"
    
    print("🏥 Medicine Scraper for VS Code")
    print("="*50)
    
    if not urls:
        print("⚠️  No URLs configured!")
        print("📝 Please add medicine URLs to the 'urls' list in main() function")
        return None
    
    print(f"🎯 Target URLs: {len(urls)}")
    print(f"⏰ Delay between requests: {DELAY_SECONDS}s")
    print(f"📁 Output file: {OUTPUT_FILE}")
    print("="*50)
    
    # Run scraping
    try:
        df = scrape_medicines_batch(urls, delay=DELAY_SECONDS)
        
        if df.empty:
            logger.error("No data scraped!")
            return None
            
        # Display results
        display_summary(df)
        
        # Show sample data
        print(f"\n📋 Sample Results (first 3 rows):")
        display_columns = ['name', 'mrp', 'discounted_price', 'quantity', 'status']
        available_columns = [col for col in display_columns if col in df.columns]
        print(df[available_columns].head(3).to_string(index=False))
        
        # Save results
        saved_file = save_results(df, OUTPUT_FILE)
        
        if saved_file:
            print(f"\n✨ Scraping completed successfully!")
            print(f"📂 Check your project folder for: {saved_file}")
        
        return df
        
    except KeyboardInterrupt:
        logger.info("🛑 Scraping interrupted by user")
        return None
    except Exception as e:
        logger.error(f"💥 Unexpected error in main: {e}")
        return None

def quick_test():
    """Test scraper with single URL"""
    test_url = "https://www.1mg.com/drugs/dolo-650-tablet-74467"
    
    print("🧪 Running quick test...")
    result = scrape_medicine(test_url, delay=1)
    
    test_df = pd.DataFrame([result])
    print(f"\n📋 Test Result:")
    print(test_df.to_string(index=False))
    
    return test_df

if __name__ == "__main__":
    # Uncomment line below to run quick test first:
    # quick_test()
    
    # Run main scraper
    df = main()
    
    if df is not None and not df.empty:
        print(f"\n🎉 All done! Check the CSV file in your project folder.")
    else:
        print(f"\n❌ Scraping failed. Check the logs above for errors.")
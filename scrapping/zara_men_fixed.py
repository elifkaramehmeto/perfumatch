from playwright.async_api import async_playwright
import asyncio
import json
import os
import re
import time
import signal
import sys
from datetime import datetime

# Global variable to track if we should exit
should_exit = False

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    global should_exit
    print("\nInterrupt received. Finishing current operation and exiting...")
    should_exit = True

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

async def scrape_zara_mens_perfumes():
    screenshots_dir = "zara_men_screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
        print(f"Created directory: {screenshots_dir}")
    
    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()
            
            print("Opening Zara men's perfumes page...")
            try:
                response = await page.goto("https://www.zara.com/tr/tr/erkek-aksesuarlar-parfemler-l551.html?v1=2436468", timeout=120000)
                if not response.ok:
                    print(f"Failed to load page: {response.status} - {response.status_text}")
                    return []
            except Exception as e:
                print(f"Error navigating to page: {e}")
                return []
            
            print("Waiting for page to load...")
            await asyncio.sleep(10)
            
            # Accept cookies if dialog appears
            try:
                cookie_selectors = [
                    'button:has-text("Tümünü Kabul Et")',
                    'button:has-text("Accept All")',
                    'button:has-text("Kabul Et")',
                    '[data-qa="cookies-accept"]',
                    '.cookies-accept',
                    '#onetrust-accept-btn-handler'
                ]
                
                for selector in cookie_selectors:
                    try:
                        accept_button = page.locator(selector)
                        if await accept_button.count() > 0:
                            await accept_button.click()
                            print(f"Accepted cookies using selector: {selector}")
                            await asyncio.sleep(3)
                            break
                    except Exception as e:
                        continue
            except Exception as e:
                print(f"Cookie handling error: {e}")
            
            # Check if browser is still open
            if page.is_closed():
                print("Browser was closed by user")
                return []
            
            # Scroll down to load all products (lazy loading)
            print("Scrolling to load all products...")
            previous_height = 0
            max_scroll_attempts = 20
            scroll_attempts = 0
            
            while scroll_attempts < max_scroll_attempts:
                try:
                    if page.is_closed():
                        print("Browser was closed by user during scrolling")
                        return []
                    
                    # Scroll to bottom of page
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(3)
                    
                    # Get the new height
                    current_height = await page.evaluate("document.body.scrollHeight")
                    
                    # Check if we've reached the bottom (no new content loaded)
                    if current_height == previous_height:
                        print(f"Reached the bottom of the page after {scroll_attempts} scrolls")
                        break
                    
                    previous_height = current_height
                    scroll_attempts += 1
                    print(f"Scroll attempt {scroll_attempts}/{max_scroll_attempts}, height: {current_height}")
                    
                except Exception as e:
                    print(f"Error during scrolling: {e}")
                    if page.is_closed():
                        print("Browser was closed during scrolling")
                        return []
                    await asyncio.sleep(1)
            
            # Take screenshot after scrolling
            try:
                if not page.is_closed():
                    await page.screenshot(path=os.path.join(screenshots_dir, "after_scrolling.png"), full_page=True)
                    print("Screenshot saved after scrolling")
            except Exception as e:
                print(f"Could not save screenshot: {e}")
            
            # Check if browser is still open
            if page.is_closed():
                print("Browser was closed by user")
                return []
            
            print("Looking for product links...")
            
            # Find all product links using the correct selector
            product_links = []
            try:
                # Use the correct selector based on our analysis
                product_link_elements = await page.locator('.product-link').all()
                print(f"Found {len(product_link_elements)} product link elements")
                
                for element in product_link_elements:
                    try:
                        href = await element.get_attribute('href')
                        if href:
                            # Filter for perfume/fragrance products
                            if any(term in href.lower() for term in ['parfum', 'parfem', 'edp', 'edt', 'fragrance', 'cologne']):
                                product_links.append(href)
                            # Also include products with p20 pattern (Zara product codes)
                            elif 'p20' in href and any(term in href.lower() for term in ['mist', 'cream', 'body']):
                                product_links.append(href)
                    except Exception as e:
                        print(f"Error getting href from element: {e}")
                        continue
                        
            except Exception as e:
                print(f"Error finding product links: {e}")
            
            # Remove duplicates while preserving order
            unique_links = []
            for link in product_links:
                if link not in unique_links:
                    unique_links.append(link)
            product_links = unique_links
            
            print(f"Found {len(product_links)} unique product links")
            if product_links:
                print("Sample links:")
                for i, link in enumerate(product_links[:5]):
                    print(f"  {i+1}. {link}")
            else:
                print("No product links found. Exiting.")
                return []
            
            perfumes = []
            
            # Visit each product detail page
            for i, link in enumerate(product_links):
                if should_exit or page.is_closed():
                    print("Interruption detected, stopping product scraping")
                    break
                    
                full_url = link if link.startswith('http') else f"https://www.zara.com{link}"
                print(f"\nVisiting product {i+1}/{len(product_links)}: {full_url}")
                
                try:
                    await page.goto(full_url, timeout=60000)
                    await asyncio.sleep(3)
                    
                    # Take screenshot for first few products
                    if i < 3:
                        try:
                            await page.screenshot(path=os.path.join(screenshots_dir, f"product_{i+1}.png"))
                            print(f"Product screenshot saved")
                        except Exception as e:
                            print(f"Could not save product screenshot: {e}")
                    
                    # Extract product information
                    name = "Unknown"
                    price = "Unknown"
                    description = ""
                    notes = []
                    image_url = ""
                    
                    # Try different selectors for product name
                    name_selectors = [
                        'h1.product-detail-info__header-name',
                        '.product-detail-info h1',
                        'h1[data-qa-heading]',
                        '.product-name',
                        '.product-info h1',
                        'h1'
                    ]
                    
                    for name_selector in name_selectors:
                        try:
                            if await page.locator(name_selector).count() > 0:
                                name_el = await page.query_selector(name_selector)
                                if name_el:
                                    name = await name_el.inner_text()
                                    name = name.strip()
                                    print(f"Found product name: {name}")
                                    break
                        except Exception as e:
                            continue
                    
                    # Try different selectors for price
                    price_selectors = [
                        '.price__amount',
                        '.product-detail-unit-price',
                        '.price',
                        '.product-price',
                        'span[data-qa-price]',
                        '.product-detail-price',
                        '[data-qa-price]',
                        '[data-price]',
                        '[class*="price"]'
                    ]
                    
                    for price_selector in price_selectors:
                        try:
                            if await page.locator(price_selector).count() > 0:
                                price_el = await page.query_selector(price_selector)
                                if price_el:
                                    price = await price_el.inner_text()
                                    price = price.strip()
                                    print(f"Found price: {price}")
                                    break
                        except Exception as e:
                            continue
                    
                    # Try different selectors for product description
                    desc_selectors = [
                        '.product-detail-description',
                        '.product-detail-info__description',
                        '.product-info-text',
                        '.description',
                        'p[class*="description"]',
                        'div[class*="description"]',
                        'div[class*="detail"] p'
                    ]
                    
                    for desc_selector in desc_selectors:
                        try:
                            if await page.locator(desc_selector).count() > 0:
                                desc_elements = await page.query_selector_all(desc_selector)
                                if desc_elements:
                                    desc_texts = []
                                    for elem in desc_elements:
                                        desc_texts.append(await elem.inner_text())
                                    description = "\n".join(desc_texts).strip()
                                    if description:
                                        print(f"Found description: {description[:50]}...")
                                        break
                        except Exception as e:
                            continue
                    
                    # Get image URL if available
                    image_selectors = [
                        'img.media-image__image',
                        '.product-detail-image img',
                        '.product-image img',
                        'picture img',
                        'img[srcset]',
                        'img[src*="zara"]',
                        'img[class*="product"]',
                        'img'
                    ]
                    
                    for img_selector in image_selectors:
                        try:
                            if await page.locator(img_selector).count() > 0:
                                img_el = await page.query_selector(img_selector)
                                if img_el:
                                    image_url = await img_el.get_attribute('src')
                                    if not image_url:
                                        image_url = await img_el.get_attribute('srcset')
                                    
                                    if image_url:
                                        print(f"Found image URL: {image_url[:50]}...")
                                        break
                        except Exception as e:
                            continue
                    
                    # Extract notes from description if available
                    if description:
                        # Look for fragrance notes in description
                        fragrance_keywords = [
                            "vanilla", "rose", "jasmine", "sandalwood", "amber", "musk", "citrus", 
                            "bergamot", "lavender", "vetiver", "patchouli", "cedar", "oud",
                            "woody", "spicy", "aquatic", "marine", "fresh", "floral", "fruity"
                        ]
                        
                        desc_lower = description.lower()
                        for keyword in fragrance_keywords:
                            if keyword in desc_lower:
                                notes.append(keyword.capitalize())
                    
                    # Compile all data
                    perfume_data = {
                        "name": name,
                        "price": price,
                        "description": description,
                        "notes": notes,
                        "image_url": image_url,
                        "product_url": full_url,
                        "brand": "Zara",
                        "gender": "Men",
                        "scrape_date": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    perfumes.append(perfume_data)
                    print(f"Added product {i+1} to results")
                    
                    # Sleep briefly between requests
                    await asyncio.sleep(2)
                    
                except asyncio.CancelledError:
                    print(f"Processing of product {i+1} was interrupted")
                    break
                except Exception as e:
                    print(f"Error processing product {i+1}: {e}")
                    continue

            return perfumes
    except asyncio.CancelledError:
        print("Scraping was interrupted by user")
    except Exception as e:
        print(f"Fatal error during scraping: {e}")
    finally:
        if browser:
            try:
                await browser.close()
            except:
                pass
        return perfumes if 'perfumes' in locals() else []

async def main():
    try:
        print(f"Starting Zara men's perfume scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        result = await scrape_zara_mens_perfumes()
        print("\nScraping completed!")
        print(f"Total men's perfumes found: {len(result)}")
        
        if result:
            # Create output filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"zara_mens_perfumes_{timestamp}.json"
            
            # Save results to file
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"Results saved to {output_file}")
            
            # Print sample of results
            print("\nSample of scraped perfumes:")
            for i, perfume in enumerate(result[:3]):
                print(f"\nPerfume {i+1}:")
                print(f"Name: {perfume['name']}")
                print(f"Price: {perfume['price']}")
                print(f"Notes: {', '.join(perfume['notes']) if perfume['notes'] else 'None'}")
                if perfume['description']:
                    print(f"Description: {perfume['description'][:100]}...")
                print(f"URL: {perfume['product_url']}")
            
            if len(result) > 3:
                print(f"\n... and {len(result) - 3} more perfumes")
        else:
            print("No perfumes were found.")
    except asyncio.CancelledError:
        print("Main function was interrupted")
    except KeyboardInterrupt:
        print("Script was interrupted by keyboard")
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    
    try:
        input("Press Enter to continue...")
    except (KeyboardInterrupt, EOFError):
        pass
    
    print("Script finished")

# Usage
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScript terminated by user")
        sys.exit(0)
    except Exception as e:
        print(f"Unhandled exception: {e}")
        sys.exit(1) 
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

async def debug_zara_page():
    """Debug function to understand the page structure"""
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
                    return
            except Exception as e:
                print(f"Error navigating to page: {e}")
                return
            
            print("Page loaded, waiting 10 seconds for content...")
            await asyncio.sleep(10)
            
            # Take initial screenshot
            try:
                await page.screenshot(path=os.path.join(screenshots_dir, "initial_page.png"), full_page=True)
                print("Initial screenshot saved")
            except Exception as e:
                print(f"Could not save screenshot: {e}")
            
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
            
            # Take screenshot after cookies
            try:
                await page.screenshot(path=os.path.join(screenshots_dir, "after_cookies.png"), full_page=True)
                print("After cookies screenshot saved")
            except Exception as e:
                print(f"Could not save screenshot: {e}")
            
            # Get page title and URL
            try:
                title = await page.title()
                url = page.url
                print(f"Page title: {title}")
                print(f"Current URL: {url}")
            except Exception as e:
                print(f"Error getting page info: {e}")
            
            # Check for common elements
            print("\n=== DEBUGGING PAGE STRUCTURE ===")
            
            # Check for various container elements
            container_selectors = [
                'main',
                'body',
                '.layout-products-wrapper',
                '.product-grid',
                '.media-grid',
                '.products-wrapper',
                '.product-list',
                '[data-qa="product-list"]',
                '.layout-content',
                '.category-products',
                '.product-container'
            ]
            
            for selector in container_selectors:
                try:
                    count = await page.locator(selector).count()
                    print(f"Found {count} elements with selector: {selector}")
                    if count > 0:
                        # Get some info about the first element
                        first_el = page.locator(selector).first
                        try:
                            text_content = await first_el.text_content()
                            if text_content:
                                print(f"  First element text (first 100 chars): {text_content[:100]}...")
                        except:
                            pass
                except Exception as e:
                    print(f"Error checking selector {selector}: {e}")
            
            # Look for any links
            print("\n=== CHECKING FOR LINKS ===")
            try:
                all_links = await page.locator('a').all()
                print(f"Total links found: {len(all_links)}")
                
                # Check for product-like links
                product_like_links = []
                for link in all_links[:50]:  # Check first 50 links
                    try:
                        href = await link.get_attribute('href')
                        if href and any(term in href.lower() for term in ['p2', 'product', 'parfum', 'parfem']):
                            product_like_links.append(href)
                    except:
                        continue
                
                print(f"Product-like links found: {len(product_like_links)}")
                for i, link in enumerate(product_like_links[:10]):
                    print(f"  {i+1}. {link}")
                    
            except Exception as e:
                print(f"Error checking links: {e}")
            
            # Look for images
            print("\n=== CHECKING FOR IMAGES ===")
            try:
                all_images = await page.locator('img').all()
                print(f"Total images found: {len(all_images)}")
                
                # Check for product images
                product_images = []
                for img in all_images[:20]:  # Check first 20 images
                    try:
                        src = await img.get_attribute('src')
                        alt = await img.get_attribute('alt')
                        if src and any(term in src.lower() for term in ['product', 'parfum', 'parfem']):
                            product_images.append({'src': src, 'alt': alt})
                    except:
                        continue
                
                print(f"Product-like images found: {len(product_images)}")
                for i, img in enumerate(product_images[:5]):
                    print(f"  {i+1}. {img['src'][:80]}... (alt: {img['alt']})")
                    
            except Exception as e:
                print(f"Error checking images: {e}")
            
            # Save page source for manual inspection
            try:
                html_content = await page.content()
                with open(os.path.join(screenshots_dir, "debug_page_source.html"), "w", encoding="utf-8") as f:
                    f.write(html_content)
                print(f"\nPage source saved to {screenshots_dir}/debug_page_source.html")
            except Exception as e:
                print(f"Could not save page source: {e}")
            
            # Wait for user to inspect
            print("\n=== MANUAL INSPECTION ===")
            print("Browser will stay open for 30 seconds for manual inspection...")
            print("Check the browser window to see what's actually on the page.")
            
            for i in range(30):
                if page.is_closed():
                    print("Browser was closed by user")
                    break
                await asyncio.sleep(1)
                if i % 5 == 0:
                    print(f"Waiting... {30-i} seconds remaining")
            
            return
    except Exception as e:
        print(f"Fatal error during debugging: {e}")
    finally:
        if browser:
            try:
                await browser.close()
            except:
                pass

async def main():
    try:
        print(f"Starting Zara page debugging at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await debug_zara_page()
        print("\nDebugging completed!")
    except Exception as e:
        print(f"An error occurred during debugging: {e}")
    
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
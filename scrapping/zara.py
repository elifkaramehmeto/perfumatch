from playwright.async_api import async_playwright
import asyncio
import json
import os
import re
import time
from datetime import datetime

async def scrape_zara_perfumes():
    # Create a directory for screenshots if it doesn't exist
    screenshots_dir = "zara_screenshots"
    if not os.path.exists(screenshots_dir):
        os.makedirs(screenshots_dir)
        print(f"Created directory: {screenshots_dir}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("Opening Zara perfumes page...")
        # 1. Navigate to category page
        await page.goto("https://www.zara.com/tr/en/woman-beauty-perfumes-l1415.html?v1=2419833", timeout=60000)
        
        print("Waiting for page to load...")
        # Wait with a fixed delay instead of networkidle
        await asyncio.sleep(5)
        
        try:
            # Accept cookies if dialog appears
            accept_button = page.locator('button:has-text("Accept All")')
            if await accept_button.count() > 0:
                await accept_button.click()
                print("Accepted cookies")
        except Exception as e:
            print(f"No cookie dialog or error handling it: {e}")
        
        # Scroll down to load all products (lazy loading)
        print("Scrolling to load all products...")
        previous_height = 0
        max_scroll_attempts = 30  # Increase max scroll attempts
        scroll_attempts = 0
        
        while scroll_attempts < max_scroll_attempts:
            # Scroll to bottom of page
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(3)  # Increase wait time to ensure content loads
            
            # Get the new height
            current_height = await page.evaluate("document.body.scrollHeight")
            
            # Take screenshot periodically to show progress
            if scroll_attempts % 5 == 0:
                try:
                    await page.screenshot(path=os.path.join(screenshots_dir, f"scroll_progress_{scroll_attempts}.png"))
                    print(f"Scroll progress screenshot saved (attempt {scroll_attempts})")
                except Exception as e:
                    print(f"Could not save scroll screenshot: {e}")
            
            # Check if we've reached the bottom (no new content loaded)
            if current_height == previous_height:
                print(f"Reached the bottom of the page after {scroll_attempts} scrolls")
                break
            
            previous_height = current_height
            scroll_attempts += 1
            print(f"Scroll attempt {scroll_attempts}/{max_scroll_attempts}, height: {current_height}")
            
        # Final screenshot after all scrolling
        try:
            await page.screenshot(path=os.path.join(screenshots_dir, "zara_category_page_full.png"))
            print("Full page screenshot saved")
        except Exception as e:
            print(f"Could not save screenshot: {e}")
        
        print("Looking for product cards...")
        
        # Analyze page structure after scrolling
        print("Analyzing page structure...")
        # Get all elements with hrefs
        try:
            html_content = await page.content()
            with open(os.path.join(screenshots_dir, "page_source.html"), "w", encoding="utf-8") as f:
                f.write(html_content)
            print("Saved page source for analysis")
        except Exception as e:
            print(f"Could not save page source: {e}")
            
        # Try different selectors
        selectors = [
            'a[href*="p2"]',  # Links with product IDs
            'a[data-productid]',
            '.product-link',
            '.product-grid-product a',
            'li.product-grid-product a',
            'article a',
            '.layout-products-wrapper a',
            'a[class*="product"]',
            '.media-grid__image-link',
            '.media-image a',
            '.product-grid__product a',
            'a[href*="perfume"]',
            'a[href*="edp"]',
            'a[href*="edt"]',
            '.item a'
        ]
        
        product_links = []
        
        # Try each selector
        for selector in selectors:
            try:
                print(f"Trying selector: {selector}")
                elements = await page.locator(selector).all()
                print(f"Found {len(elements)} elements with selector {selector}")
                
                # Get href attribute from each element
                temp_links = []
                for el in elements:
                    try:
                        href = await el.get_attribute('href')
                        if href:
                            # Check if it's a product link (contains p2 in the URL or has perfume/edt/edp in the URL)
                            if ('p2' in href and ('html' in href)) or any(term in href.lower() for term in ['perfume', 'edp', 'edt']):
                                temp_links.append(href)
                    except Exception as e:
                        print(f"Error getting href: {e}")
                        continue
                
                print(f"Found {len(temp_links)} product links with selector {selector}")
                if temp_links:
                    product_links.extend(temp_links)
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
                continue
        
        # If specific selectors fail, try a general approach
        if not product_links:
            print("Trying general link extraction...")
            try:
                # Use JavaScript to get all links
                all_links = await page.evaluate('''
                    () => {
                        const links = Array.from(document.querySelectorAll('a[href]'));
                        return links.map(a => a.href).filter(href => 
                            href.includes('p2') && 
                            href.includes('html') && 
                            (href.includes('perfume') || href.includes('edp') || href.includes('edt'))
                        );
                    }
                ''')
                
                product_links.extend(all_links)
                print(f"Found {len(all_links)} links via JavaScript extraction")
            except Exception as e:
                print(f"Error with JavaScript extraction: {e}")
        
        # Remove duplicates while preserving order
        unique_links = []
        for link in product_links:
            if link not in unique_links:
                unique_links.append(link)
        product_links = unique_links
        
        print(f"Total unique product links found: {len(product_links)}")
        if product_links:
            print("First few links:", product_links[:5])
            print("Last few links:", product_links[-5:])
            
            # Save links to a file for debugging
            try:
                with open(os.path.join(screenshots_dir, "product_links.txt"), "w", encoding="utf-8") as f:
                    for i, link in enumerate(product_links):
                        f.write(f"{i+1}. {link}\n")
                print("Saved product links to file")
            except Exception as e:
                print(f"Could not save product links: {e}")
        else:
            print("No product links found. Exiting.")
            await browser.close()
            return []
        
        perfumes = []

        # Visit each product detail page
        for i, link in enumerate(product_links):
            full_url = f"https://www.zara.com{link}" if not link.startswith('http') else link
            print(f"\nVisiting product {i+1}/{len(product_links)}: {full_url}")
            
            try:
                await page.goto(full_url, timeout=60000)
                # Use fixed delay instead of networkidle
                await asyncio.sleep(3)
                
                # Take screenshot to debug (only for first 5 products)
                if i < 5:
                    try:
                        await page.screenshot(path=os.path.join(screenshots_dir, f"zara_product_{i+1}.png"))
                        print(f"Screenshot saved")
                    except Exception as e:
                        print(f"Could not save screenshot: {e}")
                
                # Try different selectors for product name
                name = "Unknown"
                name_selectors = [
                    'h1.product-detail-info__header-name', 
                    '.product-name', 
                    '.product-info h1',
                    'h1[data-qa-heading]',
                    '.product-detail-info h1',
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
                price = "Unknown"
                price_selectors = [
                    'p.product-detail-unit-price', 
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
                description = ""
                desc_selectors = [
                    '.product-detail-description p',
                    '.product-info-text',
                    '.product-detail-info__description',
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
                
                # Extract scent notes from description using pattern matching
                notes = []
                notes_keywords = ["notes:", "note:", "accords:", "accord:", "fragrance notes:", "scent notes:"]
                
                if description:
                    desc_lower = description.lower()
                    for keyword in notes_keywords:
                        if keyword in desc_lower:
                            start_idx = desc_lower.find(keyword) + len(keyword)
                            end_idx = desc_lower.find(".", start_idx)
                            if end_idx == -1:  # If no period found, take until end of paragraph
                                end_idx = desc_lower.find("\n", start_idx)
                            
                            if end_idx != -1:
                                notes_text = description[start_idx:end_idx].strip()
                                # Split by commas, "and", or other separators
                                note_items = re.split(r',|\sand\s|;|\s-\s', notes_text)
                                notes = [note.strip() for note in note_items if note.strip()]
                                if notes:
                                    print(f"Extracted notes from description: {', '.join(notes)}")
                                    break
                
                # If no notes found in description, try specific notes selectors
                if not notes:
                    notes_selectors = [
                        'div.product-detail-composition span', 
                        '.product-composition span', 
                        '.product-details p',
                        '.product-detail-description p',
                        '.composition-content',
                        'div[class*="composition"]',
                        'div[class*="ingredient"]'
                    ]
                    
                    raw_notes_text = ""
                    for notes_selector in notes_selectors:
                        try:
                            if await page.locator(notes_selector).count() > 0:
                                note_spans = await page.query_selector_all(notes_selector)
                                if note_spans:
                                    note_texts = []
                                    for span in note_spans:
                                        note_texts.append(await span.inner_text())
                                    raw_notes_text = " ".join(note_texts).strip()
                                    if raw_notes_text:
                                        print(f"Found raw notes text: {raw_notes_text[:50]}...")
                                        break
                        except Exception as e:
                            continue
                    
                    # Try to extract actual fragrance notes from composition text if found
                    if raw_notes_text:
                        # Common fragrance ingredients to look for
                        fragrance_ingredients = [
                            "vanilla", "rose", "jasmine", "sandalwood", "amber", "musk", "citrus", 
                            "bergamot", "lavender", "vetiver", "patchouli", "cedar", "oud", "orange blossom",
                            "neroli", "ylang", "lily", "violet", "iris", "cinnamon", "cardamom", "pepper",
                            "leather", "tobacco", "coffee", "chocolate", "caramel", "coconut", "peach",
                            "apple", "pear", "strawberry", "raspberry", "blackberry", "cherry", "plum",
                            "almond", "hazelnut", "pine", "fig", "mint", "basil", "rosemary", "thyme",
                            "mandarin", "lemon", "lime", "grapefruit", "orange", "watermelon"
                        ]
                        
                        for ingredient in fragrance_ingredients:
                            if ingredient.lower() in raw_notes_text.lower():
                                notes.append(ingredient.capitalize())
                        
                        if notes:
                            print(f"Extracted fragrance notes: {', '.join(notes)}")
                        else:
                            # If no specific notes found, use the raw text
                            notes = [raw_notes_text[:100] + "..." if len(raw_notes_text) > 100 else raw_notes_text]
                
                # Get image URL if available
                image_url = ""
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

                # Compile all data
                perfume_data = {
                    "name": name,
                    "price": price,
                    "description": description,
                    "notes": notes,
                    "image_url": image_url,
                    "product_url": full_url,
                    "brand": "Zara",
                    "scrape_date": datetime.now().strftime("%Y-%m-%d")
                }
                
                perfumes.append(perfume_data)
                print(f"Added product {i+1} to results")
                
                # Sleep briefly between requests to avoid rate limiting
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error processing product {i+1}: {e}")
                continue

        await browser.close()
        return perfumes

async def main():
    try:
        print(f"Starting Zara perfume scraping at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        result = await scrape_zara_perfumes()
        print("\nScraping completed!")
        print(f"Total perfumes found: {len(result)}")
        
        if result:
            # Create output filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"zara_perfumes_{timestamp}.json"
            
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
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    
    input("Press Enter to continue...")

# Usage
if __name__ == "__main__":
    asyncio.run(main())

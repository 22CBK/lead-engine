import os
import json
import csv
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import status_tracker

def get_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)

def scrape_query(page, query):
    print(f"Scraping Google Maps for: {query}")
    page.goto(f"https://www.google.com/maps/search/{query.replace(' ', '+')}")
    time.sleep(5)  # Wait for initial load
    
    # Accept cookies if the popup appears (EU etc.)
    try:
        page.locator('button:has-text("Accept all")').click(timeout=3000)
    except:
        pass

    results = []
    
    # We will try to extract some results. Google Maps DOM is complex and dynamic.
    # We use a broader approach: find elements with 'role="article"' or links that look like business listings.
    
    try:
        # Wait for the feed to load
        page.wait_for_selector('a[href*="/maps/place/"]', timeout=10000)
        
        # Scroll the feed a bit to load more
        for _ in range(3):
            page.mouse.wheel(0, 1000)
            time.sleep(2)
            
        listings = page.locator('a[href*="/maps/place/"]').all()
        
        # To avoid being blocked, we just take the top few easily visible elements' attributes
        # Since clicking each takes a long time, we parse their aria-labels if available
        # aria-label usually contains "Name, Category, Rating, etc."
        
        import re
        for listing in listings[:15]:  # Limit to top 15 per query to avoid long runs
            label = listing.get_attribute('aria-label')
            if label:
                name = label
                rating = "0"
                reviews = 0
                
                try:
                    text = listing.inner_text()
                    # Look for pattern like 4.2 (15) or 4.2(1,500)
                    rating_match = re.search(r'(\d\.\d)\s*\(([\d,]+)\)', text)
                    if rating_match:
                        rating = rating_match.group(1)
                        reviews = int(rating_match.group(2).replace(',', ''))
                except Exception:
                    pass
                    
                category = query.split(' in ')[0] if ' in ' in query else "business"
                area = query.split(' in ')[-1] if ' in ' in query else "Chennai"
                
                results.append({
                    "business_name": name,
                    "category": category,
                    "rating": rating,
                    "reviews": reviews,
                    "area": area,
                    "website": "",
                    "phone": ""
                })
    except Exception as e:
        print(f"Error scraping {query}: {e}")
        
    return results

def run_scraper():
    config = get_config()
    queries = config.get("search_queries", [])
    
    all_results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        for i, query in enumerate(queries):
            status_tracker.update_status("running", f"Scraping category: {query.split(' in ')[0]} ({i+1}/{len(queries)})", 10 + int((i/len(queries))*30))
            results = scrape_query(page, query)
            all_results.extend(results)
            time.sleep(2) # be nice
            
        browser.close()
        
    if all_results:
        date_str = datetime.now().strftime("%Y-%m-%d")
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"maps_{date_str}.csv")
        
        keys = ["business_name", "category", "rating", "reviews", "area", "website", "phone"]
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_results)
        print(f"Scraped {len(all_results)} leads to {output_file}")
    else:
        print("No results found.")

if __name__ == "__main__":
    run_scraper()

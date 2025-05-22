import random
import asyncio
from apify import Actor
from playwright.async_api import async_playwright

USER_AGENTS = [
    # Desktop Chrome user agents
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15"
    # Add more if needed
]

async def scrape_yellow_pages(search_term, location, max_pages=1):
    results = []
    base_url = "https://www.yellowpages.com"
    search_url = f"{base_url}/search?search_terms={search_term}&geo_location_terms={location}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            locale="en-US"
        )
        page = await context.new_page()

        for page_num in range(1, max_pages + 1):
            url = f"{search_url}&page={page_num}"
            print(f"Visiting: {url}")
            await page.goto(url, timeout=60000)
            await page.wait_for_selector('.search-results', timeout=10000)

            listings = await page.query_selector_all(".result")
            for listing in listings:
                name = await listing.query_selector_eval(".business-name span", "el => el.innerText", strict=False)
                phone = await listing.query_selector_eval(".phones", "el => el.innerText", strict=False)
                address = await listing.query_selector_eval(".street-address", "el => el.innerText", strict=False)
                locality = await listing.query_selector_eval(".locality", "el => el.innerText", strict=False)

                results.append({
                    "name": name.strip() if name else None,
                    "phone": phone.strip() if phone else None,
                    "address": address.strip() if address else None,
                    "locality": locality.strip() if locality else None
                })

            await asyncio.sleep(random.uniform(2, 5))  # Mimic human behavior

        await browser.close()
    return results

async def main():
    async with Actor:
        input_data = await Actor.get_input() or {}
        search_term = input_data.get("searchTerm", "restaurants")
        location = input_data.get("location", "New York, NY")
        max_pages = input_data.get("maxPages", 1)

        Actor.log.info(f"Scraping Yellow Pages for '{search_term}' in '{location}'")

        results = await scrape_yellow_pages(search_term, location, max_pages)

        await Actor.push_data(results)

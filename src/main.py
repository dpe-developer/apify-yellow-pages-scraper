import random
import asyncio
from apify import Actor
from playwright.async_api import async_playwright, BrowserContext

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1"
]

async def create_stealth_context(browser, proxy_url: str) -> BrowserContext:
    user_agent = random.choice(USER_AGENTS)
    viewport = {"width": 1280, "height": 800}

    context = await browser.new_context(
        user_agent=user_agent,
        viewport=viewport,
        locale="en-US",
        timezone_id="America/New_York",
        proxy={"server": proxy_url} if proxy_url else None,
        java_script_enabled=True,
        bypass_csp=True,
        device_scale_factor=1,
        is_mobile=False,
        has_touch=False,
    )

    await context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return context

async def scrape_yellow_pages(search_term, location, max_pages=1, proxy_url=None):

    results = []
    base_url = "https://www.yellowpages.com"
    search_url = f"{base_url}/search?search_terms={search_term}&geo_location_terms={location}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)  # Set to False for visual debug
        for page_num in range(1, max_pages + 1):
            context = await create_stealth_context(browser, proxy_url)
            page = await context.new_page()

            url = f"{search_url}&page={page_num}"
            try:
                Actor.log.info(f"Navigating to: {url}")
                await page.goto(url, timeout=60000)
                await page.wait_for_selector('.search-results .info', timeout=10000)

                if await page.query_selector("iframe[src*='captcha']") or "captcha" in await page.content():
                    Actor.log.warning(f"CAPTCHA detected on page {page_num}, skipping...")
                    await context.close()
                    break

                listings = await page.query_selector_all(".search-results .info")
                Actor.log.info(f"Found {len(listings)} listings on page {page_num}")

                for listing in listings:
                    try:
                        name_el = await listing.query_selector(".business-name span")
                        phone_el = await listing.query_selector(".phones")
                        addr_el = await listing.query_selector(".street-address")
                        loc_el = await listing.query_selector(".locality")

                        results.append({
                            "name": (await name_el.text_content()).strip() if name_el else None,
                            "phone": (await phone_el.text_content()).strip() if phone_el else None,
                            "address": (await addr_el.text_content()).strip() if addr_el else None,
                            "locality": (await loc_el.text_content()).strip() if loc_el else None,
                        })
                    except Exception as listing_error:
                        Actor.log.warning(f"Failed to extract a listing: {listing_error}")

                await asyncio.sleep(random.uniform(2, 10))
            except Exception as e:
                Actor.log.error(f"Error scraping page {page_num}: {e}")
            finally:
                await context.close()

        await browser.close()
    return results

async def main():

    Actor.log.info(f'Program Start')

    async with Actor:
        input_data = await Actor.get_input() or {}
        search_term = input_data.get("searchTerm", "restaurants")
        location = input_data.get("location", "New York, NY")
        max_pages = input_data.get("maxPages", 1)

        proxy_config = await Actor.create_proxy_configuration()
        proxy_url = await proxy_config.new_url()

        Actor.log.info(f"Scraping '{search_term}' in '{location}' for {max_pages} pages with proxy: {proxy_url}")
        results = await scrape_yellow_pages(search_term, location, max_pages, proxy_url)

        Actor.log.info(f"Scraping completed. Total records: {len(results)}")
        await Actor.push_data(results)

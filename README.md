# Yellow Pages Scraper

This Apify actor scrapes business listings from Yellow Pages using Playwright with stealth mode, proxy rotation, and user-agent rotation to avoid IP blocking.

## Features

- Uses Playwright in headless Chromium mode  
- Rotates user agents for better anonymity  
- Uses Apify Proxy Residential IPs  
- Detects and avoids CAPTCHA pages  
- Configurable search term, location, and number of pages  
- Outputs structured JSON data with business name, phone, and address

## Input

The actor expects a JSON input with the following fields:

```json
{
  "searchTerm": "restaurants",
  "location": "New York, NY",
  "maxPages": 1
}

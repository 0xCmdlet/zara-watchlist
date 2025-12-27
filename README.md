# Zara Product Availability Monitor

A simple script to monitor Zara product availability using Playwright.

## What It Does

- Opens Zara product pages in a browser
- Checks if products are sold out (AUSVERKAUFT) or available for purchase
- Saves product state to track changes over time
- Stores raw HTML for debugging

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Add products to monitor in `src/products.py`

3. Run the script:
```bash
python src/main.py
```

## How It Works

1. Loads each product URL from `src/products.py`
2. Opens the page with Playwright (visible browser)
3. Accepts cookie banner
4. Waits for product details to load
5. Checks for availability status:
   - Sold out: "AUSVERKAUFT" button present
   - Available: "Hinzufügen" (add to cart) button present
6. Saves state to `data/state.json`
7. Saves raw HTML to `data/raw/`

## Files

- `src/main.py` - Main script
- `src/zara_client.py` - Browser automation logic
- `src/products.py` - Product configuration
- `src/state_store.py` - State persistence
- `src/zara_parser.py` - HTML parsing (placeholder)
- `src/config.py` - Settings
- `data/state.json` - Last known availability state
- `data/raw/` - Raw HTML files
- `data/debug/` - Debug HTML snapshots

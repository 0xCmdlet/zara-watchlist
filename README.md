# Zara Product Availability Monitor

A simple script to monitor Zara product availability using Playwright.

## What It Does

- Opens Zara product pages in a browser
- Checks if products are sold out (AUSVERKAUFT) or available for purchase
- Extracts available sizes and checks if any of your desired sizes are in stock
- Saves product state to track changes over time
- Sends email notifications when products become available in your desired sizes
- Stores raw HTML for debugging

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
playwright install chromium
```

2. Create a `.env` file in the project root with your email settings:
```bash
cp .env.example .env
# Edit .env with your actual credentials
```

Example `.env` content:
```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=465
EMAIL_USERNAME=your-email@example.com
EMAIL_PASSWORD=your-password
TO_EMAIL=notification-email@example.com
```

3. Add products to monitor in `src/products.py`:
```python
PRODUCTS = [
    {
        "id": "p08679425",
        "name": "PRODUCT NAME",
        "url": "https://www.zara.com/...",
        "sizes": ["M", "L"]  # Desired sizes - can specify multiple!
    },
    {
        "id": "p12345678",
        "name": "ANOTHER PRODUCT",
        "url": "https://www.zara.com/...",
        "sizes": ["XS"]  # Or just one size
    }
]
```

4. Run the script:
```bash
python src/main.py
```

## Running on VPS (Headless)

On a VPS without a display server, use xvfb-run:

```bash
# Install xvfb
sudo apt-get update && sudo apt-get install -y xvfb

# Run the script
xvfb-run python3 src/main.py
```

## Automated Monitoring with Cron

To check every 30 minutes:

```bash
# Create logs directory
mkdir -p logs

# Edit crontab
crontab -e

# Add this line (adjust paths):
*/30 * * * * cd /path/to/zara && xvfb-run /path/to/.venv/bin/python3 /path/to/src/main.py >> /path/to/logs/cron.log 2>&1
```

## How It Works

1. Loads each product URL from `src/products.py`
2. Opens the page with Playwright (browser automation)
3. Accepts cookie banner
4. Waits for product details to load
5. Checks for availability status:
   - Sold out: "AUSVERKAUFT" button present
   - Available: "Hinzufügen" (add to cart) button present
6. Clicks "Hinzufügen" button to reveal size selector
7. Extracts all available sizes
8. Checks if ANY of your desired sizes are in stock
9. Compares with previous status from `data/state.json`
10. Sends email notification ONLY if:
    - Product became available (status changed)
    - AND at least one of your desired sizes is in stock
11. Saves updated state to `data/state.json`
12. Saves raw HTML to `data/raw/`

## Files

- `src/main.py` - Main script orchestration
- `src/zara_client.py` - Browser automation and availability checking
- `src/email_client.py` - Email notification sender
- `src/products.py` - Product configuration
- `src/state_store.py` - State persistence
- `.env` - Email credentials (not committed to git)
- `.env.example` - Template for environment variables
- `data/state.json` - Last known availability state
- `data/raw/` - Raw HTML files for debugging

from typing import Dict
from playwright.sync_api import sync_playwright


def fetch_product_page(product: Dict) -> str:
    """
    Opens a Zara product page, accepts cookies, checks if sold out.
    Returns the HTML.
    """
    url = product["url"]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

        context = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080},
            locale='de-DE',
            timezone_id='Europe/Berlin',
            extra_http_headers={
                'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Referer': 'https://www.zara.com/',
            }
        )

        page = context.new_page()

        # Add JavaScript to mask automation
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        # 1) Navigate to the page and wait for it to load
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_timeout(2000)

        # 2) Accept cookie banner
        try:
            page.wait_for_selector("#onetrust-accept-btn-handler", timeout=5000)
            page.click("#onetrust-accept-btn-handler")
            print("  Cookies accepted")
        except Exception:
            print("  No cookie banner found")

        # DEBUG: Save HTML after cookies
        from pathlib import Path
        debug_dir = Path(__file__).resolve().parent.parent / "data" / "debug"
        debug_dir.mkdir(parents=True, exist_ok=True)
        debug_file = debug_dir / f"{product['id']}_after_cookies.html"
        debug_file.write_text(page.content(), encoding="utf-8")
        print(f"  Debug HTML saved to {debug_file}")

        # 3) Wait 2 seconds
        page.wait_for_timeout(2000)

        # 4) Wait for the similar products button to render
        try:
            page.wait_for_selector("button.product-detail-show-similar-products", timeout=5000)
            print("  Similar products button found")
        except Exception:
            print("  Similar products button not found")

        # 5) Check for AUSVERKAUFT span
        ausverkauft = page.query_selector('span.zds-button__second-line:has-text("AUSVERKAUFT")')
        if ausverkauft:
            print("  ⚠️  Product is SOLD OUT (AUSVERKAUFT)")
        else:
            # Check for add-to-cart button instead
            add_to_cart = page.query_selector('button[data-qa-action="add-to-cart"]')
            if add_to_cart:
                print("  ✓ Product is AVAILABLE (Hinzufügen button found)")
            else:
                print("  ❓ Could not determine availability")

        # 6) Return HTML
        html = page.content()
        browser.close()
        return html

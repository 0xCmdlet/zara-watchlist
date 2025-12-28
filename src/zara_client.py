from typing import Dict
from playwright.sync_api import sync_playwright


def fetch_product_page(product: Dict) -> tuple[str, str, list[str]]:
    """
    Opens a Zara product page, accepts cookies, checks if sold out.
    Returns (html, availability_status, available_sizes) where:
    - status is 'available', 'sold_out', or 'unknown'
    - available_sizes is a list of size strings (e.g., ['XS', 'S', 'M', 'L'])
    """
    url = product["url"]

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-extensions',
                '--disable-plugins',
                '--single-process',
                '--disable-setuid-sandbox'
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

        # 3) Dismiss geolocation modal if present
        modal_dismissed = False
        try:
            # Try clicking "Stay in Germany" button (preferred)
            stay_button = page.wait_for_selector('button[data-qa-action="stay-in-store"]', timeout=3000)
            if stay_button:
                stay_button.click()
                page.wait_for_timeout(500)  # Wait for modal to close
                modal_dismissed = True
                print("  Geolocation modal dismissed (stayed on German site)")
        except Exception:
            pass

        if not modal_dismissed:
            try:
                # Fallback: Try close button (X icon)
                close_button = page.wait_for_selector('button.zds-dialog-close-button', timeout=2000)
                if close_button:
                    close_button.click()
                    page.wait_for_timeout(500)
                    print("  Geolocation modal closed")
            except Exception:
                print("  No geolocation modal found")

        # 4) Wait 2 seconds
        page.wait_for_timeout(2000)

        # 5) Wait for the similar products button to render
        try:
            page.wait_for_selector("button.product-detail-show-similar-products", timeout=5000)
            print("  Similar products button found")
        except Exception:
            print("  Similar products button not found")

        # 6) Check for add-to-cart button and click it to reveal size selector
        available_sizes = []
        add_to_cart = page.query_selector('button[data-qa-action="add-to-cart"]')

        if add_to_cart:
            print("  Clicking add-to-cart button to reveal size selector...")
            try:
                add_to_cart.click(timeout=10000)  # 10 second timeout for click
            except Exception as e:
                print(f"  Failed to click add-to-cart button: {e}")

                # Save HTML for debugging when click fails
                from pathlib import Path
                error_dir = Path(__file__).resolve().parent.parent / "data" / "error_html"
                error_dir.mkdir(parents=True, exist_ok=True)
                error_file = error_dir / f"{product['id']}_click_failed.html"
                error_file.write_text(page.content(), encoding="utf-8")
                print(f"  Saved error HTML to {error_file}")

                add_to_cart = None  # Mark as failed

        if add_to_cart:
            # Wait for size selector to appear
            try:
                page.wait_for_selector('ul.size-selector-sizes', timeout=3000)
                print("  Size selector revealed")

                # Extract available sizes
                size_buttons = page.query_selector_all('button.size-selector-sizes-size__button')
                for button in size_buttons:
                    action = button.get_attribute('data-qa-action')
                    if action in ['size-in-stock', 'size-low-on-stock']:
                        label_div = button.query_selector('div[data-qa-qualifier="size-selector-sizes-size-label"]')
                        if label_div:
                            size = label_div.text_content().strip()
                            available_sizes.append(size)

                print(f"  Available sizes: {', '.join(available_sizes) if available_sizes else 'None'}")
            except Exception:
                print("  Size selector did not appear")
        else:
            print("  No add-to-cart button found")

        # 7) Determine overall availability
        availability = "unknown"
        ausverkauft = page.query_selector('span.zds-button__second-line:has-text("AUSVERKAUFT")')
        if ausverkauft:
            availability = "sold_out"
            print("  Product is SOLD OUT (AUSVERKAUFT)")
        elif add_to_cart:
            availability = "available"
            print("  Product is AVAILABLE")
        else:
            print("  Could not determine availability")

        # 8) Return HTML, availability, and available sizes
        html = page.content()
        browser.close()
        return html, availability, available_sizes

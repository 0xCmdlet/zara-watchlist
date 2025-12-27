# src/main.py

from products import PRODUCTS
from zara_client import fetch_product_page
from state_store import load_state, save_state
from email_client import send_status_change_email
from pathlib import Path


def main():
    state = load_state()
    updated_state = {}
    newly_available_products = []

    for product in PRODUCTS:
        pid = product["id"]
        name = product["name"]
        url = product["url"]

        print(f"Checking product: {name} ({pid})")
        print(f"URL: {url}")

        try:
            html, availability, available_sizes = fetch_product_page(product)

            # --- SAVE RAW HTML ---
            raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
            raw_dir.mkdir(parents=True, exist_ok=True)

            raw_file = raw_dir / f"{pid}.html"
            raw_file.write_text(html, encoding="utf-8")

            print(f"  Saved raw HTML to {raw_file}")

            prev = state.get(pid)
            print(f"  Previous status: {prev}")
            print(f"  Current status:  {availability}")

            # Check if desired size is available
            desired_size = product.get("size")
            size_match = desired_size and desired_size in available_sizes

            if desired_size:
                if size_match:
                    print(f"  Desired size {desired_size} is AVAILABLE!")
                else:
                    print(f"  Desired size {desired_size} is NOT available")

            # Check if status changed to available AND desired size is in stock
            if availability == "available" and prev != "available" and size_match:
                print(f"  STATUS CHANGE: {name} (Size {desired_size}) is now AVAILABLE!")
                send_status_change_email(product, prev or "unknown", availability)
                newly_available_products.append(product)

            updated_state[pid] = availability

        except RuntimeError as e:
            print(f"  ERROR: {e}")
            # keep previous state if exists
            updated_state[pid] = state.get(pid, "unknown")
            continue

    save_state(updated_state)

    # Summary
    print(f"\n{'='*60}")
    print(f"Check complete. {len(newly_available_products)} product(s) became available.")
    if newly_available_products:
        for p in newly_available_products:
            size = p.get('size', 'N/A')
            print(f"  - {p['name']} (Size: {size})")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

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

            # Check if any desired size is available
            desired_sizes = product.get("sizes", [])
            if not desired_sizes:
                # Backwards compatibility: check for old "size" field
                old_size = product.get("size")
                if old_size:
                    desired_sizes = [old_size]

            # Find which desired sizes are in stock
            matching_sizes = [size for size in desired_sizes if size in available_sizes]

            if desired_sizes:
                if matching_sizes:
                    print(f"  Desired size(s) {', '.join(matching_sizes)} AVAILABLE!")
                else:
                    print(f"  Desired size(s) {', '.join(desired_sizes)} NOT available")

            # Check if status changed to available AND at least one desired size is in stock
            if availability == "available" and prev != "available" and matching_sizes:
                print(f"  STATUS CHANGE: {name} (Sizes: {', '.join(matching_sizes)}) is now AVAILABLE!")
                # Store matching sizes in product for email
                product['matching_sizes'] = matching_sizes
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
            matching_sizes = p.get('matching_sizes', [])
            if matching_sizes:
                size_text = ", ".join(matching_sizes)
            else:
                size_text = p.get('size', 'N/A')
            print(f"  - {p['name']} (Size: {size_text})")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()

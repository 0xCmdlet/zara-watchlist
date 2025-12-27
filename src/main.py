# src/main.py

from products import PRODUCTS
from zara_client import fetch_product_page
from zara_parser import extract_availability
from state_store import load_state, save_state
from pathlib import Path



def main():
    state = load_state()
    updated_state = {}

    for product in PRODUCTS:
        pid = product["id"]
        name = product["name"]
        url = product["url"]

        print(f"Checking product: {name} ({pid})")
        print(f"URL: {url}")

        try:
            html = fetch_product_page(product)

            # --- SAVE RAW HTML ---
            raw_dir = Path(__file__).resolve().parent.parent / "data" / "raw"
            raw_dir.mkdir(parents=True, exist_ok=True)

            raw_file = raw_dir / f"{pid}.html"
            raw_file.write_text(html, encoding="utf-8")

            print(f"  Saved raw HTML to {raw_file}")

        except RuntimeError as e:
            print(f"  ERROR: {e}")
            # keep previous state if exists
            updated_state[pid] = state.get(pid, "unknown")
            continue

        availability = extract_availability(html, product)

        prev = state.get(pid)
        print(f"  Previous status: {prev}")
        print(f"  Current status:  {availability}")

        # later we'll trigger notifications when prev != availability
        updated_state[pid] = availability

    save_state(updated_state)


if __name__ == "__main__":
    main()

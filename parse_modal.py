#!/usr/bin/env python3
"""
Script to extract geolocation modal from HTML file
"""

from bs4 import BeautifulSoup
import sys

def extract_modal(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Try to find the geolocation modal
    modal_selectors = [
        {'class': 'geolocation-modal'},
        {'class': 'zds-modal'},
        {'role': 'dialog'},
        {'class': 'zds-dialog'},
    ]

    print("=" * 80)
    print("SEARCHING FOR GEOLOCATION MODAL")
    print("=" * 80)

    for selector in modal_selectors:
        modals = soup.find_all('div', selector)
        if modals:
            print(f"\nFound {len(modals)} element(s) with selector: {selector}\n")

            for idx, modal in enumerate(modals):
                print(f"\n--- Modal #{idx + 1} ---")
                print(modal.prettify()[:2000])  # First 2000 chars
                print("\n... (truncated)\n")

                # Look for buttons in this modal
                buttons = modal.find_all('button')
                if buttons:
                    print(f"Found {len(buttons)} button(s) in this modal:")
                    for btn_idx, btn in enumerate(buttons):
                        print(f"\n  Button #{btn_idx + 1}:")
                        print(f"    Classes: {btn.get('class', [])}")
                        print(f"    Aria-label: {btn.get('aria-label', 'N/A')}")
                        print(f"    Data attributes: {[k for k in btn.attrs.keys() if k.startswith('data-')]}")
                        print(f"    Text: {btn.get_text(strip=True)[:100]}")
                        print(f"    HTML: {str(btn)[:200]}")

    # Also search for backdrop (the overlay that blocks clicks)
    print("\n" + "=" * 80)
    print("SEARCHING FOR BACKDROP")
    print("=" * 80)

    backdrops = soup.find_all('div', {'class': lambda x: x and 'backdrop' in str(x).lower()})
    if backdrops:
        print(f"\nFound {len(backdrops)} backdrop(s):")
        for idx, backdrop in enumerate(backdrops):
            print(f"\nBackdrop #{idx + 1}:")
            print(f"  Classes: {backdrop.get('class', [])}")
            print(f"  Aria-hidden: {backdrop.get('aria-hidden', 'N/A')}")
            print(f"  HTML: {str(backdrop)[:500]}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_modal.py <html_file>")
        sys.exit(1)

    extract_modal(sys.argv[1])

# src/zara_parser.py

from typing import Dict

# For now we'll just pretend everything is "unknown"
# We'll implement real parsing later.

def extract_availability(html: str, product: Dict) -> str:
    """
    Given the raw HTML and product info, return availability status.

    For now it always returns 'unknown' as a placeholder.

    Later we'll return: 'in_stock', 'out_of_stock', or 'unknown'.
    """
    # TODO: implement actual parsing logic
    return "unknown"

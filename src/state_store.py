# src/state_store.py

import json
from pathlib import Path
from typing import Dict

STATE_FILE = Path(__file__).resolve().parent.parent / "data" / "state.json"


def load_state() -> Dict[str, str]:
    """
    Load last known availability state for each product id.
    Returns a dict: {product_id: availability}
    """
    if not STATE_FILE.exists():
        return {}
    try:
        with STATE_FILE.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # Corrupt file, start clean
        return {}


def save_state(state: Dict[str, str]) -> None:
    """
    Save availability state to JSON file.
    """
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

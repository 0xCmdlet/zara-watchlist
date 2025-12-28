import smtplib
import os
from email.message import EmailMessage
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
USERNAME = os.getenv("EMAIL_USERNAME")
PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL_RAW = os.getenv("TO_EMAIL", "")
# Support multiple recipients: comma-separated emails
TO_EMAILS = [email.strip() for email in TO_EMAIL_RAW.split(",") if email.strip()]


def send_availability_email(available_products: List[Dict]) -> None:
    """
    Send email notification for available products.

    :param available_products: List of product dicts with 'name', 'url', 'size', 'id'
    """
    if not available_products:
        return

    # Build email content
    subject = f"Zara Alert: {len(available_products)} Product(s) Available!"

    body_lines = ["The following products are now available:\n"]

    for product in available_products:
        name = product.get("name", "Unknown")
        size = product.get("size", "N/A")
        url = product.get("url", "")
        product_id = product.get("id", "")

        body_lines.append(f"Product: {name}")
        body_lines.append(f"Size: {size}")
        body_lines.append(f"Product ID: {product_id}")
        body_lines.append(f"URL: {url}")
        body_lines.append("-" * 60)
        body_lines.append("")

    body_lines.append("\nCheck these products before they sell out!")

    body = "\n".join(body_lines)

    # Create and send email
    msg = EmailMessage()
    msg["From"] = USERNAME
    msg["To"] = ", ".join(TO_EMAILS)
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(USERNAME, PASSWORD)
            smtp.send_message(msg)
        print(f"\nEmail notification sent to {len(TO_EMAILS)} recipient(s): {', '.join(TO_EMAILS)}")
    except Exception as e:
        print(f"\nFailed to send email: {e}")


def send_status_change_email(product: Dict, old_status: str, new_status: str) -> None:
    """
    Send email when a product status changes.

    :param product: Product dict
    :param old_status: Previous availability status
    :param new_status: Current availability status
    """
    name = product.get("name", "Unknown")

    # Check for matching sizes (set in main.py)
    matching_sizes = product.get("matching_sizes", [])
    if matching_sizes:
        size_text = ", ".join(matching_sizes)
    else:
        # Backwards compatibility
        size_text = product.get("size", "N/A")

    url = product.get("url", "")

    subject = f"Zara Alert: {name} (Size {size_text}) Available!"

    body = f"""Your desired product is now AVAILABLE!

Product: {name}
Available Size(s): {size_text}
URL: {url}

Previous Status: {old_status}
Current Status: {new_status}

BUY NOW before it sells out:
{url}
"""

    msg = EmailMessage()
    msg["From"] = USERNAME
    msg["To"] = ", ".join(TO_EMAILS)
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.login(USERNAME, PASSWORD)
            smtp.send_message(msg)
        print(f"\nStatus change email sent to {len(TO_EMAILS)} recipient(s): {', '.join(TO_EMAILS)}")
    except Exception as e:
        print(f"\nFailed to send status change email: {e}")

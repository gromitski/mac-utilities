#!/usr/bin/env python3
"""
URL Tracker & Telemetry Stripper
---------------------------------
Cleans tracking parameters (utm_*, fbclid, gclid, si, ref, etc.) from copied URLs
and replaces the macOS clipboard with the clean link.
"""

import os
import re
import subprocess
import sys
import urllib.parse

# Comprehensive tracking parameter blocklist
TRACKING_PARAMS = {
    # Google & Analytics / Ads
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "utm_id", "utm_name", "utm_reader", "utm_viz_id", "gclid", "gclsrc",
    "dclid", "wbraid", "gbraid", "_ga", "_gl",

    # Meta / Facebook / Instagram
    "fbclid", "igshid", "hrc", "fref",

    # Twitter / X
    "twclid", "ref_src", "ref_url",

    # Microsoft / Bing / LinkedIn
    "msclkid", "li_fat_id",

    # TikTok / Video platforms
    "tt_medium", "tt_content", "is_from_webapp", "sender_device", "sender_web_id",

    # YouTube
    "si", "feature", "pp",

    # Spotify
    "si", "nd",

    # Amazon tracking clutter
    "ref", "ref_", "tag", "keywords", "qid", "sr", "crid", "sprefix",
    "dib", "dib_tag", "pd_rd_r", "pd_rd_w", "pd_rd_wg", "_encoding",

    # Email & Marketing Platforms (HubSpot, Mailchimp, Marketo, Substack)
    "mkt_tok", "_hsenc", "_hsmi", "mc_eid", "mc_cid", "vero_id", "vero_conv",
    "sc_customer", "yclid", "rb_clickid",
}


def get_clipboard() -> str:
    """Read plain text from macOS clipboard."""
    try:
        res = subprocess.run(["pbpaste"], capture_output=True, text=True)
        return res.stdout.strip()
    except Exception:
        return ""


def set_clipboard(text: str):
    """Write text to macOS clipboard."""
    try:
        p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True)
        p.communicate(input=text)
    except Exception as e:
        print(f"Error copying to clipboard: {e}", file=sys.stderr)


def clean_single_url(raw_url: str) -> str:
    """Clean tracking parameters from a single URL string."""
    raw_url = raw_url.strip()
    if not (raw_url.startswith("http://") or raw_url.startswith("https://")):
        return raw_url

    parsed = urllib.parse.urlsplit(raw_url)
    query_params = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)

    # Filter out parameters in the blocklist or starting with utm_
    cleaned_params = [
        (k, v) for (k, v) in query_params
        if k.lower() not in TRACKING_PARAMS and not k.lower().startswith("utm_")
    ]

    # Special handling for clean Amazon product links (canonical /dp/ASIN)
    path = parsed.path
    if "amazon." in parsed.netloc.lower():
        match = re.search(r"/(?:dp|gp/product)/([A-Z0-9]{10})", path)
        if match:
            asin = match.group(1)
            path = f"/dp/{asin}"

    # Reconstruct cleaned query string
    cleaned_query = urllib.parse.urlencode(cleaned_params)

    clean_url = urllib.parse.urlunsplit((
        parsed.scheme,
        parsed.netloc,
        path,
        cleaned_query,
        parsed.fragment,
    ))

    # Clean trailing ? if query is empty
    return clean_url.rstrip("?")


def clean_clipboard_url(input_url: str = None) -> tuple:
    """
    Clean URL from argument or clipboard.
    Returns (clean_url, original_url, was_modified).
    """
    original = input_url if input_url else get_clipboard()
    if not original:
        return "", "", False

    # Extract URL if surrounded by other text
    url_match = re.search(r"https?://[^\s]+", original)
    target_url = url_match.group(0) if url_match else original

    cleaned = clean_single_url(target_url)
    was_modified = (cleaned != target_url)

    if not input_url and was_modified:
        set_clipboard(cleaned)

    return cleaned, target_url, was_modified


def run_clean_url(input_url: str = None, notify: bool = False):
    cleaned, original, was_modified = clean_clipboard_url(input_url)

    if not original:
        print("\n⚠️ Clipboard is empty or contains no URL.\n")
        return

    print("\n🔗 \033[1mURL Tracker Cleaner\033[0m")
    print("──────────────────────────────────────────────────────────────────────────")
    print(f"\033[90mOriginal:\033[0m {original}")
    print(f"\033[32mCleaned :\033[0m \033[1m{cleaned}\033[0m")
    print("──────────────────────────────────────────────────────────────────────────")

    if was_modified:
        print("✓ \033[32mTracking parameters removed and clean URL copied to clipboard!\033[0m\n")
        if notify:
            from clean import send_macos_notification
            send_macos_notification("URL Cleaned", "Copied to clipboard", cleaned)
    else:
        print("✓ \033[90mURL was already clean (copied to clipboard).\033[0m\n")
        if notify:
            from clean import send_macos_notification
            send_macos_notification("URL Already Clean", "Copied to clipboard", cleaned)


if __name__ == "__main__":
    url_arg = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else None
    notify_flag = "--notify" in sys.argv
    run_clean_url(url_arg, notify=notify_flag)

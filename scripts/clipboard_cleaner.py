#!/usr/bin/env python3
"""
Clipboard Cleaner Utility for macOS
-------------------------------------
Provides instant privacy flushing, rich-text formatting sanitization,
and safe metadata inspection for the macOS clipboard.
"""

import argparse
import re
import subprocess
import sys


def get_clipboard_text() -> str:
    """Read the current clipboard plain-text contents."""
    try:
        res = subprocess.run(["pbpaste"], capture_output=True, text=True, check=True)
        return res.stdout
    except Exception:
        return ""


def set_clipboard_text(text: str) -> bool:
    """Write plain-text contents to the macOS clipboard."""
    try:
        subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True)
        return True
    except Exception:
        return False


def wipe_clipboard() -> bool:
    """Instantly wipe/empty the macOS clipboard."""
    try:
        subprocess.run(["pbcopy"], input=b"", check=True)
        return True
    except Exception:
        return False


def sanitize_text(text: str) -> tuple[str, dict]:
    """
    Sanitize text:
    - Strip invisible zero-width and control characters.
    - Convert non-breaking spaces to standard spaces.
    - Normalize curly/smart quotes to standard ASCII quotes.
    - Normalize line breaks and trim trailing whitespace per line.
    """
    stats = {
        "original_len": len(text),
        "zero_width_count": 0,
        "quotes_normalized": 0,
        "spaces_normalized": 0,
    }

    if not text:
        return "", stats

    # 1. Count and remove invisible zero-width and formatting control characters
    # \u200b: Zero-Width Space
    # \u200c: Zero-Width Non-Joiner
    # \u200d: Zero-Width Joiner
    # \ufeff: Zero-Width No-Break Space / BOM
    # \u2060: Word Joiner
    # \u00ad: Soft Hyphen
    zero_width_pattern = re.compile(r"[\u200b\u200c\u200d\ufeff\u2060\u00ad]")
    stats["zero_width_count"] = len(zero_width_pattern.findall(text))
    cleaned = zero_width_pattern.sub("", text)

    # 2. Convert non-breaking spaces (\u00a0, \u202f, \u2007) to standard spaces
    nbsp_pattern = re.compile(r"[\u00a0\u202f\u2007]")
    stats["spaces_normalized"] = len(nbsp_pattern.findall(cleaned))
    cleaned = nbsp_pattern.sub(" ", cleaned)

    # 3. Normalize smart / curly quotes
    # Double quotes: \u201c \u201d \u201e \u201f \u00ab \u00bb
    # Single quotes: \u2018 \u2019 \u201a \u201b ` ´
    double_quotes_pattern = re.compile(r"[\u201c\u201d\u201e\u201f\u00ab\u00bb]")
    single_quotes_pattern = re.compile(r"[\u2018\u2019\u201a\u201b`´]")

    dq_count = len(double_quotes_pattern.findall(cleaned))
    sq_count = len(single_quotes_pattern.findall(cleaned))
    stats["quotes_normalized"] = dq_count + sq_count

    cleaned = double_quotes_pattern.sub('"', cleaned)
    cleaned = single_quotes_pattern.sub("'", cleaned)

    # 4. Normalize line breaks and trim trailing whitespace per line
    lines = [line.rstrip() for line in cleaned.splitlines()]
    cleaned = "\n".join(lines)

    stats["final_len"] = len(cleaned)
    return cleaned, stats


def get_clipboard_status() -> dict:
    """Inspect clipboard types and size safely without exposing contents."""
    info_types = []
    try:
        res = subprocess.run(["osascript", "-e", "clipboard info"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            raw_info = res.stdout.strip()
            # osascript returns e.g. "«class utf8», 12, «class HTML», 450"
            matches = re.findall(r"«class ([^»]+)»,\s*(\d+)", raw_info)
            for cls_name, size_bytes in matches:
                info_types.append({"type": cls_name, "size": int(size_bytes)})
    except Exception:
        pass

    text_content = get_clipboard_text()
    line_count = len(text_content.splitlines()) if text_content else 0
    char_count = len(text_content)

    return {
        "is_empty": (not text_content and not info_types),
        "char_count": char_count,
        "line_count": line_count,
        "types": info_types,
    }


def clean_clipboard(mode: str = "wipe", dry_run: bool = False, verbose: bool = False) -> bool:
    """
    Main dispatch for clipboard cleaner.
    mode: 'wipe' (default), 'text' / 'plain', or 'status'
    """
    mode = mode.lower().strip()

    # Mode 1: Status / Inspection
    if mode in ("status", "info", "inspect"):
        status = get_clipboard_status()
        print()
        print("📋 \033[1mClipboard Status\033[0m")
        print("──────────────────────────────────────────────────────────────────────────")
        if status["is_empty"]:
            print("   Status      : \033[90mEmpty (No data on clipboard)\033[0m")
        else:
            print(f"   Characters  : {status['char_count']}")
            print(f"   Lines       : {status['line_count']}")
            if status["types"]:
                type_labels = [f"{t['type']} ({t['size']} B)" for t in status["types"]]
                print(f"   Data Types  : {', '.join(type_labels)}")
            else:
                print("   Data Types  : Plain Text")
        print("──────────────────────────────────────────────────────────────────────────\n")
        return True

    # Mode 2: Text / Plain-Text Sanitization
    if mode in ("text", "plain", "sanitize", "format"):
        raw_text = get_clipboard_text()
        if not raw_text:
            print("\n⚠️  Clipboard is empty or contains no text data.\n")
            return False

        cleaned_text, stats = sanitize_text(raw_text)

        print()
        print("📝 \033[1mClipboard Text Sanitizer\033[0m")
        print("──────────────────────────────────────────────────────────────────────────")
        print(f"   Original length       : {stats['original_len']} characters")
        print(f"   Zero-width removed    : {stats['zero_width_count']}")
        print(f"   Quotes normalized     : {stats['quotes_normalized']}")
        print(f"   Spaces normalized     : {stats['spaces_normalized']}")
        print(f"   Final length          : {stats['final_len']} characters")
        print("──────────────────────────────────────────────────────────────────────────")

        if dry_run:
            print("   \033[34m[DRY-RUN] Preview only. Clipboard was not modified.\033[0m\n")
            return True

        set_clipboard_text(cleaned_text)
        print("   \033[32m✓ Clean plain text copied back to clipboard!\033[0m\n")
        return True

    # Mode 3: Privacy Flush / Wipe (Default)
    if dry_run:
        print("\n   \033[34m[DRY-RUN] Preview only. Clipboard would be wiped.\033[0m\n")
        return True

    success = wipe_clipboard()
    if success:
        print("\n🧹 \033[32mClipboard wiped successfully.\033[0m Sensitive data cleared from memory.\n")
    else:
        print("\n✕ \033[31mFailed to wipe clipboard.\033[0m\n")
    return success


def main():
    parser = argparse.ArgumentParser(
        description="Clipboard Cleaner for macOS: Instant privacy wiping, text formatting sanitization, and status inspection.",
    )
    parser.add_argument(
        "mode",
        nargs="?",
        default="wipe",
        help="Action: 'wipe' (default: clear clipboard), 'text' (sanitize plain text), or 'status' (inspect metadata)",
    )
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Simulate action without altering clipboard",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Display verbose details",
    )

    args = parser.parse_args()
    clean_clipboard(mode=args.mode, dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    main()

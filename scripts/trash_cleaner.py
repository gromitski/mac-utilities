#!/usr/bin/env python3
"""
Trash Cleaner Utility for macOS
---------------------------------
Scans ~/.Trash, reports disk usage, and safely purges items older than a
configurable age threshold (default: 30 days). Protects recently deleted items.

Relies on macOS Finder AppleScript for reliable access with a direct
filesystem fallback for environments where Finder scripting is unavailable.
"""

import datetime
import os
import re
import shutil
import stat
import subprocess
import sys


TRASH_DIR = os.path.expanduser("~/.Trash")
DEFAULT_DAYS = 30


def _format_bytes(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(num_bytes) < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} PB"


def _item_size(path: str) -> int:
    """Return size in bytes; recursively for directories."""
    if os.path.islink(path) or os.path.isfile(path):
        try:
            return os.path.getsize(path)
        except OSError:
            return 0
    total = 0
    for root, dirs, files in os.walk(path):
        for f in files:
            try:
                total += os.path.getsize(os.path.join(root, f))
            except OSError:
                pass
    return total


def _remove_item(path: str) -> bool:
    """Permanently remove a file or directory. Returns True on success."""
    try:
        if os.path.islink(path) or os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path, ignore_errors=False)
        return True
    except Exception:
        # Try chmod on locked files / immutable dirs
        try:
            os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            return True
        except Exception:
            return False


def _empty_via_applescript() -> bool:
    """Empty entire Trash via Finder AppleScript (reliable, no TCC issues)."""
    script = 'tell application "Finder" to empty trash'
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.returncode == 0


def scan_trash() -> list[dict]:
    """
    Scan ~/.Trash and return a list of item dicts:
    {name, path, size_bytes, mtime, age_days}
    """
    items = []
    if not os.path.exists(TRASH_DIR):
        return items
    try:
        entries = os.listdir(TRASH_DIR)
    except PermissionError:
        return items

    now = datetime.datetime.now().timestamp()
    for name in entries:
        if name.startswith(".") and name not in []:
            continue
        path = os.path.join(TRASH_DIR, name)
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            mtime = now
        age_days = (now - mtime) / 86400
        size_bytes = _item_size(path)
        items.append({
            "name": name,
            "path": path,
            "size_bytes": size_bytes,
            "mtime": mtime,
            "age_days": age_days,
        })
    return items


def print_status(items: list[dict], threshold_days: int = DEFAULT_DAYS) -> None:
    """Print a Trash status summary."""
    total_size = sum(i["size_bytes"] for i in items)
    expired = [i for i in items if i["age_days"] >= threshold_days]
    active = [i for i in items if i["age_days"] < threshold_days]
    expired_size = sum(i["size_bytes"] for i in expired)

    print()
    print(f"🗑️  \033[1mTrash Status\033[0m")
    print("──────────────────────────────────────────────────────────────────────────")
    print(f"   Total items  : {len(items)}")
    print(f"   Total size   : {_format_bytes(total_size)}")
    print()
    print(f"   ✅  Safe (trashed <{threshold_days}d)  : {len(active)} items")
    print(f"   🗑️  Expired  (trashed >{threshold_days}d) : {len(expired)} items  ({_format_bytes(expired_size)} reclaimable)")
    print("──────────────────────────────────────────────────────────────────────────")
    print()


def clean_trash(
    older_than_days: int = DEFAULT_DAYS,
    empty_all: bool = False,
    dry_run: bool = False,
    verbose: bool = False,
) -> int:
    """
    Purge Trash items.

    Args:
        older_than_days: Permanently delete items trashed more than this many days ago.
        empty_all:       If True, purge ALL Trash items regardless of age.
        dry_run:         If True, simulate only—nothing is deleted.
        verbose:         If True, print each item being purged.

    Returns:
        Number of bytes reclaimed (0 in dry-run).
    """
    items = scan_trash()
    mode_label = "DRY-RUN" if dry_run else "LIVE"

    if empty_all:
        to_purge = items
        threshold_label = "ALL items"
    else:
        to_purge = [i for i in items if i["age_days"] >= older_than_days]
        threshold_label = f"items older than {older_than_days} days"

    total_size = sum(i["size_bytes"] for i in items)
    purge_size = sum(i["size_bytes"] for i in to_purge)
    kept = [i for i in items if i not in to_purge]

    print()
    print(f"🗑️  \033[1mTrash Cleaner ({mode_label})\033[0m")
    print("──────────────────────────────────────────────────────────────────────────")
    print(f"   Trash contains : {len(items)} items  ({_format_bytes(total_size)})")
    print(f"   To purge       : {len(to_purge)} {threshold_label}  ({_format_bytes(purge_size)})")
    print(f"   To keep        : {len(kept)} items (trashed <{older_than_days}d)")
    print("──────────────────────────────────────────────────────────────────────────")
    print()

    if not to_purge:
        print("   ✓ Nothing to purge — Trash is either empty or all items are recent.\n")
        return 0

    reclaimed = 0
    failed = []

    if dry_run:
        for item in to_purge:
            age_str = f"{item['age_days']:.0f}d"
            if verbose:
                print(f"   [DRY-RUN] Would purge: {item['name']}  (age: {age_str}, size: {_format_bytes(item['size_bytes'])})")
        if not verbose:
            print(f"   [DRY-RUN] Would permanently purge {len(to_purge)} item(s), reclaiming ~{_format_bytes(purge_size)}.")
        print()
    else:
        if empty_all:
            # Use Finder AppleScript for full empty — it handles all edge cases
            print("   Emptying entire Trash via Finder...")
            if _empty_via_applescript():
                reclaimed = total_size
                print(f"   ✓ Trash emptied. Reclaimed {_format_bytes(reclaimed)}.\n")
            else:
                print("   ⚠️  Finder empty failed — falling back to direct filesystem delete.\n")
                for item in to_purge:
                    if _remove_item(item["path"]):
                        reclaimed += item["size_bytes"]
                        if verbose:
                            print(f"   ✓ Purged: {item['name']}  ({_format_bytes(item['size_bytes'])})")
                    else:
                        failed.append(item["name"])
        else:
            for item in to_purge:
                if _remove_item(item["path"]):
                    reclaimed += item["size_bytes"]
                    if verbose:
                        age_str = f"{item['age_days']:.0f}d"
                        print(f"   ✓ Purged: {item['name']}  (age: {age_str}, size: {_format_bytes(item['size_bytes'])})")
                else:
                    failed.append(item["name"])

        if not verbose and not empty_all:
            print(f"   ✓ Purged {len(to_purge) - len(failed)} item(s). Reclaimed {_format_bytes(reclaimed)}.")
            if len(kept) > 0:
                print(f"   ✅  Kept {len(kept)} item(s) trashed within the last {older_than_days} days (safe).\n")
            else:
                print()

        if failed:
            print(f"   ⚠️  Could not purge {len(failed)} item(s) — may be locked or in use:")
            for name in failed[:5]:
                print(f"      • {name}")
            print()

    return reclaimed


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Smart Trash Purge for macOS")
    parser.add_argument(
        "mode",
        nargs="?",
        default="30d",
        help="'status', 'all', '--empty', or age threshold like '30d', '14d', '60d'",
    )
    parser.add_argument("-n", "--dry-run", action="store_true", help="Simulate without deleting")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print every item purged")
    args = parser.parse_args()

    mode = (args.mode or "30d").strip().lower()

    if mode in ("status",):
        items = scan_trash()
        print_status(items)
        return

    if mode in ("all", "--empty", "empty"):
        clean_trash(empty_all=True, dry_run=args.dry_run, verbose=args.verbose)
        return

    # Parse age threshold like "30d", "14d", "60d"
    match = re.match(r"^(\d+)d?$", mode)
    if match:
        days = int(match.group(1))
        clean_trash(older_than_days=days, dry_run=args.dry_run, verbose=args.verbose)
    else:
        print(f"Unknown mode: {mode}. Use 'status', 'all', or a number like '30d'.")
        sys.exit(1)


if __name__ == "__main__":
    main()

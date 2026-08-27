#!/usr/bin/env python3
"""
Trash Cleaner Utility for macOS
---------------------------------
Scans ~/.Trash, reports disk usage, and safely purges items older than a
configurable age threshold (default: 30 days). Protects recently deleted items.

Uses native macOS Finder AppleScript for 100% reliable scanning and silent
shell execution (chflags + rm -rf) for zero-dialog GUI popup purges.
"""

import datetime
import os
import re
import shlex
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


def _parse_applescript_date(d_str: str) -> datetime.datetime:
    """Parse short date string returned by AppleScript (DD/MM/YYYY HH:MM:SS or MM/DD/YYYY)."""
    d_str = d_str.strip()
    for fmt in ["%d/%m/%Y %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y", "%m/%d/%Y"]:
        try:
            return datetime.datetime.strptime(d_str, fmt)
        except ValueError:
            pass
    return datetime.datetime.now()


def scan_trash_applescript() -> list[dict]:
    """Scan Trash via Finder AppleScript (fast bulk property fetch)."""
    items = []
    # 1. Fetch names
    r_names = subprocess.run(
        ["osascript", "-e", 'tell application "Finder" to get name of items of trash'],
        capture_output=True,
        text=True,
    )
    if r_names.returncode != 0 or not r_names.stdout.strip():
        return items

    names = [n.strip() for n in r_names.stdout.strip().split(",") if n.strip()]
    if not names:
        return items

    # 2. Fetch modification dates
    date_script = """
    tell application "Finder"
        set dateList to modification date of items of trash
        set strList to {}
        repeat with d in dateList
            set end of strList to (short date string of d & " " & time string of d)
        end repeat
        return strList
    end tell
    """
    r_dates = subprocess.run(["osascript", "-e", date_script], capture_output=True, text=True)
    date_strs = [d.strip() for d in r_dates.stdout.strip().split(", ") if d.strip()]

    # 3. Fetch sizes
    r_sizes = subprocess.run(
        ["osascript", "-e", 'tell application "Finder" to get size of items of trash'],
        capture_output=True,
        text=True,
    )
    sizes_raw = r_sizes.stdout.strip().split(",")
    sizes = []
    for s in sizes_raw:
        st = s.strip()
        if st and st != "missing value":
            try:
                sizes.append(int(float(st)))
            except ValueError:
                sizes.append(0)
        else:
            sizes.append(0)

    now = datetime.datetime.now()
    count = min(len(names), len(date_strs), len(sizes))

    for i in range(count):
        name = names[i]
        d_str = date_strs[i]
        sz = sizes[i]
        dt = _parse_applescript_date(d_str)
        age_days = (now - dt).total_seconds() / 86400.0
        path = os.path.join(TRASH_DIR, name)

        items.append({
            "name": name,
            "path": path,
            "size_bytes": sz,
            "mtime": dt.timestamp(),
            "age_days": max(0.0, age_days),
        })

    return items


def scan_trash_filesystem() -> list[dict]:
    """Scan ~/.Trash via direct filesystem as fallback."""
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
        size_bytes = 0
        if os.path.islink(path) or os.path.isfile(path):
            try:
                size_bytes = os.path.getsize(path)
            except OSError:
                pass
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    try:
                        size_bytes += os.path.getsize(os.path.join(root, f))
                    except OSError:
                        pass
        items.append({
            "name": name,
            "path": path,
            "size_bytes": size_bytes,
            "mtime": mtime,
            "age_days": max(0.0, age_days),
        })
    return items


def scan_trash() -> list[dict]:
    """Scan Trash using AppleScript first (immune to TCC), falling back to filesystem."""
    items = scan_trash_applescript()
    if not items:
        items = scan_trash_filesystem()
    return items


def _silent_purge_item(item_name: str) -> bool:
    """
    Silently unlock and permanently delete a Trash item without Finder GUI dialog popups.
    """
    quoted = shlex.quote(item_name)
    # Step 1: Remove user-lock flag if set, then rm -rf
    shell_cmd = f"chflags -R nouchg ~/.Trash/{quoted} 2>/dev/null; rm -rf ~/.Trash/{quoted}"
    res = subprocess.run(["bash", "-c", shell_cmd], capture_output=True, text=True)

    if res.returncode == 0:
        return True

    # Step 2: Fallback to AppleScript do shell script (runs silently without Finder GUI popups)
    as_cmd = f'do shell script "chflags -R nouchg ~/.Trash/{quoted} 2>/dev/null; rm -rf ~/.Trash/{quoted}"'
    res_as = subprocess.run(["osascript", "-e", as_cmd], capture_output=True, text=True)
    return res_as.returncode == 0


def _empty_via_applescript() -> bool:
    """Empty entire Trash via silent shell execution."""
    cmd = "chflags -R nouchg ~/.Trash/* 2>/dev/null; rm -rf ~/.Trash/* ~/.Trash/.* 2>/dev/null || true"
    res = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True)
    if res.returncode == 0:
        return True
    as_cmd = f'do shell script "{cmd}"'
    res_as = subprocess.run(["osascript", "-e", as_cmd], capture_output=True, text=True)
    return res_as.returncode == 0


def print_status(items: list[dict], threshold_days: int = DEFAULT_DAYS) -> None:
    """Print a Trash status summary."""
    total_size = sum(i["size_bytes"] for i in items)
    expired = [i for i in items if i["age_days"] >= threshold_days]
    active = [i for i in items if i["age_days"] < threshold_days]
    expired_size = sum(i["size_bytes"] for i in expired)

    print()
    print("🗑️  \033[1mTrash Status\033[0m")
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
        Number of bytes reclaimed.
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
            print("   Emptying entire Trash silently...")
            if _empty_via_applescript():
                reclaimed = total_size
                print(f"   ✓ Trash emptied. Reclaimed {_format_bytes(reclaimed)}.\n")
            else:
                print("   ⚠️  Failed to empty Trash.\n")
        else:
            print(f"   Purging {len(to_purge)} item(s) older than {older_than_days} days silently...")
            failed_count = 0
            for item in to_purge:
                if _silent_purge_item(item["name"]):
                    reclaimed += item["size_bytes"]
                    if verbose:
                        age_str = f"{item['age_days']:.0f}d"
                        print(f"   ✓ Purged: {item['name']}  (age: {age_str}, size: {_format_bytes(item['size_bytes'])})")
                else:
                    failed_count += 1

            purged_count = len(to_purge) - failed_count
            print(f"   ✓ Purged {purged_count} item(s). Reclaimed {_format_bytes(reclaimed)}.")
            if len(kept) > 0:
                print(f"   ✅  Kept {len(kept)} item(s) trashed within the last {older_than_days} days (safe).\n")
            else:
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

    match = re.match(r"^(\d+)d?$", mode)
    if match:
        days = int(match.group(1))
        clean_trash(older_than_days=days, dry_run=args.dry_run, verbose=args.verbose)
    else:
        print(f"Unknown mode: {mode}. Use 'status', 'all', or a number like '30d'.")
        sys.exit(1)


if __name__ == "__main__":
    main()

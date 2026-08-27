#!/usr/bin/env python3
"""
Desktop Housekeeping Utility for macOS
---------------------------------------
Sweeps loose files and directories off the Desktop into monthly archive folders (YYYY-MM/),
keeping your screen and wallpaper spotless without deleting anything.

Guarantees:
- Zero deletions: Files are only organized into monthly folders, never deleted or trashed.
- Protection: System files (.DS_Store, .localized), monthly folders (YYYY-MM), and Archive/ are untouched.
- Collision safe: Automatically appends numbers to filenames (e.g. file (1).pdf) to prevent overwriting.
"""

import argparse
import datetime
import os
import re
import shutil
import sys

MONTH_FOLDER_REGEX = re.compile(r"^\d{4}-\d{2}$")
PROTECTED_NAMES = {"Archive", "_archive", "_review", ".DS_Store", ".localized"}


def get_safe_destination(dest_folder: str, item_name: str) -> str:
    """Generate a collision-free file/folder path in dest_folder."""
    target = os.path.join(dest_folder, item_name)
    if not os.path.exists(target):
        return target

    base, ext = os.path.splitext(item_name)
    counter = 1
    while True:
        candidate = f"{base} ({counter}){ext}"
        target = os.path.join(dest_folder, candidate)
        if not os.path.exists(target):
            return target
        counter += 1


def organize_desktop(desktop_dir: str = "~/Desktop", dry_run: bool = False, verbose: bool = False) -> int:
    """
    Organize loose files and non-archive directories on the Desktop into YYYY-MM/.
    Returns the total number of items organized.
    """
    desktop_dir = os.path.abspath(os.path.expanduser(desktop_dir))
    if not os.path.exists(desktop_dir):
        print(f"Directory not found: {desktop_dir}", file=sys.stderr)
        return 0

    today = datetime.date.today()
    current_month_folder = today.strftime("%Y-%m")
    dest_dir = os.path.join(desktop_dir, current_month_folder)

    mode_label = "DRY-RUN" if dry_run else "LIVE"
    print(f"=== Desktop Housekeeping ({mode_label}) ===")
    print(f"Target Directory : {desktop_dir}")
    print(f"Destination      : {current_month_folder}/")
    print()

    items = sorted(os.listdir(desktop_dir))
    moved_count = 0

    for item in items:
        # Ignore hidden files, system files, and protected folders
        if item.startswith(".") or item in PROTECTED_NAMES or MONTH_FOLDER_REGEX.match(item):
            continue

        src_path = os.path.join(desktop_dir, item)
        safe_dest_path = get_safe_destination(dest_dir, item)

        moved_count += 1
        if dry_run:
            print(f"   [DRY-RUN] Would move: {item} ➔ {current_month_folder}/{os.path.basename(safe_dest_path)}")
        else:
            os.makedirs(dest_dir, exist_ok=True)
            shutil.move(src_path, safe_dest_path)
            if verbose:
                print(f"   ✓ Moved: {item} ➔ {current_month_folder}/{os.path.basename(safe_dest_path)}")

    if not dry_run and moved_count > 0 and not verbose:
        print(f"   ✓ {moved_count} loose item(s) organized into {current_month_folder}/")

    print()
    if dry_run:
        print(f"=== Dry-Run Complete: {moved_count} item(s) would be organized ===")
    else:
        print(f"=== Desktop Housekeeping Complete: {moved_count} item(s) organized ===")
    print()

    return moved_count


def main():
    parser = argparse.ArgumentParser(
        description="Organize loose Desktop files and folders into monthly archives.",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Simulate actions without moving files",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display verbose output for every file moved",
    )
    parser.add_argument(
        "--dir",
        default="~/Desktop",
        help="Custom Desktop directory path (default: ~/Desktop)",
    )

    args = parser.parse_args()
    organize_desktop(desktop_dir=args.dir, dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Screenshot Housekeeping Utility for macOS
------------------------------------------
1. Keeps today's screenshots in the root directory for easy access.
2. Organizes screenshots from previous days into 'YYYY-MM-DD' day folders.
3. Automatically moves 'YYYY-MM-DD' folders older than 14 days to the macOS Trash (~/.Trash).
4. Strictly protects any custom folders (e.g. 'Archive') from modification or deletion.
"""

import argparse
import datetime
import os
import re
import shutil
import sys

DATE_DIR_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SCREENSHOT_DATE_PATTERN = re.compile(r"(?:Screenshot|Screen Shot|Screen Recording) (\d{4}-\d{2}-\d{2})")

VALID_EXTENSIONS = {".png", ".jpg", ".jpeg", ".mov", ".mp4", ".gif", ".webp"}
VALID_PREFIXES = ("Screenshot ", "Screen Shot ", "Screen Recording ")


def parse_file_date(filename: str, filepath: str) -> datetime.date:
    """Extract date from standard macOS screenshot filename, falling back to mtime."""
    match = SCREENSHOT_DATE_PATTERN.search(filename)
    if match:
        try:
            return datetime.datetime.strptime(match.group(1), "%Y-%m-%d").date()
        except ValueError:
            pass

    # Fallback to file modification time
    mtime = os.path.getmtime(filepath)
    return datetime.datetime.fromtimestamp(mtime).date()


def move_to_trash(target_path: str, dry_run: bool = False, verbose: bool = False) -> bool:
    """Move a folder or file safely into the user macOS Trash (~/.Trash)."""
    trash_dir = os.path.expanduser("~/.Trash")
    os.makedirs(trash_dir, exist_ok=True)

    base_name = os.path.basename(target_path)
    dest_path = os.path.join(trash_dir, base_name)

    # Handle name collision in Trash
    if os.path.exists(dest_path):
        timestamp = datetime.datetime.now().strftime("%H%M%S")
        dest_path = os.path.join(trash_dir, f"{base_name}_{timestamp}")

    if dry_run:
        print(f"[DRY-RUN] Would trash: {target_path} -> {dest_path}")
        return True

    try:
        shutil.move(target_path, dest_path)
        if verbose:
            print(f"Trashed: {target_path} -> {dest_path}")
        return True
    except Exception as e:
        print(f"Error trashing {target_path}: {e}", file=sys.stderr)
        return False


def organize_screenshots(
    base_dir: str,
    retention_days: int = 14,
    archive_name: str = "Archive",
    dry_run: bool = False,
    verbose: bool = False,
):
    base_dir = os.path.abspath(os.path.expanduser(base_dir))
    if not os.path.exists(base_dir):
        print(f"Screenshot directory does not exist: {base_dir}")
        return

    today = datetime.date.today()
    cutoff_date = today - datetime.timedelta(days=retention_days)

    print(f"=== Screenshot Housekeeping ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    print(f"Target Directory : {base_dir}")
    print(f"Today's Date     : {today}")
    print(f"Retention Window : {retention_days} days (Trashing folders older than {cutoff_date})")
    print(f"Archive Folder   : '{archive_name}' (Protected)")
    if dry_run:
        print("Mode             : DRY-RUN (No files will be moved or deleted)\n")
    else:
        print("Mode             : LIVE EXECUTION\n")

    # -------------------------------------------------------------
    # Step 1: Organize loose screenshot files into YYYY-MM-DD folders
    # -------------------------------------------------------------
    moved_count = 0
    kept_today_count = 0

    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)

        # Only process regular loose files matching screenshot criteria
        if not os.path.isfile(item_path):
            continue

        ext = os.path.splitext(item)[1].lower()
        if not (item.startswith(VALID_PREFIXES) and ext in VALID_EXTENSIONS):
            continue

        file_date = parse_file_date(item, item_path)

        if file_date == today:
            kept_today_count += 1
            if verbose:
                print(f"Preserving in root (today): {item}")
            continue

        # File is from a previous day -> move into day folder
        date_folder_name = file_date.strftime("%Y-%m-%d")
        date_folder_path = os.path.join(base_dir, date_folder_name)
        target_file_path = os.path.join(date_folder_path, item)

        if dry_run:
            print(f"[DRY-RUN] Would move: {item} -> {date_folder_name}/{item}")
            moved_count += 1
        else:
            os.makedirs(date_folder_path, exist_ok=True)
            # Handle potential name collision in the day folder
            if os.path.exists(target_file_path):
                name_stem, name_ext = os.path.splitext(item)
                target_file_path = os.path.join(
                    date_folder_path, f"{name_stem}_{int(datetime.datetime.now().timestamp())}{name_ext}"
                )
            shutil.move(item_path, target_file_path)
            moved_count += 1
            if verbose:
                print(f"Moved: {item} -> {date_folder_name}/")

    print(f"Step 1 Complete : {moved_count} previous-day file(s) organized, {kept_today_count} today's file(s) preserved in root.")

    # -------------------------------------------------------------
    # Step 2: Clean up YYYY-MM-DD day folders older than retention_days
    # -------------------------------------------------------------
    trashed_folders_count = 0
    preserved_folders_count = 0

    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)

        if not os.path.isdir(item_path):
            continue

        # Explicitly protect Archive and any custom non-date folder
        if item.lower() == archive_name.lower():
            if verbose:
                print(f"Protected folder skipped: {item}/")
            continue

        # Only touch folders named strictly in YYYY-MM-DD format
        if not DATE_DIR_PATTERN.match(item):
            if verbose:
                print(f"Custom folder skipped: {item}/")
            continue

        try:
            folder_date = datetime.datetime.strptime(item, "%Y-%m-%d").date()
        except ValueError:
            continue

        age_days = (today - folder_date).days

        if folder_date < cutoff_date:
            # Older than retention period -> Move to Trash
            success = move_to_trash(item_path, dry_run=dry_run, verbose=verbose)
            if success:
                trashed_folders_count += 1
                if not dry_run and not verbose:
                    print(f"Moved to Trash: {item}/ (Age: {age_days} days)")
        else:
            preserved_folders_count += 1
            if verbose:
                print(f"Retaining: {item}/ (Age: {age_days} days)")

    print(f"Step 2 Complete : {trashed_folders_count} folder(s) moved to Trash, {preserved_folders_count} recent day folder(s) retained.")
    print("=== Done ===\n")


def main():
    parser = argparse.ArgumentParser(description="Clean and organize macOS screenshots into daily folders with 14-day retention.")
    parser.add_argument(
        "--dir",
        default="~/Pictures/screenshots",
        help="Path to screenshots directory (default: ~/Pictures/screenshots)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=14,
        help="Retention period in days before moving to Trash (default: 14)",
    )
    parser.add_argument(
        "--archive-name",
        default="Archive",
        help="Name of the pinned archive folder to protect (default: Archive)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate actions without moving files or trashing folders",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display detailed output for each file and directory",
    )

    args = parser.parse_args()
    organize_screenshots(
        base_dir=args.dir,
        retention_days=args.days,
        archive_name=args.archive_name,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()

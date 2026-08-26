#!/usr/bin/env python3
"""
Downloads Housekeeping Utility for macOS
-----------------------------------------
1. Organizes all loose files and unzipped folders into rolling 3-month 'YYYY-MM' folders.
2. Automatically trashes installer files (.dmg, .pkg, .iso, .app installers) older than 14 days.
3. For monthly folders older than 3 months:
   - Loose files are moved to macOS Trash (~/.Trash).
   - Unzipped directories / custom folders are moved to '_review/' for safe manual review.
4. Strictly protects the '_review/' folder from being moved or deleted.
5. Seamlessly appends to existing month folders without conflicts.
"""

import argparse
import datetime
import os
import re
import shutil
import sys

MONTH_DIR_PATTERN = re.compile(r"^\d{4}-\d{2}$")
INSTALLER_EXTENSIONS = {".dmg", ".pkg", ".iso"}
PROTECTED_NAMES = {"_review", "review", ".ds_store", ".localized"}


def is_installer(filename: str) -> bool:
    """Check if a file or bundle is an installer."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in INSTALLER_EXTENSIONS:
        return True
    if filename.lower().endswith("_installer.app") or filename.lower().endswith("installer.app"):
        return True
    return False


def move_to_trash(target_path: str, dry_run: bool = False, verbose: bool = False) -> bool:
    """Move a folder or file safely into the user macOS Trash (~/.Trash)."""
    trash_dir = os.path.expanduser("~/.Trash")
    os.makedirs(trash_dir, exist_ok=True)

    base_name = os.path.basename(target_path)
    dest_path = os.path.join(trash_dir, base_name)

    if os.path.exists(dest_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
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


def move_to_review(target_path: str, review_dir: str, dry_run: bool = False, verbose: bool = False) -> bool:
    """Move an unzipped/custom directory to the _review folder for safe keeping."""
    os.makedirs(review_dir, exist_ok=True)
    base_name = os.path.basename(target_path)
    dest_path = os.path.join(review_dir, base_name)

    if os.path.exists(dest_path):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        dest_path = os.path.join(review_dir, f"{base_name}_{timestamp}")

    if dry_run:
        print(f"[DRY-RUN] Would move to _review: {target_path} -> {dest_path}")
        return True

    try:
        shutil.move(target_path, dest_path)
        if verbose:
            print(f"Moved to _review: {target_path} -> {dest_path}")
        return True
    except Exception as e:
        print(f"Error moving {target_path} to review: {e}", file=sys.stderr)
        return False


def organize_downloads(
    downloads_dir: str = "~/Downloads",
    installer_days: int = 14,
    archive_months: int = 3,
    review_folder_name: str = "_review",
    dry_run: bool = False,
    verbose: bool = False,
    **kwargs,
):
    downloads_dir = os.path.abspath(os.path.expanduser(downloads_dir))
    if not os.path.exists(downloads_dir):
        print(f"Downloads directory does not exist: {downloads_dir}")
        return

    try:
        raw_items = os.listdir(downloads_dir)
    except PermissionError:
        print(
            f"\n\033[1;31m[Permission Error]\033[0m macOS blocked access to '{downloads_dir}'.\n"
            "Please allow Terminal (or Alfred) access in:\n"
            "👉 System Settings > Privacy & Security > Files and Folders (or Full Disk Access).\n",
            file=sys.stderr,
        )
        sys.exit(1)

    review_dir = os.path.join(downloads_dir, review_folder_name)
    today = datetime.date.today()
    cutoff_3_months = today - datetime.timedelta(days=archive_months * 30)

    print(f"=== Downloads Housekeeping ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}) ===")
    print(f"Target Directory     : {downloads_dir}")
    print(f"Today's Date         : {today}")
    print(f"Installer Purge      : {installer_days} days (Trashing .dmg/.pkg/.iso)")
    print(f"Archive Retention    : {archive_months} months (~{archive_months * 30} days)")
    print(f"Review Folder        : {review_dir} (For unzipped folders >3 months)")
    if dry_run:
        print("Mode                 : DRY-RUN (No files will be moved or deleted)\n")
    else:
        print("Mode                 : LIVE EXECUTION\n")

    # -------------------------------------------------------------
    # Step 1: Scan Root of ~/Downloads and Organize ALL loose items
    # -------------------------------------------------------------
    trashed_installers = 0
    moved_to_month_files = 0
    moved_to_month_dirs = 0

    simulated_month_contents = {}

    for item in raw_items:
        if item.startswith(".") or item.lower() in PROTECTED_NAMES:
            continue

        item_path = os.path.join(downloads_dir, item)
        try:
            mtime = datetime.datetime.fromtimestamp(os.path.getmtime(item_path)).date()
        except OSError:
            continue
        age_days = (today - mtime).days

        # Case A: Loose Files
        if os.path.isfile(item_path):
            # Old installer files (> 14 days) -> Trash
            if is_installer(item) and age_days > installer_days:
                if move_to_trash(item_path, dry_run=dry_run, verbose=verbose):
                    trashed_installers += 1
                continue

            # All other loose files -> Move to YYYY-MM folder
            month_folder_name = mtime.strftime("%Y-%m")
            month_folder_path = os.path.join(downloads_dir, month_folder_name)
            dest_file_path = os.path.join(month_folder_path, item)

            if dry_run:
                print(f"[DRY-RUN] Would move file: {item} -> {month_folder_name}/{item}")
                moved_to_month_files += 1
                simulated_month_contents.setdefault(month_folder_name, []).append(("file", item_path))
            else:
                os.makedirs(month_folder_path, exist_ok=True)
                if os.path.exists(dest_file_path):
                    stem, f_ext = os.path.splitext(item)
                    dest_file_path = os.path.join(
                        month_folder_path, f"{stem}_{int(datetime.datetime.now().timestamp())}{f_ext}"
                    )
                shutil.move(item_path, dest_file_path)
                moved_to_month_files += 1
                if verbose:
                    print(f"Moved file: {item} -> {month_folder_name}/")

        # Case B: Directories / Unzipped folders
        elif os.path.isdir(item_path):
            # Skip existing monthly archive folders (processed in Step 2)
            if MONTH_DIR_PATTERN.match(item):
                continue

            # Installer app bundles (> 14 days)
            if is_installer(item) and age_days > installer_days:
                if move_to_trash(item_path, dry_run=dry_run, verbose=verbose):
                    trashed_installers += 1
                continue

            # Move unzipped folder into YYYY-MM folder
            month_folder_name = mtime.strftime("%Y-%m")
            month_folder_path = os.path.join(downloads_dir, month_folder_name)
            dest_dir_path = os.path.join(month_folder_path, item)

            if dry_run:
                print(f"[DRY-RUN] Would move folder: {item}/ -> {month_folder_name}/{item}/")
                moved_to_month_dirs += 1
                simulated_month_contents.setdefault(month_folder_name, []).append(("dir", item_path))
            else:
                os.makedirs(month_folder_path, exist_ok=True)
                if os.path.exists(dest_dir_path):
                    dest_dir_path = os.path.join(
                        month_folder_path, f"{item}_{int(datetime.datetime.now().timestamp())}"
                    )
                shutil.move(item_path, dest_dir_path)
                moved_to_month_dirs += 1
                if verbose:
                    print(f"Moved folder: {item}/ -> {month_folder_name}/")

    print(f"\nStep 1 Summary : {trashed_installers} installer(s) trashed.")
    print(f"                 {moved_to_month_files} file(s) & {moved_to_month_dirs} unzipped folder(s) organized into monthly folders.\n")

    # -------------------------------------------------------------
    # Step 2: Manage Monthly Archive Folders (> 3 Months Old)
    # -------------------------------------------------------------
    expired_months_count = 0
    retained_months_count = 0
    files_trashed_from_archive = 0
    folders_moved_to_review = 0

    all_months = set(
        [item for item in raw_items if os.path.isdir(os.path.join(downloads_dir, item)) and MONTH_DIR_PATTERN.match(item)]
    )
    if dry_run:
        all_months.update(simulated_month_contents.keys())

    cutoff_month_date = datetime.date(cutoff_3_months.year, cutoff_3_months.month, 1)

    for item in sorted(all_months):
        try:
            folder_month_date = datetime.datetime.strptime(item, "%Y-%m").date()
        except ValueError:
            continue

        item_path = os.path.join(downloads_dir, item)

        if folder_month_date < cutoff_month_date:
            expired_months_count += 1
            print(f"--- Processing Expired Month: {item}/ (> 3 months old) ---")

            if dry_run:
                contents = simulated_month_contents.get(item, [])
                for c_type, c_path in contents:
                    c_name = os.path.basename(c_path)
                    if c_type == "dir":
                        print(f"[DRY-RUN] Would preserve folder in _review: {item}/{c_name} -> {review_folder_name}/{c_name}")
                        folders_moved_to_review += 1
                    else:
                        print(f"[DRY-RUN] Would trash expired file: {item}/{c_name} -> ~/.Trash/{c_name}")
                        files_trashed_from_archive += 1
                print(f"[DRY-RUN] Would clean up month folder: {item}/\n")
            else:
                if os.path.exists(item_path):
                    for sub_item in os.listdir(item_path):
                        if sub_item.startswith("."):
                            continue
                        sub_path = os.path.join(item_path, sub_item)

                        if os.path.isdir(sub_path):
                            if move_to_review(sub_path, review_dir=review_dir, dry_run=dry_run, verbose=verbose):
                                folders_moved_to_review += 1
                        elif os.path.isfile(sub_path):
                            if move_to_trash(sub_path, dry_run=dry_run, verbose=verbose):
                                files_trashed_from_archive += 1

                    try:
                        os.rmdir(item_path)
                        if verbose:
                            print(f"Removed empty month folder: {item}/")
                    except OSError:
                        move_to_trash(item_path, dry_run=dry_run, verbose=verbose)
        else:
            retained_months_count += 1
            if verbose:
                print(f"Retaining active month folder: {item}/")

    print(f"\nStep 2 Summary : {expired_months_count} month(s) expired (>3m): {files_trashed_from_archive} file(s) trashed, {folders_moved_to_review} folder(s) safely preserved in {review_folder_name}/.")
    print(f"                 {retained_months_count} active monthly archive(s) retained.")
    print("=== Done ===\n")


def main():
    parser = argparse.ArgumentParser(description="Downloads Housekeeping utility with installer purge, monthly grouping, and review preservation.")
    parser.add_argument(
        "--dir",
        default="~/Downloads",
        help="Path to Downloads directory (default: ~/Downloads)",
    )
    parser.add_argument(
        "--installers-days",
        type=int,
        default=14,
        help="Retention period in days for installer files (.dmg, .pkg, .iso) before trashing (default: 14)",
    )
    parser.add_argument(
        "--months",
        type=int,
        default=3,
        help="Number of months of archives to keep before expiring (default: 3)",
    )
    parser.add_argument(
        "--review-name",
        default="_review",
        help="Name of review folder for unzipped folders older than 3 months (default: _review)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate actions without moving files or trashing anything",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display detailed output for each file and directory",
    )

    args = parser.parse_args()
    organize_downloads(
        downloads_dir=args.dir,
        installer_days=args.installers_days,
        archive_months=args.months,
        review_folder_name=args.review_name,
        dry_run=args.dry_run,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()

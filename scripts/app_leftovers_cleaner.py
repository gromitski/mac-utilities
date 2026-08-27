#!/usr/bin/env python3
"""
App Leftovers Cleaner for macOS
---------------------------------
Identifies and safely cleans orphaned configuration, saved state, and log
directories left behind by uninstalled applications in ~/Library.

Built with a 4-tier safety model:
1. Indexing all installed apps, bundle IDs, and Casks.
2. Hardcoded zero-touch whitelist for system services & CLI developer tools.
3. 60-day recency guard (never touches recently modified data).
4. Reversible operations (moves to macOS Trash, never hard-deletes).
"""

import argparse
import datetime
import os
import plistlib
import re
import shutil
import subprocess
import sys

# Standard library target directories to scan
USER_LIB = os.path.expanduser("~/Library")
TARGET_DIRS = [
    os.path.join(USER_LIB, "Application Support"),
    os.path.join(USER_LIB, "Saved Application State"),
    os.path.join(USER_LIB, "Logs"),
]

# Standard application search roots
APP_SEARCH_PATHS = [
    "/Applications",
    "/System/Applications",
    "/System/Applications/Utilities",
    "/Applications/Utilities",
    os.path.expanduser("~/Applications"),
    "/System/Library/CoreServices",
    "/opt/homebrew/Caskroom",
    "/opt/homebrew/Cellar",
]

# Permanently protected whitelist (case-insensitive prefixes/exact names)
ZERO_TOUCH_WHITELIST = {
    # System & macOS Core
    "apple", "apple computer", "com.apple", "clouddocs", "mobilesync",
    "addressbook", "callhistory", "safari", "quicklook", "crashreporter",
    "diskimages", "accounts", "quicktime", "syncservices", "icloud",
    "coredata", "family", "finder", "dock", "preferences", "siri",
    "speech", "voicetrigger", "assistant", "security", "keychains",
    "identityservices", "macsecurity", "messages", "photos", "mail",
    "reminders", "notes", "calendar", "contacts", "maps", "preview",
    "textedit", "terminal", "systempreferences", "systemsettings",
    "automator", "shortcuts", "timemachine", "bluetooth", "audio",
    "inputmethods", "spellcheck", "fontcollections", "screensavers",
    "knowledge", "coreparsec", "suggestions", "corespeech",

    # Developer Runtimes, Package Managers & CLI Tools (no .app bundle)
    "homebrew", "pip", "npm", "nvm", "rustup", "cargo", "docker",
    "git", "ssh", "gnupg", "pnpm", "yarn", "zsh", "bash", "fish",
    "code", "cursor", "antigravity", "gemini", "claude", "ollama",
    "openssl", "jetbrains", "python", "node", "java", "ruby", "go",
    "webkit", "electron", "uv", "poetry", "conda", "virtualenvs",
    "dbt", "dataform", "gcloud", "firebase", "flutter", "dart",
    "com.google", "com.github", "com.anthropic", "com.microsoft",
    "alfred", "alfred 5", "alfred 4", "runningwithcrayons",

    # Common shared data stores
    "google", "microsoft", "adobe", "mozilla", "brave", "arc",
    "dropbox", "box", "onedrive", "spotify", "slack", "zoom",
    "notion", "linear", "figma", "tableplus", "postman", "raycast",
}

DEFAULT_RECENCY_DAYS = 60


def format_bytes(size_bytes: int) -> str:
    """Format bytes into a clean, human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if abs(size_bytes) < 1024.0:
            return f"{size_bytes:3.1f} {unit}" if unit != "B" else f"{size_bytes} B"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def get_dir_size(path: str) -> int:
    """Calculate the total size of a directory in bytes."""
    total = 0
    try:
        if os.path.isfile(path) or os.path.islink(path):
            return os.path.getsize(path)
        for entry in os.scandir(path):
            if entry.is_symlink():
                continue
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    except (PermissionError, FileNotFoundError):
        pass
    return total


def index_installed_apps() -> set[str]:
    """
    Build a comprehensive set of known application identifiers, display names,
    bundle IDs, executable names, and package folder names.
    """
    known_names = set()

    for root_dir in APP_SEARCH_PATHS:
        if not os.path.exists(root_dir):
            continue
        try:
            for item in os.listdir(root_dir):
                full_path = os.path.join(root_dir, item)
                base_name = item.lower()

                # Add folder/cask name directly
                known_names.add(base_name)
                if base_name.endswith(".app"):
                    clean_name = base_name[:-4]
                    known_names.add(clean_name)
                    known_names.add(re.sub(r"[^a-z0-9]", "", clean_name))

                # Inspect Info.plist if it's an app bundle
                info_plist_path = os.path.join(full_path, "Contents", "Info.plist")
                if os.path.exists(info_plist_path):
                    try:
                        with open(info_plist_path, "rb") as fp:
                            plist_data = plistlib.load(fp)

                        # CFBundleIdentifier (e.g. com.google.Chrome)
                        bundle_id = plist_data.get("CFBundleIdentifier", "")
                        if bundle_id:
                            known_names.add(bundle_id.lower())
                            for part in bundle_id.lower().split("."):
                                if len(part) > 2:
                                    known_names.add(part)

                        # CFBundleName
                        cf_name = plist_data.get("CFBundleName", "")
                        if cf_name:
                            known_names.add(cf_name.lower())

                        # CFBundleDisplayName
                        display_name = plist_data.get("CFBundleDisplayName", "")
                        if display_name:
                            known_names.add(display_name.lower())

                        # CFBundleExecutable
                        executable = plist_data.get("CFBundleExecutable", "")
                        if executable:
                            known_names.add(executable.lower())

                    except Exception:
                        pass
        except (PermissionError, FileNotFoundError):
            continue

    # Add active running processes to ensure no running background daemon is flagged
    try:
        res = subprocess.run(["ps", "-eo", "comm="], capture_output=True, text=True)
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                proc = os.path.basename(line.strip()).lower()
                if proc:
                    known_names.add(proc)
                    if proc.endswith(".app"):
                        known_names.add(proc[:-4])
    except Exception:
        pass

    return known_names


def is_whitelisted(name: str) -> bool:
    """Check if a folder or bundle ID matches the zero-touch whitelist."""
    norm = name.lower()

    # Skip hidden entries
    if norm.startswith("."):
        return True

    # Exact or prefix match against whitelist
    for item in ZERO_TOUCH_WHITELIST:
        if norm == item or norm.startswith(item + ".") or norm.startswith(item + "_") or norm.startswith(item + " "):
            return True
        if item in norm and len(item) >= 5:
            # e.g. "com.apple.something" matches "com.apple"
            if norm.startswith("com.apple") or norm.startswith("apple"):
                return True

    return False


def is_recently_modified(path: str, days: int = DEFAULT_RECENCY_DAYS) -> bool:
    """Check if any file in the directory has been modified within the given days."""
    cutoff = datetime.datetime.now().timestamp() - (days * 86400)
    try:
        stat_res = os.stat(path)
        if stat_res.st_mtime >= cutoff:
            return True

        # Check top-level children for recent updates
        if os.path.isdir(path):
            for entry in os.scandir(path):
                try:
                    if entry.stat().st_mtime >= cutoff:
                        return True
                except (PermissionError, FileNotFoundError):
                    pass
    except (PermissionError, FileNotFoundError):
        return True  # If inaccessible, protect by default
    return False


def scan_orphaned_leftovers(recency_days: int = DEFAULT_RECENCY_DAYS) -> list[dict]:
    """
    Scan target Library directories and identify orphaned app leftovers.
    Returns a list of dictionaries with item metadata.
    """
    known_apps = index_installed_apps()
    orphans = []

    for target_dir in TARGET_DIRS:
        if not os.path.exists(target_dir):
            continue

        try:
            for entry_name in os.listdir(target_dir):
                full_path = os.path.join(target_dir, entry_name)

                # Skip hidden entries and standard symlinks
                if entry_name.startswith(".") or os.path.islink(full_path):
                    continue

                # 1. Whitelist Check
                if is_whitelisted(entry_name):
                    continue

                # Clean name for matching
                norm_name = entry_name.lower()
                clean_name = norm_name
                if clean_name.endswith(".savedstate"):
                    clean_name = clean_name[:-11]

                # 2. Known Apps Check
                is_known = (
                    norm_name in known_apps or
                    clean_name in known_apps or
                    re.sub(r"[^a-z0-9]", "", clean_name) in known_apps
                )

                if is_known:
                    continue

                # Check if parts of bundle id match known apps (e.g. "org.videolan.vlc" -> "vlc")
                parts = clean_name.split(".")
                if any(p in known_apps for p in parts if len(p) > 3):
                    continue

                # 3. Recency Check (Zero-touch if modified within last N days)
                if is_recently_modified(full_path, days=recency_days):
                    continue

                # Calculate size and age
                size_bytes = get_dir_size(full_path)
                try:
                    mtime = os.stat(full_path).st_mtime
                    age_days = (datetime.datetime.now().timestamp() - mtime) / 86400.0
                except Exception:
                    age_days = 0.0

                category = os.path.basename(target_dir)
                orphans.append({
                    "name": entry_name,
                    "path": full_path,
                    "category": category,
                    "size_bytes": size_bytes,
                    "age_days": age_days,
                })

        except (PermissionError, FileNotFoundError):
            continue

    # Sort orphans by size descending
    orphans.sort(key=lambda x: x["size_bytes"], reverse=True)
    return orphans


def clean_app_leftovers(
    dry_run: bool = False,
    force: bool = False,
    verbose: bool = False,
    recency_days: int = DEFAULT_RECENCY_DAYS,
) -> int:
    """
    Scan and safely move orphaned app leftovers to macOS Trash.
    Returns total bytes reclaimed.
    """
    mode_label = "DRY-RUN" if dry_run else "LIVE"
    orphans = scan_orphaned_leftovers(recency_days=recency_days)

    total_size = sum(o["size_bytes"] for o in orphans)

    print()
    print(f"👻  \033[1mApp Leftovers Cleaner ({mode_label})\033[0m")
    print("──────────────────────────────────────────────────────────────────────────")
    print(f"   Orphaned items found : {len(orphans)}")
    print(f"   Reclaimable space    : {format_bytes(total_size)}")
    print(f"   Safety threshold     : Unmodified for >{recency_days} days (recent items protected)")
    print("──────────────────────────────────────────────────────────────────────────")
    print()

    if not orphans:
        print("   ✓ No orphaned application leftovers found. Your Library is clean!\n")
        return 0

    # Display items
    for item in orphans:
        age_str = f"{item['age_days']:.0f}d ago"
        size_str = format_bytes(item["size_bytes"])
        cat_str = f"[{item['category']}]"
        print(f"   • \033[33m{item['name']}\033[0m {cat_str} — {size_str} \033[90m(last modified {age_str})\033[0m")

    print()

    if dry_run:
        print(f"   \033[34m[DRY-RUN] Preview only. {len(orphans)} item(s) would be moved to Trash ({format_bytes(total_size)}).\033[0m\n")
        return total_size

    # Confirmation prompt if not forced
    if not force:
        try:
            response = input(f"   Move these {len(orphans)} orphaned item(s) to Trash? [y/N]: ").strip().lower()
            if response not in ("y", "yes"):
                print("   ✕ Operation cancelled. No files were touched.\n")
                return 0
        except (KeyboardInterrupt, EOFError):
            print("\n   ✕ Operation cancelled.\n")
            return 0

    # Move items to Trash
    trash_dir = os.path.expanduser("~/.Trash")
    reclaimed = 0
    moved_count = 0

    print()
    for item in orphans:
        source_path = item["path"]
        base_name = item["name"]
        dest_path = os.path.join(trash_dir, base_name)

        # Handle destination collision in Trash
        if os.path.exists(dest_path):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            dest_path = os.path.join(trash_dir, f"{base_name}_{timestamp}")

        try:
            shutil.move(source_path, dest_path)
            reclaimed += item["size_bytes"]
            moved_count += 1
            if verbose:
                print(f"   ✓ Moved to Trash: {item['name']} ({format_bytes(item['size_bytes'])})")
        except Exception as e:
            print(f"   \033[31m✕ Failed to move:\033[0m {item['name']} ({e})")

    print(f"   \033[32m✓ Successfully moved {moved_count} orphaned item(s) to Trash.\033[0m Reclaimed \033[1m{format_bytes(reclaimed)}\033[0m.\n")
    return reclaimed


def main():
    parser = argparse.ArgumentParser(
        description="App Leftovers Cleaner for macOS: Safely clean orphaned app support data.",
    )
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Simulate scan without moving any files to Trash",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Move identified leftovers to Trash without interactive prompt",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress during cleanup",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=DEFAULT_RECENCY_DAYS,
        help=f"Minimum days since last modification (default: {DEFAULT_RECENCY_DAYS})",
    )

    args = parser.parse_args()
    clean_app_leftovers(
        dry_run=args.dry_run,
        force=args.force,
        verbose=args.verbose,
        recency_days=args.days,
    )


if __name__ == "__main__":
    main()

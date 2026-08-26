#!/usr/bin/env python3
"""
System & Cache Space Reclaimer for macOS (Conservative Safe Mode)
------------------------------------------------------------------
Safely reclaims ghost disk space using official package manager & developer tool cleanups:
1. Homebrew: Clears outdated formula archives and downloaded bottles (brew cleanup -s).
2. npm: Purges downloaded tarball cache (npm cache clean --force).
3. pip: Purges downloaded Python wheel cache (pip cache purge).
4. Xcode: Clears temporary build cache (DerivedData) if present.

Guarantees:
- Never touches ~/Library/Application Support/ (all app logins/settings safe).
- Never touches general app caches in ~/Library/Caches/.
- Never touches project source code or virtual environments.
"""

import argparse
import os
import shutil
import subprocess
import sys


def get_dir_size(path: str) -> int:
    """Calculate the total size of a directory in bytes."""
    total = 0
    if not os.path.exists(path):
        return 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            try:
                total += os.path.getsize(fp)
            except (OSError, FileNotFoundError):
                pass
    return total


def format_bytes(size_bytes: int) -> str:
    """Format bytes into a human-readable string (KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def find_binary(name: str, fallback_paths=None) -> str:
    """Locate a binary on PATH or via standard fallback locations."""
    path = shutil.which(name)
    if path:
        return path
    if fallback_paths:
        for p in fallback_paths:
            if os.path.exists(p) and os.access(p, os.X_OK):
                return p
    return ""


def clean_system_caches(dry_run: bool = False, verbose: bool = False) -> int:
    """
    Execute conservative safe cache cleaning routines.
    Returns estimated total bytes reclaimed.
    """
    print(f"=== System & Cache Space Reclaimer ({'DRY-RUN' if dry_run else 'LIVE'}) ===")

    free_before = shutil.disk_usage("/").free
    tasks_performed = 0

    # -------------------------------------------------------------
    # 1. Homebrew Cleanup
    # -------------------------------------------------------------
    brew_bin = find_binary("brew", ["/opt/homebrew/bin/brew", "/usr/local/bin/brew"])
    if brew_bin:
        print("🍺 Cleaning Homebrew cache & outdated downloads...")
        if dry_run:
            res = subprocess.run([brew_bin, "cleanup", "-s", "--dry-run"], capture_output=True, text=True)
            lines = [l for l in res.stdout.splitlines() if l.strip().startswith("Would remove:")]
            print(f"   [DRY-RUN] Homebrew would remove ~{len(lines)} cached archive(s).")
            if verbose and lines:
                for l in lines[:5]:
                    print(f"      {l}")
        else:
            subprocess.run([brew_bin, "cleanup", "-s"], capture_output=True, text=True)
            print("   ✓ Homebrew bottle archives & outdated versions cleaned.")
        tasks_performed += 1
    else:
        if verbose:
            print("   • Homebrew not found; skipping.")

    # -------------------------------------------------------------
    # 2. Node / npm Cache
    # -------------------------------------------------------------
    npm_cache_dir = os.path.expanduser("~/.npm/_cacache")
    if os.path.exists(npm_cache_dir):
        npm_size = get_dir_size(npm_cache_dir)
        print(f"📦 Cleaning npm cache ({format_bytes(npm_size)})...")
        if dry_run:
            print(f"   [DRY-RUN] Would clean npm cache: {format_bytes(npm_size)}.")
        else:
            npm_bin = find_binary("npm", [
                os.path.expanduser("~/.nvm/versions/node/v24.18.0/bin/npm"),
                "/opt/homebrew/bin/npm",
                "/usr/local/bin/npm",
            ])
            if npm_bin:
                subprocess.run([npm_bin, "cache", "clean", "--force"], capture_output=True, text=True)
            else:
                shutil.rmtree(npm_cache_dir, ignore_errors=True)
            print("   ✓ npm package download cache purged.")
        tasks_performed += 1

    # -------------------------------------------------------------
    # 3. Python / pip Cache
    # -------------------------------------------------------------
    pip_cache_dir = os.path.expanduser("~/Library/Caches/pip")
    if not os.path.exists(pip_cache_dir):
        pip_cache_dir = os.path.expanduser("~/.cache/pip")

    if os.path.exists(pip_cache_dir):
        pip_size = get_dir_size(pip_cache_dir)
        if pip_size > 0:
            print(f"🐍 Cleaning pip cache ({format_bytes(pip_size)})...")
            if dry_run:
                print(f"   [DRY-RUN] Would clean pip cache: {format_bytes(pip_size)}.")
            else:
                subprocess.run([sys.executable, "-m", "pip", "cache", "purge"], capture_output=True, text=True)
                print("   ✓ Python pip wheel download cache purged.")
            tasks_performed += 1

    # -------------------------------------------------------------
    # 4. Xcode DerivedData Cache (if present)
    # -------------------------------------------------------------
    derived_data = os.path.expanduser("~/Library/Developer/Xcode/DerivedData")
    if os.path.exists(derived_data):
        xcode_size = get_dir_size(derived_data)
        if xcode_size > 1024 * 1024:  # > 1MB
            print(f"🔨 Cleaning Xcode DerivedData ({format_bytes(xcode_size)})...")
            if dry_run:
                print(f"   [DRY-RUN] Would clear Xcode build cache: {format_bytes(xcode_size)}.")
            else:
                shutil.rmtree(derived_data, ignore_errors=True)
                os.makedirs(derived_data, exist_ok=True)
                print("   ✓ Xcode temporary build cache purged.")
            tasks_performed += 1

    free_after = shutil.disk_usage("/").free
    reclaimed = max(0, free_after - free_before)

    print()
    if dry_run:
        print("=== Dry-Run Complete: No files were deleted ===")
    else:
        print(f"=== Deep Clean Complete: {tasks_performed} safe tasks executed ===")
        if reclaimed > 0:
            print(f"🎉 Estimated Space Reclaimed: {format_bytes(reclaimed)}")
    print()

    return reclaimed


def main():
    parser = argparse.ArgumentParser(description="Conservative safe macOS system & developer cache reclaimer.")
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Simulate actions without deleting anything",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display verbose output",
    )
    args = parser.parse_args()

    clean_system_caches(dry_run=args.dry_run, verbose=args.verbose)


if __name__ == "__main__":
    main()

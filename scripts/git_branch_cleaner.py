#!/usr/bin/env python3
"""
Git Branch Cleaner for macOS
-----------------------------
Safely identifies and prunes local Git branches that have already been merged
into main/master or deleted on the remote repository.

Safety Guarantees:
- Never deletes protected primary branches (main, master, develop, staging, release/*).
- Never deletes the currently active branch.
- Uses safe deletion (git branch -d) by default.
- Never runs automatically during standard or deep system cleans.
"""

from __future__ import annotations
import argparse
import os
import re
import subprocess
import sys
from typing import Optional, List, Dict, Set

PROTECTED_BRANCHES = {
    "main", "master", "develop", "dev", "staging",
    "production", "prod", "trunk", "gh-pages",
}

DEFAULT_WORKSPACE_DIRS = [
    os.path.expanduser("~/Projects"),
    os.path.expanduser("~/utilities"),
    os.path.expanduser("~/Documents"),
]


def run_git(args: list[str], cwd: Optional[str] = None) -> tuple[int, str, str]:
    """Run a Git command and return (returncode, stdout, stderr)."""
    try:
        res = subprocess.run(
            ["git"] + args,
            cwd=cwd or os.getcwd(),
            capture_output=True,
            text=True,
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except Exception as e:
        return 1, "", str(e)


def is_git_repo(path: Optional[str] = None) -> bool:
    """Check if the directory is inside a Git working tree."""
    code, out, _ = run_git(["rev-parse", "--is-inside-work-tree"], cwd=path)
    return code == 0 and out == "true"


def get_git_root(path: Optional[str] = None) -> Optional[str]:
    """Get the root directory of the current Git repository."""
    code, out, _ = run_git(["rev-parse", "--show-toplevel"], cwd=path)
    return out if code == 0 else None


def get_default_branch(repo_path: str) -> str:
    """Detect the default branch (main or master)."""
    # 1. Try remote symbolic ref
    code, out, _ = run_git(["symbolic-ref", "refs/remotes/origin/HEAD"], cwd=repo_path)
    if code == 0 and out:
        return out.split("/")[-1]

    # 2. Check local branch list for main or master
    code, out, _ = run_git(["branch", "--list", "main", "master"], cwd=repo_path)
    if code == 0 and out:
        branches = [b.strip().lstrip("* ") for b in out.splitlines()]
        if "main" in branches:
            return "main"
        if "master" in branches:
            return "master"

    return "main"


def get_current_branch(repo_path: str) -> str:
    """Get the currently checked out branch name."""
    code, out, _ = run_git(["branch", "--show-current"], cwd=repo_path)
    return out if code == 0 else ""


def is_protected(branch: str) -> bool:
    """Check if a branch name is in the protected list."""
    norm = branch.lower().strip()
    if norm in PROTECTED_BRANCHES:
        return True
    if norm.startswith("release/") or norm.startswith("hotfix/") or norm.startswith("v"):
        return True
    return False


def scan_stale_branches(repo_path: str, fetch: bool = True) -> list[dict]:
    """
    Scan for stale local branches in the given repository.
    Returns list of dicts with branch metadata.
    """
    if not is_git_repo(repo_path):
        return []

    # 1. Fetch & prune remote refs if connected to remote
    if fetch:
        run_git(["fetch", "--prune", "origin"], cwd=repo_path)

    default_branch = get_default_branch(repo_path)
    current_branch = get_current_branch(repo_path)

    # 2. Get list of merged branches
    merged_branches = set()
    code, out, _ = run_git(["branch", "--merged", default_branch], cwd=repo_path)
    if code == 0 and out:
        for line in out.splitlines():
            b = line.strip().lstrip("* ")
            if b:
                merged_branches.add(b)

    # 3. Get branches marked as '[gone]' (upstream deleted)
    gone_branches = set()
    code, out, _ = run_git(["branch", "-vv"], cwd=repo_path)
    if code == 0 and out:
        for line in out.splitlines():
            # Pattern: "* branch_name commit_hash [origin/branch_name: gone] commit message"
            match = re.search(r"^\*?\s*(\S+)\s+[a-f0-9]+\s+\[[^:]+: gone\]", line)
            if match:
                gone_branches.add(match.group(1))

    candidates = set()
    for b in merged_branches | gone_branches:
        if b == current_branch or b == default_branch or is_protected(b):
            continue
        candidates.add(b)

    stale_list = []
    for b in sorted(candidates):
        # Determine reason
        reasons = []
        if b in merged_branches:
            reasons.append(f"Merged into {default_branch}")
        if b in gone_branches:
            reasons.append("Remote tracking deleted (: gone)")
        reason_str = " & ".join(reasons)

        # Get last commit relative time and subject
        _, date_str, _ = run_git(["log", "-1", "--format=%cr", b], cwd=repo_path)
        _, subject_str, _ = run_git(["log", "-1", "--format=%s", b], cwd=repo_path)

        stale_list.append({
            "name": b,
            "reason": reason_str,
            "last_commit_date": date_str or "unknown",
            "last_commit_subject": subject_str or "",
        })

    return stale_list


def clean_branches_in_repo(
    repo_path: str,
    dry_run: bool = False,
    force: bool = False,
    fetch: bool = True,
    verbose: bool = False,
) -> int:
    """Clean stale branches in a single Git repository."""
    if not is_git_repo(repo_path):
        print(f"\n⚠️  \033[31mNot a Git repository:\033[0m {repo_path}\n")
        return 0

    root = get_git_root(repo_path)
    repo_name = os.path.basename(root)
    current_branch = get_current_branch(root)
    mode_label = "DRY-RUN" if dry_run else "LIVE"

    print()
    print(f"🌿  \033[1mGit Branch Cleaner ({mode_label})\033[0m")
    print("──────────────────────────────────────────────────────────────────────────")
    print(f"   Repository     : {repo_name}  \033[90m({root})\033[0m")
    print(f"   Active branch  : \033[32m{current_branch}\033[0m (Protected)")
    print("──────────────────────────────────────────────────────────────────────────")

    stale_branches = scan_stale_branches(root, fetch=fetch)

    if not stale_branches:
        print("\n   ✓ No stale or merged branches found. Your repository is clean!\n")
        return 0

    print(f"\n   Found \033[1m{len(stale_branches)}\033[0m stale local branch(es):\n")
    for b in stale_branches:
        print(f"   • \033[33m{b['name']}\033[0m \033[90m({b['reason']})\033[0m")
        print(f"     \033[90mLast commit: {b['last_commit_date']} — {b['last_commit_subject'][:60]}\033[0m")

    print()

    if dry_run:
        print(f"   \033[34m[DRY-RUN] Preview only. {len(stale_branches)} branch(es) would be deleted.\033[0m\n")
        return len(stale_branches)

    # Interactive confirmation prompt
    if not force:
        try:
            response = input(f"   Delete these {len(stale_branches)} local branch(es)? [y/N]: ").strip().lower()
            if response not in ("y", "yes"):
                print("   ✕ Cancelled. No branches were deleted.\n")
                return 0
        except (KeyboardInterrupt, EOFError):
            print("\n   ✕ Cancelled.\n")
            return 0

    deleted_count = 0
    print()
    for b in stale_branches:
        branch_name = b["name"]
        code, _, err = run_git(["branch", "-d", branch_name], cwd=root)
        if code == 0:
            deleted_count += 1
            print(f"   ✓ Deleted local branch: \033[32m{branch_name}\033[0m")
        else:
            print(f"   \033[31m✕ Failed to delete {branch_name}:\033[0m {err}")
            print(f"     \033[90m(Use 'git branch -D {branch_name}' manually if unmerged commits are intentional)\033[0m")

    print(f"\n   \033[32m✨ Cleaned up {deleted_count} stale branch(es).\033[0m\n")
    return deleted_count


def scan_workspace(search_dirs: Optional[list[str]] = None) -> None:
    """Scan all repositories across workspace directories and report stale branches."""
    search_dirs = search_dirs or DEFAULT_WORKSPACE_DIRS
    print()
    print("🌿 \033[1mWorkspace Git Branch Audit\033[0m")
    print("──────────────────────────────────────────────────────────────────────────")

    found_repos = []
    for base in search_dirs:
        if not os.path.exists(base):
            continue
        try:
            for entry in os.scandir(base):
                if entry.is_dir():
                    git_dir = os.path.join(entry.path, ".git")
                    if os.path.exists(git_dir):
                        found_repos.append(entry.path)
        except (PermissionError, FileNotFoundError):
            continue

    if not found_repos:
        print("   No Git repositories found in workspace directories.\n")
        return

    print(f"   Scanning {len(found_repos)} repositories across workspace...\n")

    total_stale = 0
    for repo_path in sorted(found_repos):
        repo_name = os.path.basename(repo_path)
        stale = scan_stale_branches(repo_path, fetch=False)
        if stale:
            total_stale += len(stale)
            branch_names = ", ".join(b["name"] for b in stale[:3])
            more_str = f" (+{len(stale)-3} more)" if len(stale) > 3 else ""
            print(f"   • \033[1m{repo_name}\033[0m: \033[33m{len(stale)} stale branch(es)\033[0m \033[90m({branch_names}{more_str})\033[0m")
        else:
            print(f"   • \033[90m{repo_name}: Clean (0 stale branches)\033[0m")

    print("──────────────────────────────────────────────────────────────────────────")
    if total_stale > 0:
        print(f"   Total stale branches across workspace: \033[1;33m{total_stale}\033[0m")
        print("   \033[90mRun 'cd <repo> && clean branches' to clean individual repositories.\033[0m\n")
    else:
        print("   \033[32m✨ All repositories in workspace are 100% clean!\033[0m\n")


def main():
    parser = argparse.ArgumentParser(
        description="Git Branch Cleaner for macOS: Prune merged and dead local feature branches.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Repository path to clean (default: current directory)",
    )
    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Audit stale branches across all workspace repositories",
    )
    parser.add_argument(
        "-n", "--dry-run",
        action="store_true",
        help="Simulate scan without deleting any branches",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Bypass interactive confirmation prompt",
    )
    parser.add_argument(
        "--no-fetch",
        action="store_true",
        help="Skip 'git fetch --prune' (offline mode)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Display verbose details",
    )

    args = parser.parse_args()

    if args.all:
        scan_workspace()
    else:
        clean_branches_in_repo(
            repo_path=args.path,
            dry_run=args.dry_run,
            force=args.force,
            fetch=not args.no_fetch,
            verbose=args.verbose,
        )


if __name__ == "__main__":
    main()

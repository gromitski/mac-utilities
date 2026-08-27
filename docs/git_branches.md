# 🌿 Git Branch Cleaner (`clean branches`)

Safely identifies and prunes local Git branches that have already been merged into `main` or whose upstream tracking branches have been deleted (`: gone`) on GitHub/GitLab.

> 🔒 **Independent Execution:** `clean branches` is **strictly an on-demand utility**. It is **never** executed automatically by standard `clean` or `clean deep`, protecting your development repositories unless you explicitly run the command.

---

## 🎯 What it Cleans

* **Merged Branches:** Local feature branches whose commits are already fully integrated into the repository's default branch (`main` / `master`).
* **Deleted Remote Tracking Branches (`[gone]`):** Local branches whose upstream tracking branches on GitHub/GitLab were deleted after a pull request merge.
* **Remote Ref Pruning:** Runs `git fetch --prune` first so local tracking status matches the remote accurately.

---

## 🛡️ Hardcoded Safety Guarantees

1. **Protected Branch Whitelist:** Primary branches are **permanently protected** from deletion: `main`, `master`, `develop`, `dev`, `staging`, `production`, `trunk`, `release/*`, `hotfix/*`.
2. **Current Active Branch Guard:** The branch you are currently standing on (`git branch --show-current`) is **never** touched.
3. **Safe Deletion (`git branch -d`):** Always uses Git's native safe deletion. If a branch has unmerged commits, Git blocks the deletion and alerts you.
4. **Interactive Prompt:** Lists candidate branches with author, commit date, and commit subject with a `[y/N]` confirmation before removing anything.

---

## 💻 Terminal CLI Usage

```bash
# 1. Clean merged/dead branches in current repository (interactive)
clean branches

# 2. Preview only (shows candidate branches without deleting)
clean branches -n
# or
clean branches --dry-run

# 3. Clean without interactive prompt (for trusted scripts)
clean branches --force

# 4. Clean a specific repository path
clean branches ~/Projects/my-app

# 5. Workspace-wide Audit (scans all repos in ~/Projects, ~/utilities, ~/Documents)
clean branches --all
# or
clean branches all
```

---

## 🔍 Triggering via Alfred

1. Press your Alfred hotkey (e.g. `Cmd + Space`).
2. Type **`clean`**.
3. Select **🌿 Clean Git Branches** to prune merged branches in your active repository.

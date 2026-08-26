# 🔍 Git Repositories Audit (`git-audit`)

A fast multi-threaded Git repository scanner for macOS that provides an instant visual overview of uncommitted changes, unpushed commits, and branch synchronization across all your projects.

---

## 🎯 Features

* **Instant Parallel Scan:** Scans dozens of repositories in < 1 second using multi-threading.
* **Auto-Discovery:** Automatically searches standard development roots (`~/Projects`, `~/utilities`, `~/Documents`, `~/Code`, `~/Developer`).
* **Uncommitted & Untracked Tracking:** Flags modified, staged, and untracked files (`3M+2?`).
* **Remote Sync Check:** Identifies unpushed commits (ahead `↑`) and unpulled commits (behind `↓`).
* **Alfred Integration:** Live interactive search in Alfred to check repo status and open directories directly.

---

## 💻 Terminal CLI Usage

```bash
# 1. Standard scan across all project directories
git-audit

# 2. Focus mode: only display repositories that need attention
git-audit -d
# or
git-audit --dirty-only

# 3. Detailed mode: show modified file names and unpushed commit messages
git-audit -v
# or
git-audit --verbose

# 4. Scan a specific directory or repository
git-audit ~/Projects
git-audit .
```

---

## 🔍 Triggering via Alfred

1. Press your Alfred hotkey (e.g. `Cmd + Space`).
2. Type **`git-audit`**.
3. Alfred will immediately render a live list of your repositories with their status badges:
   * 🟢 Clean & Synced
   * 🟡 Uncommitted changes
   * ⬆️ Unpushed commits
   * ⬇️ Behind remote
4. Press **Enter** on any repository to open it directly in Terminal.

---

## 🔄 Setup on a New Mac

`git-audit` is located in `~/utilities/scripts/` and is automatically available in your shell once `~/utilities/scripts` is added to `$PATH` in `~/.zshrc`:

```bash
echo 'export PATH="$HOME/utilities/scripts:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

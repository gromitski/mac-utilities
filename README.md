# Mac Utilities (`mac-utilities`)

A collection of lightweight, portable automation scripts, LaunchAgents, and Alfred workflows for macOS.

---

## 🛠 Available Utilities

| Utility | Description | Documentation |
| :--- | :--- | :--- |
| **`clean`** | Master on-demand CLI & Alfred trigger (`clean`, `clean screenshots`, `clean downloads`, `clean deep`, `clean cache`, `clean -n`). | [Instructions & Details](docs/clean.md) |
| **Screenshot Housekeeping** | Organizes loose screenshots into daily `YYYY-MM-DD/` folders, purges items older than 14 days to Trash, and permanently protects `Archive/`. | [Instructions & Details](docs/screenshot_housekeeping.md) |
| **Downloads Housekeeping** | Organizes loose files into rolling 3-month `YYYY-MM/` folders, purges installers after 14 days, and moves expired unzipped folders to `_review/`. | [Instructions & Details](docs/downloads_housekeeping.md) |
| **System Cache Reclaimer** | Conservative safe disk space reclaimer for Homebrew, npm, pip, and Xcode caches. | [Instructions & Details](docs/system_cache_cleaner.md) |

---

## 🚀 Quick Setup on a New Mac

To restore and activate all utilities on a new or fresh Mac:

```bash
# 1. Clone this repository
git clone git@github.com:gromitski/mac-utilities.git ~/utilities

# 2. Add scripts to PATH in ~/.zshrc
echo 'export PATH="$HOME/utilities/scripts:$PATH"' >> ~/.zshrc
source ~/.zshrc

# 3. Make all scripts executable
chmod +x ~/utilities/scripts/*

# 4. Install and load automated daily schedules (launchd)
cp ~/utilities/launchd/*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.gromitski.screenshot-housekeeping.plist
launchctl load ~/Library/LaunchAgents/com.gromitski.downloads-housekeeping.plist

# 5. (Optional) Install Alfred Workflow
open ~/utilities/alfred/Clean.alfredworkflow
```

> **Note on Permissions:** If macOS ever blocks terminal access to Downloads (`Operation not permitted`), reset the permission cache by running:  
> `tccutil reset SystemPolicyDownloadsFolder com.apple.Terminal` and click **Allow**.

---

## ➕ Adding New Utilities

1. Place your script in `scripts/` (e.g. `scripts/my_tool.py`).
2. If it requires background scheduling, add its `.plist` to `launchd/`.
3. Create a detailed documentation file in `docs/` (e.g. `docs/my_tool.md`).
4. Add a one-sentence summary and link to the table above.
5. Commit and push:
   ```bash
   git add .
   git commit -m "Add my_tool"
   git push
   ```

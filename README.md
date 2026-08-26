# Mac Utilities (`mac-utilities`)

A collection of lightweight, portable automation scripts and LaunchAgents for macOS.

---

## 🛠 Available Utilities

| Utility | Description | Documentation |
| :--- | :--- | :--- |
| **Screenshot Housekeeping** | Keeps today's screenshots in root, groups older ones into daily folders, purges items older than 14 days to Trash, and permanently protects `Archive/`. | [Instructions & Details](docs/screenshot_housekeeping.md) |
| **Downloads Housekeeping** | Keeps recent files in root, purges installers after 14 days, groups items into 3-month rolling archives, and moves old unzipped folders to `_review/`. | [Instructions & Details](docs/downloads_housekeeping.md) |

---

## 🚀 Quick Setup on a New Mac

To restore and activate all utilities on a new or fresh Mac:

```bash
# 1. Clone this repository
git clone git@github.com:gromitski/mac-utilities.git ~/utilities

# 2. Make all scripts executable
chmod +x ~/utilities/scripts/*.py

# 3. Install and load LaunchAgents
cp ~/utilities/launchd/*.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.gromitski.screenshot-housekeeping.plist
launchctl load ~/Library/LaunchAgents/com.gromitski.downloads-housekeeping.plist
```

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

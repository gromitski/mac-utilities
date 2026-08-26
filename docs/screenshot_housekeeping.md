# 📸 Screenshot Housekeeping (`screenshot_housekeeping.py`)

Automatically manages `~/Pictures/screenshots` to keep your workspace clean and organized.

---

## 🎯 How It Works

1. **Today's Screenshots in Root:** Files matching today's date stay directly in `~/Pictures/screenshots/` so you have immediate access for drag-and-drop or uploading.
2. **Daily Date Folders:** Loose screenshots and screen recordings from previous days are organized into date-stamped subfolders (`YYYY-MM-DD/`).
3. **14-Day Retention & Safe Trash:** Day folders older than 14 days are safely moved to the **macOS Trash** (`~/.Trash`), providing a recovery window before permanent deletion.
4. **Archive & Custom Folder Protection:** Any folder named `Archive` (or any custom folder that does not follow the `YYYY-MM-DD` date format) is strictly ignored and permanently protected from modification or deletion.

---

## 💻 Manual CLI Usage & Flags

The script can be run manually at any time:

```bash
# Preview what would be moved or trashed without making any changes
python3 ~/utilities/scripts/screenshot_housekeeping.py --dry-run

# Run with verbose, file-by-file output
python3 ~/utilities/scripts/screenshot_housekeeping.py -v

# Custom retention period (e.g. 30 days instead of default 14)
python3 ~/utilities/scripts/screenshot_housekeeping.py --days 30

# Specify custom screenshots directory or custom archive folder name
python3 ~/utilities/scripts/screenshot_housekeeping.py --dir ~/Pictures/screenshots --archive-name Archive
```

---

## ⏰ Automated Scheduling (`launchd`)

The script is scheduled via a native macOS LaunchAgent:

* **Plist Path:** `~/Library/LaunchAgents/com.gromitski.screenshot-housekeeping.plist`
* **Schedule:** Runs daily at **23:59** (and catches up automatically upon waking if your Mac was asleep).
* **Logs:** Recorded to `~/Library/Logs/screenshot_housekeeping.log`.

---

## 🔄 Setup on a New Mac

```bash
cp ~/utilities/launchd/com.gromitski.screenshot-housekeeping.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.gromitski.screenshot-housekeeping.plist
```

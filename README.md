# Mac Utilities (`mac-utilities`)

A collection of lightweight, portable automation scripts and LaunchAgents for macOS. 

---

## 📸 1. Screenshot Housekeeping (`scripts/screenshot_housekeeping.py`)

Automatically manages `~/Pictures/screenshots` to keep your workspace clean and organized.

### How It Works
1. **Today's Screenshots Stay in Root:** Any screenshot or screen recording taken today stays in `~/Pictures/screenshots/` so it's readily accessible for drag-and-drop or uploading.
2. **Daily Organization:** At the end of each day, loose screenshots from previous days are organized into date-stamped subfolders (`YYYY-MM-DD/`).
3. **14-Day Retention & Safe Trash:** Day folders older than 14 days are automatically moved to the **macOS Trash** (`~/.Trash`), providing a safety recovery buffer before permanent deletion.
4. **Archive & Custom Folder Protection:** Any folder named `Archive` (or any custom folder that does not match `YYYY-MM-DD`) is strictly ignored and permanently protected from modification or deletion.

### Manual Usage & Flags
You can run the script manually at any time:

```bash
# Preview actions without moving or deleting anything
python3 ~/utilities/scripts/screenshot_housekeeping.py --dry-run

# Run with verbose output
python3 ~/utilities/scripts/screenshot_housekeeping.py -v

# Custom retention period (e.g. 30 days)
python3 ~/utilities/scripts/screenshot_housekeeping.py --days 30
```

### Automation (`launchd`)
The script is scheduled via a macOS LaunchAgent located at `~/Library/LaunchAgents/com.gromitski.screenshot-housekeeping.plist`.
* **Schedule:** Daily at **23:59** (if your Mac is asleep, it runs immediately upon wake).
* **Logs:** Execution logs are saved to `~/Library/Logs/screenshot_housekeeping.log`.

---

## 🚀 Setting Up on a New Mac

If you ever migrate to a new Mac or do a clean install:

1. **Clone this repository:**
   ```bash
   git clone git@github.com:gromitski/mac-utilities.git ~/utilities
   ```

2. **Make scripts executable:**
   ```bash
   chmod +x ~/utilities/scripts/*.py
   ```

3. **Install and load LaunchAgents:**
   ```bash
   cp ~/utilities/launchd/com.gromitski.screenshot-housekeeping.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.gromitski.screenshot-housekeeping.plist
   ```

---

## 🛠 Adding New Utilities

To add future automation scripts to this repository:
1. Place the script in `scripts/` (e.g. `scripts/my_new_tool.py` or `.sh`).
2. If it requires background scheduling, add its `.plist` to `launchd/`.
3. Document its usage in this `README.md`.
4. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Add my_new_tool"
   git push
   ```

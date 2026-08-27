# 📸 Screenshot Housekeeping (`screenshot_housekeeping.py`)

Automated organizer and cleanup utility for macOS screenshots.

---

## 🎯 What It Does

1. **Immediate Daily Grouping:** Moves all loose screenshots (`Screenshot *.png`) from `~/Pictures/screenshots` into daily `YYYY-MM-DD/` folders. If run multiple times in a day, items are safely appended to today's folder.
2. **14-Day Retention & Safe Trash:** Day folders older than 14 days are automatically moved to `~/.Trash` (never permanently deleted, so you can restore anything if needed).
3. **Protected Archive:** A folder named `Archive/` is permanently protected and will never be touched or trashed.
4. **Automated Daily Schedule:** Runs in the background every night at 23:59 via a macOS LaunchAgent.

---

## 💻 Manual CLI Usage

```bash
# 1. Run via master clean tool (recommended)
clean screenshots

# 2. Preview actions without touching any files
clean screenshots -n

# 3. Run standalone script
python3 ~/utilities/scripts/screenshot_housekeeping.py

# 4. Standalone dry-run
python3 ~/utilities/scripts/screenshot_housekeeping.py --dry-run
```

---

## ⏰ Automated Background Schedule (LaunchAgent)

* **Plist Path:** `~/Library/LaunchAgents/com.mac-utilities.screenshot-housekeeping.plist`
* **Schedule:** Daily at **23:59**
* **Logs:** `~/Library/Logs/screenshot_housekeeping.log`

### Managing the LaunchAgent:
```bash
# Check if loaded
launchctl list | grep mac-utilities

# Reload LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.mac-utilities.screenshot-housekeeping.plist
launchctl load ~/Library/LaunchAgents/com.mac-utilities.screenshot-housekeeping.plist
```

---

## ⚙️ Default Screenshot Location

Ensure macOS saves screenshots to `~/Pictures/screenshots`:

```bash
mkdir -p ~/Pictures/screenshots
defaults write com.apple.screencapture location ~/Pictures/screenshots
killall SystemUIServer
```

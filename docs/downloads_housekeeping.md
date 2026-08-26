# 📥 Downloads Housekeeping (`downloads_housekeeping.py`)

Automatically manages `~/Downloads` to eliminate installer clutter, maintain monthly archives, and protect unzipped project folders.

---

## 🎯 How It Works

1. **Recent Downloads Stay in Root:** Files and unzipped folders downloaded or created in the last **14 days** remain loose in `~/Downloads/`.
2. **14-Day Installer Purge:** Old installer files (`.dmg`, `.pkg`, `.iso`, and `*_installer.app`) older than 14 days are automatically moved to the **macOS Trash** (`~/.Trash`).
3. **3-Month Rolling Archives:** Loose files and unzipped folders between 15 and 90 days old are organized into monthly archive folders (`YYYY-MM/`).
4. **3-Month Expiry & Review Protection:**
   - When a monthly folder reaches > 3 months old, loose files inside are moved to the Trash.
   - Any **unzipped or custom project folders** inside expired months are moved safely to `~/Downloads/_review/` so you can manually review them rather than risking accidental deletion.
5. **Protected Folders:** The `_review/` directory and active monthly folders are protected.

---

## 💻 Manual CLI Usage & Flags

The script can be run manually at any time:

```bash
# Preview what would be moved or trashed without making any changes
python3 ~/utilities/scripts/downloads_housekeeping.py --dry-run

# Run with verbose, item-by-item output
python3 ~/utilities/scripts/downloads_housekeeping.py -v

# Custom retention thresholds
python3 ~/utilities/scripts/downloads_housekeeping.py --recent-days 7 --installers-days 7 --months 2
```

---

## ⏰ Automated Scheduling (`launchd`)

The script is scheduled via a native macOS LaunchAgent:

* **Plist Path:** `~/Library/LaunchAgents/com.gromitski.downloads-housekeeping.plist`
* **Schedule:** Runs daily at **23:59** (and catches up automatically upon waking if your Mac was asleep).
* **Logs:** Recorded to `~/Library/Logs/downloads_housekeeping.log`.

---

## 🔄 Setup on a New Mac

```bash
cp ~/utilities/launchd/com.gromitski.downloads-housekeeping.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.gromitski.downloads-housekeeping.plist
```

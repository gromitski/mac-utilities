# 📥 Downloads Housekeeping (`downloads_housekeeping.py`)

Automatically organizes `~/Downloads` into monthly archives, eliminates old installer clutter, and protects unzipped project folders.

---

## 🎯 How It Works

1. **Immediate Monthly Organization:** All loose files and unzipped directories in `~/Downloads/` are organized into their corresponding monthly archive folders (`YYYY-MM/`).
2. **Seamless Appending:** If a monthly folder (e.g. `2026-08/`) already exists, new downloads are safely added into it without errors or conflicts.
3. **14-Day Installer Purge:** Old installer files (`.dmg`, `.pkg`, `.iso`, and `*_installer.app`) older than 14 days are automatically moved to the **macOS Trash** (`~/.Trash`).
4. **3-Month Expiry & Review Protection:**
   - When a monthly folder reaches > 3 months old, loose files inside are moved to the Trash.
   - Any **unzipped or custom project folders** inside expired months are moved safely to `~/Downloads/_review/` so you can manually review them rather than risking accidental deletion.
5. **Protected Folders:** The `_review/` directory and active monthly folders are protected from being sorted or deleted.

---

## 💻 Manual CLI Usage & Flags

The script can be run manually at any time:

```bash
# Preview what would be moved or trashed without making any changes
python3 ~/utilities/scripts/downloads_housekeeping.py --dry-run

# Run with verbose, item-by-item output
python3 ~/utilities/scripts/downloads_housekeeping.py -v

# Custom retention thresholds
python3 ~/utilities/scripts/downloads_housekeeping.py --installers-days 14 --months 3
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

---

## 🛠 Troubleshooting: macOS Privacy & Permissions (`Operation not permitted`)

If the script encounters `PermissionError: [Errno 1] Operation not permitted: '~/Downloads'`:

```bash
# Reset permission cache so macOS prompts you fresh:
tccutil reset SystemPolicyDownloadsFolder com.apple.Terminal
```
Then re-run the command and click **Allow** on the macOS system dialog.

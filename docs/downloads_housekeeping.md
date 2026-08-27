# 📥 Downloads Housekeeping (`downloads_housekeeping.py`)

Automated organizer and cleanup utility for your macOS `~/Downloads` folder.

---

## 🎯 What It Does

1. **Immediate Monthly Grouping:** Organizes loose downloads into monthly archive folders (`YYYY-MM/`).
2. **14-Day Installer Purge:** Automatically moves installer files (`.dmg`, `.pkg`, `.iso`, and `*_installer.app`) older than 14 days directly to `~/.Trash`.
3. **Safe 3-Month Expiry:** For monthly archive folders older than 3 months (~90 days):
   * Loose files are moved to `~/.Trash`.
   * Unzipped and custom directories are safely preserved and moved to `~/Downloads/_review/` so you can manually review projects or archives before deleting.
4. **Automated Daily Schedule:** Runs automatically every night at 23:59 via a macOS LaunchAgent.

---

## 💻 Manual CLI Usage

```bash
# 1. Run via master clean tool (recommended)
clean downloads

# 2. Preview actions without touching any files
clean downloads -n

# 3. Run standalone script
python3 ~/utilities/scripts/downloads_housekeeping.py

# 4. Standalone dry-run
python3 ~/utilities/scripts/downloads_housekeeping.py --dry-run
```

---

## ⏰ Automated Background Schedule (LaunchAgent)

* **Plist Path:** `~/Library/LaunchAgents/com.mac-utilities.downloads-housekeeping.plist`
* **Schedule:** Daily at **23:59**
* **Logs:** `~/Library/Logs/downloads_housekeeping.log`

### Managing the LaunchAgent:
```bash
# Check if loaded
launchctl list | grep mac-utilities

# Reload LaunchAgent
launchctl unload ~/Library/LaunchAgents/com.mac-utilities.downloads-housekeeping.plist
launchctl load ~/Library/LaunchAgents/com.mac-utilities.downloads-housekeeping.plist
```

---

## 🛠 Troubleshooting: macOS Privacy & Permissions (`Operation not permitted`)

macOS protects `~/Downloads` via Transparency, Consent, and Control (TCC).

If Terminal reports `[Permission Error] macOS blocked access to '~/Downloads'`:

1. **Reset permission cache:**
   ```bash
   tccutil reset SystemPolicyDownloadsFolder com.apple.Terminal
   ```
2. Re-run `clean` or `clean downloads` and click **Allow** when the macOS prompt appears.
3. Alternatively, grant Terminal access in **System Settings > Privacy & Security > Files and Folders > Terminal**.

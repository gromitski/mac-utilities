# Mac Utilities (`mac-utilities`)

A collection of lightweight, portable automation scripts, LaunchAgents, and Alfred workflows for macOS.

> 💡 **Alfred is Non-Essential:** All utilities in this repository are **100% standalone command-line tools**. Alfred is purely an optional convenience shortcut for users who use it—if you don't use Alfred, every single command works fully out of the box directly from your Terminal!

---

## 🛠 Available Utilities

| Utility | Description | Documentation |
| :--- | :--- | :--- |
| **`clean`** | Master on-demand CLI & Alfred trigger (`clean`, `clean screenshots`, `clean downloads`, `clean url`, `clean deep`, `clean -n`). | [Instructions & Details](docs/clean.md) |
| **`git-audit`** | Fast multi-threaded scanner checking uncommitted changes, unpushed commits, and branch sync across all workspace repos. | [Instructions & Details](docs/git_audit.md) |
| **`localserver`** | Spins up a local Wi-Fi HTTP server and prints a terminal QR code for instant mobile testing/sharing. | [Instructions & Details](docs/localserver.md) |
| **`awake`** | Friendly timed sleep & display inhibitor for presentations, downloads, and calls (`awake 30m`, `awake 1h`, `awake off`). | [Instructions & Details](docs/awake.md) |
| **Screenshot Housekeeping** | Organizes loose screenshots into daily `YYYY-MM-DD/` folders, purges items older than 14 days to Trash, and permanently protects `Archive/`. | [Instructions & Details](docs/screenshot_housekeeping.md) |
| **Downloads Housekeeping** | Organizes loose files into rolling 3-month `YYYY-MM/` folders, purges installers after 14 days, and moves expired unzipped folders to `_review/`. | [Instructions & Details](docs/downloads_housekeeping.md) |
| **System Cache Reclaimer** | Conservative safe disk space reclaimer for Homebrew, npm, pip, and Xcode caches. | [Instructions & Details](docs/system_cache_cleaner.md) |

---

## 🚀 Quick Setup on Any Mac

To install and activate all utilities on a new or fresh Mac:

```bash
# 1. Clone the repository into ~/utilities
git clone https://github.com/gromitski/mac-utilities.git ~/utilities

# 2. Run the automated installer
cd ~/utilities && ./install.sh

# 3. Reload your shell
source ~/.zshrc   # or source ~/.bash_profile / source ~/.config/fish/config.fish

# 4. (Optional) Install the Alfred Workflow if you use Alfred
open ~/utilities/alfred/Clean.alfredworkflow
```

---

## 🔐 macOS Permissions & Troubleshooting (`Operation not permitted`)

macOS restricts access to protected folders (`~/Downloads`, `~/Documents`, `~/Desktop`) through **Transparency, Consent, and Control (TCC)**.

If running any housekeeping command returns `[Permission Error] Operation not permitted`:

### Option 1: Quick Terminal Cache Reset (Recommended)
macOS caches permission tokens per application session. If Terminal or Alfred has a stale permission token:
```bash
# Reset permission prompt for Terminal
tccutil reset SystemPolicyDownloadsFolder com.apple.Terminal

# Or reset permission prompt for Alfred (if installed)
tccutil reset SystemPolicyDownloadsFolder com.runningwithcrayons.Alfred
```
Then re-run `clean` and click **Allow** when the macOS system dialog appears.

### Option 2: System Settings Configuration
1. Open **System Settings > Privacy & Security**.
2. Navigate to **Files and Folders**.
3. Ensure **Terminal** (and **Alfred** if used) has **Downloads Folder** toggled **ON**.
4. *(Optional)* Alternatively, grant **Full Disk Access** to Terminal for unrestricted management.

---

## ➕ Adding New Utilities

1. Place your script in `scripts/` (e.g. `scripts/my_tool.py`).
2. If it requires background scheduling, add its template `.plist` to `launchd/`.
3. Create a detailed documentation file in `docs/` (e.g. `docs/my_tool.md`).
4. Add a one-sentence summary and link to the table above.
5. Commit and push:
   ```bash
   git add .
   git commit -m "Add my_tool"
   git push
   ```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

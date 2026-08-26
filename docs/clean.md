# 🧹 Clean Command & Alfred Trigger (`clean`)

The master on-demand runner that executes all housekeeping tasks across **Screenshots** and **Downloads** in one command.

---

## 🎯 Features

* **Single Universal Command:** Type `clean` anywhere in Terminal or trigger via Alfred.
* **Instant Tidy:** Sweeps all loose screenshots into daily `YYYY-MM-DD/` folders and all loose downloads into monthly `YYYY-MM/` folders immediately.
* **Unified Report:** Runs both housekeeping utilities in-process and presents a sleek status report.
* **Granular Control:** Supports targeting only screenshots or only downloads.
* **Dry-Run Mode:** Test actions beforehand with `-n` or `--dry-run`.
* **Native Notifications:** Displays a macOS notification banner when triggered via Alfred or when `--notify` is passed.

---

## 💻 Terminal CLI Usage

```bash
# 1. Standard full cleanup (Screenshots + Downloads)
clean

# 2. Preview actions without touching any files
clean --dry-run
# or
clean -n

# 3. Clean only Screenshots
clean screenshots

# 4. Clean only Downloads
clean downloads

# 5. Deep Cleanup (future-proofed for system caches & dev artifacts)
clean --deep

# 6. Detailed verbose output
clean -v
```

---

## 🔍 Triggering via Alfred

1. Press your Alfred hotkey (e.g. `Cmd + Space`).
2. Type **`clean`** and hit **Enter**.
3. The script executes instantly in the background and posts a native macOS notification:
   > 🧹 **Mac Housekeeping Complete**  
   > *Screenshots organized & Downloads organized.*

### Restoring Alfred Workflow on a New Mac
The portable workflow file is saved in `~/utilities/alfred/Clean.alfredworkflow`. Simply double-click it on any Mac with Alfred to install.

---

## 🔄 Setup on a New Mac

Add `~/utilities/scripts` to your `$PATH` in `~/.zshrc`:

```bash
echo 'export PATH="$HOME/utilities/scripts:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

---

## 🛠 Troubleshooting: macOS Privacy & Permissions (`Operation not permitted`)

macOS restricts access to protected folders (`~/Downloads`, `~/Documents`, `~/Desktop`) via Transparency, Consent, and Control (TCC).

If running `clean` reports `[Permission Error] macOS blocked access to '~/Downloads'`:

1. **Quick Fix via Terminal (Recommended):**
   Reset the permission cache so macOS prompts you fresh:
   ```bash
   tccutil reset SystemPolicyDownloadsFolder com.apple.Terminal
   ```
   Then re-run `clean` and click **Allow** when the macOS prompt appears.

2. **Manual System Settings Check:**
   * Go to **System Settings > Privacy & Security > Files and Folders** (or **Full Disk Access**).
   * Ensure **Terminal** and **Alfred** have permission toggled ON for the **Downloads Folder**.

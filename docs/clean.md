# 🧹 Clean Command & Alfred Trigger (`clean`)

The master on-demand runner that executes housekeeping tasks across **Screenshots** and **Downloads** in one command.

---

## 🎯 Features

* **Universal CLI & Alfred Trigger:** Type `clean` anywhere in Terminal or launch via Alfred.
* **Interactive Alfred Menu:** Typing `clean` in Alfred shows an instant interactive menu with selectable options.
* **Targeted Cleanups:** Run only screenshots or only downloads on-demand.
* **Dry-Run Mode:** Test actions beforehand with `-n` or `--dry-run`.
* **Native Notifications:** Displays a macOS notification banner showing exactly which target was cleaned.

---

## 💻 Terminal CLI Usage

```bash
# 1. Standard full cleanup (Screenshots + Downloads)
clean

# 2. Clean only Screenshots
clean screenshots

# 3. Clean only Downloads
clean downloads

# 4. Preview actions without touching any files
clean --dry-run
# or
clean -n

# 5. Deep Cleanup (future-proofed for system caches & dev artifacts)
clean --deep

# 6. Detailed verbose output
clean -v
```

---

## 🔍 Triggering via Alfred

1. Press your Alfred hotkey (e.g. `Cmd + Space`).
2. Type **`clean`**.
3. Alfred will immediately display interactive options in the dropdown:
   * 🧹 **Clean All (Screenshots + Downloads)** ➔ Cleans both folders
   * 📸 **Clean Screenshots** ➔ Cleans only screenshots
   * 📥 **Clean Downloads** ➔ Cleans only downloads
   * 🚀 **Clean Deep** ➔ Runs full cleanup + deep cache purges
4. Select with arrow keys or type `clean screenshots` / `clean downloads` directly and hit **Enter**.
5. You'll receive a native macOS notification confirming what was cleaned.

### Restoring Alfred Workflow on a New Mac
The portable workflow file is saved in `~/utilities/alfred/Clean.alfredworkflow`. Double-click it on any Mac with Alfred to install.

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

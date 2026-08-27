# 🧹 Clean Command & Alfred Trigger (`clean`)

The master on-demand runner that executes housekeeping tasks across **Screenshots**, **Downloads**, **Desktop**, **System Caches**, and **Clipboard URLs** in one command.

---

## 🎯 Features

* **Universal CLI & Alfred Trigger:** Type `clean` anywhere in Terminal or launch via Alfred.
* **Interactive Alfred Menu:** Typing `clean` in Alfred shows an instant interactive menu with selectable options.
* **Standard Cleanup:** Running `clean` tidies **Screenshots, Downloads, and Desktop** in one shot.
* **Targeted Cleanups:** Run only screenshots, only downloads, only desktop, only deep caches, or only clean copied URLs.
* **Dry-Run Mode:** Test file actions beforehand with `-n` or `--dry-run`.
* **Native Notifications:** Displays a macOS notification banner showing exactly which targets were cleaned.

---

## 💻 Terminal CLI Usage

```bash
# 1. Standard full cleanup (Screenshots + Downloads + Desktop)
clean

# 2. Clean only Screenshots
clean screenshots

# 3. Clean only Downloads
clean downloads

# 4. Clean only Desktop
clean desktop

# 5. Clean orphaned app leftovers
clean app-leftovers

# 6. Clipboard Cleaner (Privacy Flush, Text Sanitizer, Status)
clean clipboard          # Instant privacy flush (wipes clipboard memory)
clean clipboard text     # Strips rich styling, smart quotes & zero-width spaces
clean clipboard status   # Safe metadata inspection (length, types)

# 7. Git Branch Cleaner (Standalone on-demand only)
clean branches           # Prune merged & dead branches in current repo
clean branches --all     # Scan all repos across workspace for stale branches

# 8. Clean URL tracking parameters from clipboard (or direct argument)
clean url
# or pass a link directly:
clean url "https://blah.com/?a=1&b=2&utm_source=qwaksdb"
clean "https://blah.com/?a=1&b=2&utm_source=qwaksdb"

# 9. Deep Cleanup (Screenshots + Downloads + Desktop + App Leftovers + Caches)
clean --deep
# or
clean deep

# 10. Preview actions without touching any files
clean --dry-run
# or
clean -n

# 11. Detailed verbose output
clean -v
```

---

## 🔗 URL Cleaning Details (`clean url`)

Surgically removes analytics and ad-tech tracking parameters while **safely preserving functional query parameters** (search queries, page numbers, video IDs/timestamps).

* **What is stripped:**
  * **Google / Analytics:** `utm_source`, `utm_medium`, `utm_campaign`, `utm_term`, `utm_content`, `utm_id`, `utm_*`, `gclid`, `gclsrc`, `dclid`, `_ga`, `_gl`
  * **Meta / Social:** `fbclid`, `igshid`, `twclid`, `ref_src`, `li_fat_id`, `msclkid`, `tt_medium`
  * **Media & Sharing:** YouTube `si`, `feature`, `pp` (preserves video `v` and timestamp `t`); Spotify `si`, `nd`
  * **Amazon Clutter:** `ref`, `ref_`, `tag`, `keywords`, `qid`, `sr`, `crid`, `sprefix`, `dib`, `pd_rd_*` (normalizes to clean `/dp/ASIN`)
  * **Email & Newsletters:** `_hsenc`, `_hsmi` (HubSpot), `mc_eid` (Mailchimp), `mkt_tok` (Marketo), Substack `r`
* **Example:**
  `https://blah.com/?a=1&b=2&utm_source=qwaksdb` ➔ `https://blah.com/?a=1&b=2`

---

## 🔍 Triggering via Alfred

1. Press your Alfred hotkey (e.g. `Cmd + Space`).
2. Type **`clean`**.
3. Alfred will immediately display interactive options in the dropdown:
   * 🧹 **Clean All (Screenshots + Downloads + Desktop)** ➔ Cleans all 3 folders
   * 📸 **Clean Screenshots** ➔ Cleans only screenshots
   * 📥 **Clean Downloads** ➔ Cleans only downloads
   * 🖥️ **Clean Desktop** ➔ Sweeps loose desktop items into monthly archive
   * 👻 **Clean App Leftovers** ➔ Safely trashes orphaned uninstalled app support data
   * 🌿 **Clean Git Branches** ➔ Prunes merged and dead remote-tracking branches
   * 📋 **Clean Clipboard (Flush / Wipe)** ➔ Clears passwords & sensitive data from memory
   * 📝 **Clean Clipboard (Plain Text)** ➔ Sanitizes copied text (removes HTML/RTF, smart quotes)
   * 🔗 **Clean URL (Clipboard)** ➔ Strips tracking clutter from copied link
   * 🚀 **Clean Deep** ➔ Runs full cleanup + app leftovers + developer cache purges
4. Select with arrow keys or type `clean desktop`, `clean clipboard`, `clean url`, `clean screenshots` directly and hit **Enter**.
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

If running `clean` reports `[Permission Error] macOS blocked access`:

1. **Quick Fix via Terminal (Recommended):**
   Reset the permission cache so macOS prompts you fresh:
   ```bash
   tccutil reset SystemPolicyDownloadsFolder com.apple.Terminal
   tccutil reset SystemPolicyDesktopFolder com.apple.Terminal
   ```
   Then re-run `clean` and click **Allow** when the macOS prompt appears.

2. **Manual System Settings Check:**
   * Go to **System Settings > Privacy & Security > Files and Folders** (or **Full Disk Access**).
   * Ensure **Terminal** and **Alfred** have permission toggled ON for **Downloads Folder** and **Desktop Folder**.

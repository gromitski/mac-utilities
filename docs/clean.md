# 🧹 Clean Command & Alfred Trigger (`clean`)

The master on-demand runner that executes housekeeping tasks across **Screenshots**, **Downloads**, **System Caches**, and **Clipboard URLs** in one command.

---

## 🎯 Features

* **Universal CLI & Alfred Trigger:** Type `clean` anywhere in Terminal or launch via Alfred.
* **Interactive Alfred Menu:** Typing `clean` in Alfred shows an instant interactive menu with selectable options.
* **Targeted Cleanups:** Run only screenshots, only downloads, only deep caches, or only clean copied URLs.
* **Dry-Run Mode:** Test file actions beforehand with `-n` or `--dry-run`.
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

# 4. Clean URL tracking parameters from clipboard (or direct argument)
clean url
# or pass a link directly:
clean url "https://blah.com/?a=1&b=2&utm_source=qwaksdb"
clean "https://blah.com/?a=1&b=2&utm_source=qwaksdb"

# 5. Deep Cleanup (Safe Homebrew, npm, pip & developer caches)
clean --deep
# or
clean deep

# 6. Preview actions without touching any files
clean --dry-run
# or
clean -n

# 7. Detailed verbose output
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
   * 🧹 **Clean All (Screenshots + Downloads)** ➔ Cleans both folders
   * 📸 **Clean Screenshots** ➔ Cleans only screenshots
   * 📥 **Clean Downloads** ➔ Cleans only downloads
   * 🔗 **Clean URL (Clipboard)** ➔ Strips tracking clutter from copied link
   * 🚀 **Clean Deep** ➔ Runs full cleanup + deep cache purges
4. Select with arrow keys or type `clean url`, `clean screenshots`, `clean downloads` directly and hit **Enter**.
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

# 👻 App Leftovers Cleaner (`clean app-leftovers`)

Scans user Library directories for orphaned configuration, saved state, and log folders left behind by uninstalled applications—built with a multi-layered safety model so active applications and developer environments are **never reset or broken**.

---

## 🎯 What it Scans

When an app is deleted on macOS by dragging it to Trash, support files remain in `~/Library`. This utility inspects:
* `~/Library/Application Support/` *(App support data, configs, and profiles)*
* `~/Library/Saved Application State/` *(Cached window & session states)*
* `~/Library/Logs/` *(Application logs and crash traces)*

---

## 🛡️ Multi-Tiered Safety Model

1. **Comprehensive App Indexing:** Indexes all installed apps in `/Applications`, `/System/Applications`, `~/Applications`, and `/opt/homebrew/Caskroom`, inspecting `Info.plist` bundle IDs, display names, and executable names.
2. **Hardcoded Zero-Touch Whitelist:** Permanently protects all macOS system services (`com.apple.*`, `CloudDocs`, `MobileSync`, etc.), universal runtimes (`Node`, `Python`, `Java`), and CLI tools without `.app` bundles (`Homebrew`, `git`, `docker`, `Cursor`, `Antigravity`, `Gemini`, `Claude`, `Ollama`, etc.).
3. **60-Day Recency Guard:** Any directory modified or accessed within the last 60 days is automatically skipped, even if its matching `.app` cannot be located.
4. **Reversible (Trash Only, Never `rm -rf`):** All orphaned folders are moved to `~/.Trash`, allowing instant recovery if needed.
5. **Interactive Confirmation:** Prompted confirmation (`[y/N]`) before moving anything in standalone mode.

---

## 💻 Terminal CLI Usage

```bash
# 1. Scan and clean interactively (prompts before trashing)
clean app-leftovers

# 2. Preview only without moving anything
clean app-leftovers -n
# or
clean app-leftovers --dry-run

# 3. Clean without interactive prompt (for scripted runs)
clean app-leftovers --force

# 4. Custom recency window (e.g. only folders untouched for >90 days)
python3 ~/utilities/scripts/app_leftovers_cleaner.py --days 90
```

---

## 🔄 Integration in `clean deep`

* **Standard `clean`:** App leftovers are **excluded** (standard clean stays strictly Screenshots + Downloads + Desktop).
* **Deep Clean (`clean deep`):** Included as Step 4 alongside developer cache reclaimers.

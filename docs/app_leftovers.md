# 👻 App Leftovers Cleaner (`clean app-leftovers`)

A safe, conservative scanner and cleaner that identifies orphaned application support folders, saved states, and logs left behind by uninstalled applications—built with a multi-layered safety architecture so **active applications, developer environments, and macOS system services are never reset or broken**.

---

## 🎯 The Problem it Solves

When you uninstall an app on macOS by dragging its `.app` bundle to the Trash, macOS only deletes the binary itself. Over months and years, gigabytes of abandoned configuration files, local databases, crash logs, and cached session states accumulate in `~/Library`.

`clean app-leftovers` scans for these abandoned folders and safely moves them to the macOS Trash, reclaiming disk space without putting active software at risk.

---

## 🛡️ Safety Decisions & Multi-Tiered Architecture

Cleaning user library files requires extreme caution. To guarantee zero accidental data loss or application resets, `clean app-leftovers` employs **four independent fail-safe layers**:

```
                                  Target Folder in ~/Library
                                              │
                                              ▼
                        ┌───────────────────────────────────────────┐
                        │   Tier 1: Hardcoded Zero-Touch Whitelist  │ ──► [MATCH] ──► NEVER TOUCH (Skip)
                        │   (Apple, System, Runtimes, CLI Tools)    │
                        └───────────────────────────────────────────┘
                                              │ [Pass]
                                              ▼
                        ┌───────────────────────────────────────────┐
                        │   Tier 2: Comprehensive App Discovery    │ ──► [ACTIVE] ─► NEVER TOUCH (Skip)
                        │   (Apps, Casks, Plists, Processes)        │
                        └───────────────────────────────────────────┘
                                              │ [Pass]
                                              ▼
                        ┌───────────────────────────────────────────┐
                        │   Tier 3: 60-Day Recency Guard            │ ──► [RECENT] ─► NEVER TOUCH (Skip)
                        │   (Modified/Accessed within 60 days)      │
                        └───────────────────────────────────────────┘
                                              │ [Pass]
                                              ▼
                        ┌───────────────────────────────────────────┐
                        │   Tier 4: Reversible Trash Movement       │ ──► Moved to ~/.Trash
                        │   (Zero hard deletions; 1-click restore)  │     (Never rm -rf)
                        └───────────────────────────────────────────┘
```

---

### 1. Hardcoded "Zero-Touch" Whitelist (Tier 1)
Any folder matching known system services, universal runtimes, or tools that operate without a traditional `.app` bundle is **permanently exempt**:

| Category | Protected Names & Identifiers |
| :--- | :--- |
| **macOS & Apple System** | `Apple`, `Apple Computer`, `com.apple.*`, `CloudDocs`, `MobileSync`, `AddressBook`, `Safari`, `QuickLook`, `CrashReporter`, `DiskImages`, `Accounts`, `QuickTime`, `SyncServices`, `iCloud`, `CoreData`, `Finder`, `Dock`, `Preferences`, `Siri`, `Keychains`, `Messages`, `Photos`, `Mail`, `Notes`, `Calendar`, etc. |
| **Developer Runtimes & CLIs** | `Homebrew`, `pip`, `npm`, `nvm`, `rustup`, `cargo`, `docker`, `git`, `ssh`, `gnupg`, `pnpm`, `yarn`, `zsh`, `bash`, `fish`, `Python`, `Node`, `Java`, `Ruby`, `Go`, `OpenSSL`, `uv`, `poetry`, `conda`, `virtualenvs`, `dbt`, `dataform`, `gcloud`, `firebase`, `flutter`, `dart` |
| **AI & Modern Dev Tools** | `Code` (VS Code), `Cursor`, `Antigravity`, `Gemini`, `Claude`, `Ollama`, `JetBrains`, `com.anthropic.*`, `com.google.*`, `com.github.*`, `com.microsoft.*`, `Alfred`, `Raycast` |
| **Shared Application Suites** | `Google`, `Microsoft`, `Adobe`, `Mozilla`, `Brave`, `Arc`, `Dropbox`, `Box`, `OneDrive`, `Spotify`, `Slack`, `Zoom`, `Notion`, `Linear`, `Figma`, `TablePlus`, `Postman` |

---

### 2. Comprehensive Multi-Location App Discovery (Tier 2)
Before evaluating any folder, the scanner builds a complete index of all active software on your system:
* **All Application Directories:** Scans `/Applications`, `/System/Applications`, `~/Applications`, `/Applications/Utilities`, and `/System/Library/CoreServices`.
* **Deep Bundle Inspection (`Info.plist`):** Reads internal `CFBundleIdentifier` (e.g. `com.tinyspeck.slackmacgap`), `CFBundleDisplayName` (e.g. `Slack`), `CFBundleName`, and `CFBundleExecutable`.
* **Homebrew Casks & Packages:** Inspects `/opt/homebrew/Caskroom` and `/opt/homebrew/Cellar`.
* **Active In-Memory Processes:** Checks running system processes (`ps`) so background daemons and helper agents currently active in memory are never flagged.

---

### 3. 60-Day Recency Guard (Tier 3)
* If a directory or any of its contents has been modified or accessed within the last **60 days**, it is automatically considered **active** and **skipped**.
* This protects infrequently opened tools, portable utilities, and background services that might not have an `.app` bundle installed in a standard location.

---

### 4. 100% Reversible Deletion (Tier 4)
* **Never uses `rm -rf`:** Leftover items are moved to the macOS Trash (`~/.Trash`) using Python's standard file movement.
* **1-Click Recovery:** If you ever need to restore an application's configuration, open the macOS Trash, right-click the folder, and select **Put Back**.

---

## 💻 Terminal CLI Usage

```bash
# 1. Interactive scan (shows orphans, sizes, and prompts [y/N] before trashing)
clean app-leftovers

# 2. Dry-Run preview (simulates scan without moving any files)
clean app-leftovers -n
# or
clean app-leftovers --dry-run

# 3. Detailed verbose output
clean app-leftovers -v

# 4. Non-interactive run (for automated scripts / clean deep)
clean app-leftovers --force

# 5. Custom recency window (e.g. only folders untouched for >90 days)
python3 ~/utilities/scripts/app_leftovers_cleaner.py --days 90
```

---

## 🔄 Integration in `clean` & `clean deep`

* **Standard `clean` (`clean`):** App leftovers are **strictly excluded**. Standard `clean` only touches user file clutter in **Screenshots, Downloads, and Desktop**.
* **Deep Clean (`clean deep`):** App leftovers are included as **Step 4 of 5**:
  - `[1/5]` 📸 Screenshots
  - `[2/5]` 📥 Downloads
  - `[3/5]` 🖥️ Desktop
  - `[4/5]` 👻 Orphaned App Leftovers (>60d unmodified)
  - `[5/5]` 🚀 System & Developer Caches (`brew`, `npm`, `pip`, `xcode`)

---

## ❓ Frequently Asked Questions (FAQ)

#### Q: Will this reset my browser profiles, IDE settings, or shell configurations?
**No.** All major browsers (Chrome, Arc, Brave, Safari, Firefox), IDEs (VS Code, Cursor, JetBrains), and shell configs (`zsh`, `bash`, `fish`, `ssh`, `git`) are protected by both the **Zero-Touch Whitelist** and the **Installed Apps Index**.

#### Q: What if I uninstalled an app and reinstall it later?
If you reinstall an app whose leftovers were cleaned, the app will simply create a fresh, clean configuration folder when launched, exactly as if it were a new installation.

#### Q: How do I verify what would be cleaned before running?
Run `clean app-leftovers -n` (or `clean deep -n`). It will list every detected item with its name, location, size, and last modified date without moving a single byte.

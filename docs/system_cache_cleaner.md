# 🧹 System & Cache Space Reclaimer (`system_cache_cleaner.py`)

A conservative, safe disk space reclaimer that purges outdated package manager archives and developer build artifacts without touching any application logins, settings, or user data.

---

## 🛡️ Safety Guarantees

* **Zero Login/Config Risk:** NEVER touches `~/Library/Application Support/` (all app settings, databases, and login sessions remain 100% intact).
* **No Generic Cache Wiping:** Does not blindly wipe `~/Library/Caches/`, preventing apps from losing local session tokens or taking longer to load.
* **No Project Code Impact:** Never touches your workspace projects, active `node_modules`, or Python virtual environments.
* **Official Tool Purges Only:** Uses each tool's official built-in purge mechanisms (`brew cleanup -s`, `pip cache purge`, `npm cache clean`).

---

## 🎯 What It Cleans

1. **Homebrew:** Removes outdated package versions and downloaded `.bottle` archives for tools you've already upgraded.
2. **Node / npm:** Purges downloaded `.tar.gz` package archives in `~/.npm/_cacache`.
3. **Python / pip:** Purges cached `.whl` wheel downloads in `~/Library/Caches/pip` (or `~/.cache/pip`).
4. **Xcode (if installed):** Safely clears intermediate build files in `~/Library/Developer/Xcode/DerivedData` (rebuilt automatically on next compile).

---

## 💻 Usage

### 1. Via the `clean` CLI

```bash
# Run full housekeeping + safe cache cleanup
clean --deep
# or
clean deep

# Preview what would be cleaned without deleting anything
clean deep -n

# Run ONLY the cache reclaimer
clean cache
```

### 2. Via Alfred
* Press Alfred hotkey (e.g. `Cmd + Space`).
* Type **`clean deep`** (or select **Clean Deep** from the `clean` dropdown).
* Runs in the background and notifies you with the reclaimed space.

### 3. Standalone Script
```bash
# Standalone run
python3 ~/utilities/scripts/system_cache_cleaner.py

# Standalone dry-run
python3 ~/utilities/scripts/system_cache_cleaner.py --dry-run
```

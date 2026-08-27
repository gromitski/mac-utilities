# 🗑️ Smart Trash Purge (`clean trash`)

A safe, age-based Trash management utility for macOS. Shows disk usage and permanently purges items that have been in Trash longer than a configurable retention threshold (default: 30 days), protecting recently deleted items from accidental permanent loss.

---

## 🎯 What It Does

1. **Age-Based Purge:** Permanently deletes items that have been in `~/.Trash` longer than the retention window (default: 30 days), leaving recently trashed items untouched.
2. **Disk Usage Summary:** Displays total Trash size and a breakdown of how much disk space can be reclaimed.
3. **Custom Thresholds:** Supports configurable retention windows (`14d`, `60d`, etc.).
4. **Full Empty Option:** Can empty the entire Trash via native Finder automation (`clean trash all`).
5. **Included in Deep Clean:** Automatically runs as part of `clean deep` using the default 30-day threshold.

---

## 💻 CLI Usage

```bash
# 1. Purge Trash items older than 30 days (default)
clean trash

# 2. Preview what would be purged without deleting anything
clean trash -n
clean trash --dry-run

# 3. Show Trash disk usage summary without changing anything
clean trash status

# 4. Purge with a custom retention threshold
clean trash 14d    # Purge items trashed more than 14 days ago
clean trash 60d    # Purge items trashed more than 60 days ago

# 5. Empty entire Trash (all items, regardless of age)
clean trash all

# 6. Verbose output showing every item purged
clean trash -v
```

---

## ⚙️ Inclusion in Other Commands

| Command | Behaviour |
| :--- | :--- |
| `clean` | ❌ Trash is **not touched** — only Screenshots, Downloads, Desktop |
| `clean deep` | ✅ Purges Trash items **older than 30 days** |
| `clean trash` | ✅ Purges Trash items older than 30 days (standalone) |
| `clean trash all` | ✅ Empties entire Trash via native Finder automation |

---

## 🔍 Triggering via Alfred

1. Press your Alfred hotkey (e.g. `Cmd + Space`).
2. Type **`clean trash`** (or select **Clean Trash (Items >30 Days)** from the `clean` menu).
3. Press **Enter**.
4. A native macOS notification will confirm how much disk space was reclaimed.

---

## 🛠 Troubleshooting: macOS Privacy & Permissions

The Trash Cleaner uses a dual-engine approach:
1. **Direct filesystem access** (`~/.Trash`) — works when Terminal has Full Disk Access.
2. **Finder AppleScript fallback** — used automatically for `clean trash all` since Finder always has Trash access.

If items fail to purge (e.g. "Operation not permitted"), grant Terminal **Full Disk Access**:
1. Go to **System Settings > Privacy & Security > Full Disk Access**.
2. Toggle **Terminal** to **ON**.

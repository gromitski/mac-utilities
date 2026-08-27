# 🖥️ Desktop Housekeeping (`desktop_housekeeping.py`)

Automated desktop organizer for macOS that sweeps loose files and folders into monthly archive directories (`YYYY-MM/`), keeping your screen and wallpaper spotless without deleting anything.

---

## 🎯 What It Does

1. **Monthly Grouping:** Sweeps loose files and unorganized folders on `~/Desktop` into the current month's folder (e.g. `~/Desktop/2026-08/`).
2. **Zero Deletion Guarantee:** Files and folders are **never deleted or trashed**—they are simply organized so your desktop stays clean.
3. **Protected Items:** System files (`.DS_Store`, `.localized`), existing monthly folders (`YYYY-MM/`), and `Archive/` are permanently protected and never moved.
4. **Collision Safe:** If a file already exists in the destination month, it safely appends a counter (e.g. `document (1).pdf`) to prevent overwriting.

---

## 💻 Manual CLI Usage

```bash
# 1. Run via master clean tool (recommended)
clean desktop

# 2. Preview actions without moving any files
clean desktop -n
# or
clean desktop --dry-run

# 3. Detailed verbose output
clean desktop -v

# 4. Run standalone script
python3 ~/utilities/scripts/desktop_housekeeping.py
```

---

## 🔍 Triggering via Alfred

1. Press your Alfred hotkey (e.g. `Cmd + Space`).
2. Type **`clean desktop`** (or select **Clean Desktop** from the `clean` menu).
3. Press **Enter**.
4. You'll receive a native macOS notification confirming how many items were organized into the monthly folder.

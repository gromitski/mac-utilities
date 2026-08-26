# ☕️ Friendly Mac Stay Awake Timer (`awake`)

A simple, timed wrapper around macOS `caffeinate` that keeps your screen and system awake for presentations, long downloads, and video rendering without risking battery drain from forgetting to turn it off.

---

## 🎯 Features

* **Timed Presets:** Automatically disables itself when the timer expires (`awake 30m`, `awake 2h`).
* **Safe State Tracking:** Keeps track of active sessions in `~/.utilities_awake.json` and gracefully cancels previous timers before starting new ones.
* **Alfred Integration:** Control sleep prevention directly from Alfred with one-click presets.
* **Native Notifications:** Displays notification banners confirming active time and when sleep is restored.

---

## 💻 Terminal CLI Usage

```bash
# 1. Stay awake for a specific duration
awake 30m
awake 1h
awake 45s

# 2. Stay awake indefinitely
awake on

# 3. Check current status & remaining time
awake status
# or simply
awake

# 4. Deactivate and restore normal sleep behavior
awake off
# or
awake stop
```

---

## 🔍 Triggering via Alfred

1. Press your Alfred hotkey (e.g. `Cmd + Space`).
2. Type **`awake`**.
3. Select any duration preset:
   * ☕️ **Keep Awake for 15 Minutes**
   * ☕️ **Keep Awake for 30 Minutes**
   * ☕️ **Keep Awake for 1 Hour**
   * ☕️ **Keep Awake for 2 Hours**
   * ☕️ **Keep Awake Indefinitely**
   * 🛑 **Stop Awake (Restore Normal Sleep)**
4. Press **Enter**. You will receive a macOS notification confirming the duration.

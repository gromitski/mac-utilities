# 📋 Clipboard Cleaner (`clean clipboard`)

A macOS clipboard utility for **privacy flushing**, **plain-text formatting sanitization**, and **safe metadata inspection**.

---

## 🎯 Features

* **Instant Privacy Wipe:** Immediately flushes sensitive passwords, API keys, or 2FA tokens from system memory.
* **Plain Text Sanitizer:** Converts styled/rich text into pure unformatted plain text, stripping HTML, RTF, zero-width characters, and non-breaking space artifacts.
* **Smart Quote Normalization:** Converts curly quotes (`“” ‘’`) to clean ASCII quotes (`"" ''`) to prevent syntax errors in terminal commands and code.
* **Safe Status Inspection:** View clipboard metadata (types, size, line count) without displaying private clipboard text on screen.
* **Alfred 5 Integration:** Dedicated triggers for instant clipboard wiping or plain-text conversion via hotkey.

---

## 💻 Terminal CLI Usage

```bash
# 1. Instant Privacy Wipe (clears clipboard memory)
clean clipboard

# 2. Plain Text Sanitizer (strips rich text, smart quotes & zero-width spaces)
clean clipboard text
# or
clean clipboard plain

# 3. Clipboard Inspector (shows types, character/line count safely)
clean clipboard status

# 4. Preview / Dry-Run
clean clipboard -n
clean clipboard text -n
```

---

## 🛡️ Sanitization Details (`clean clipboard text`)

When copying text from websites, Word documents, or PDFs, hidden formatting artifacts often get pasted into code or terminal windows:

| Artifact | Source | What `clean clipboard text` does |
| :--- | :--- | :--- |
| **Zero-Width Spaces** (`\u200b`, `\ufeff`, etc.) | Web copy-paste / DRM | Completely stripped (prevents silent compiler / script bugs) |
| **Non-Breaking Spaces** (`\u00a0`, `\u202f`) | Web formatting | Converted to standard spaces |
| **Smart / Curly Quotes** (`“ ” ‘ ’`) | Word processors / CMS | Converted to standard ASCII `"` and `'` |
| **Rich Styling (HTML / RTF)** | Web browsers, Mail, Pages | Stripped; replaced with pure UTF-8 plain text |
| **Trailing Whitespace** | Web tables / code blocks | Trimmed per line while preserving paragraphs |

---

## 🔍 Triggering via Alfred

1. Press your Alfred hotkey (e.g. `Cmd + Space`).
2. Type **`clean`**.
3. Select:
   * 📋 **Clean Clipboard (Flush / Wipe)** ➔ Clears clipboard memory.
   * 📝 **Clean Clipboard (Plain Text)** ➔ Sanitizes copied text in-place and copies back clean plain text.

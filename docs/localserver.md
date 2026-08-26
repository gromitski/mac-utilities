# 📱 Local Wi-Fi Web Server & QR Code (`localserver`)

Instantly spin up a lightweight local web server in any directory and render a scannable QR code directly inside your terminal.

---

## 🎯 Features

* **Zero-Setup Mobile Testing:** Open your iPhone or Android camera, scan the terminal QR code, and immediately browse local HTML, images, designs, or files.
* **Guaranteed QR Rendering:** Pure-Python QR generator embedded with zero third-party dependencies.
* **Auto IP & Free Port Detection:** Detects your Mac's active Wi-Fi LAN IP (e.g. `192.168.1.x`) and automatically picks an open port if 8000 is occupied.

---

## 💻 Usage

```bash
# 1. Serve the current directory (default port 8000 or next available)
localserver

# 2. Serve a specific folder
localserver ~/Downloads
localserver ~/Projects/my-app

# 3. Serve on a custom port
localserver 3000
localserver . 5173
```

---

## 🛑 Stopping the Server

Press `Ctrl + C` in the terminal to immediately stop the server and release the port.

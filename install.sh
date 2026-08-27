#!/bin/bash
# ==============================================================================
# Mac Utilities Installer
# Sets up scripts PATH, background LaunchAgents, and Alfred workflows on any Mac.
# ==============================================================================

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$REPO_DIR/scripts"
LAUNCHD_DIR="$REPO_DIR/launchd"
USER_LAUNCHAGENTS="$HOME/Library/LaunchAgents"

echo ""
echo "🚀 Installing Mac Utilities Toolkit..."
echo "──────────────────────────────────────────────────────────────────────────"

# 1. Ensure scripts are executable
echo "📦 Making scripts executable..."
chmod +x "$SCRIPTS_DIR"/*

# 2. Add to PATH in ~/.zshrc
ZSHRC="$HOME/.zshrc"
PATH_LINE='export PATH="$HOME/utilities/scripts:$PATH"'

if [ -f "$ZSHRC" ] && grep -Fq "$PATH_LINE" "$ZSHRC"; then
    echo "✓ Scripts path already configured in ~/.zshrc"
else
    echo "✓ Adding scripts directory to PATH in ~/.zshrc..."
    echo "" >> "$ZSHRC"
    echo "# Mac Utilities Toolkit" >> "$ZSHRC"
    echo "$PATH_LINE" >> "$ZSHRC"
fi

# 3. Setup and Load LaunchAgents (Automated Nightly Housekeeping at 23:59)
echo "⏰ Configuring automated daily LaunchAgents..."
mkdir -p "$USER_LAUNCHAGENTS"
mkdir -p "$HOME/Library/Logs"

# Unload any legacy or previous instances
launchctl unload "$USER_LAUNCHAGENTS/com.gromitski.screenshot-housekeeping.plist" 2>/dev/null || true
launchctl unload "$USER_LAUNCHAGENTS/com.gromitski.downloads-housekeeping.plist" 2>/dev/null || true
launchctl unload "$USER_LAUNCHAGENTS/com.mac-utilities.screenshot-housekeeping.plist" 2>/dev/null || true
launchctl unload "$USER_LAUNCHAGENTS/com.mac-utilities.downloads-housekeeping.plist" 2>/dev/null || true
rm -f "$USER_LAUNCHAGENTS/com.gromitski.*.plist"

# Generate and install machine-specific plists from templates
sed "s|__HOME__|$HOME|g" "$LAUNCHD_DIR/com.mac-utilities.screenshot-housekeeping.plist" > "$USER_LAUNCHAGENTS/com.mac-utilities.screenshot-housekeeping.plist"
sed "s|__HOME__|$HOME|g" "$LAUNCHD_DIR/com.mac-utilities.downloads-housekeeping.plist" > "$USER_LAUNCHAGENTS/com.mac-utilities.downloads-housekeeping.plist"

# Load new LaunchAgents
launchctl load "$USER_LAUNCHAGENTS/com.mac-utilities.screenshot-housekeeping.plist"
launchctl load "$USER_LAUNCHAGENTS/com.mac-utilities.downloads-housekeeping.plist"
echo "✓ Screenshot & Downloads daily housekeeping LaunchAgents loaded."

# 4. Check for optional qrencode dependency (for localserver)
if command -v qrencode >/dev/null 2>&1; then
    echo "✓ qrencode is installed (terminal QR codes enabled)."
else
    echo "ℹ️  Tip: Install qrencode for instant terminal QR codes via: brew install qrencode"
fi

echo "──────────────────────────────────────────────────────────────────────────"
echo "✨ Installation complete!"
echo ""
echo "To start using immediately, reload your shell:"
echo "  source ~/.zshrc"
echo ""
echo "Available CLI Commands:"
echo "  • clean               (Clean screenshots & downloads on-demand)"
echo "  • clean url           (Strip tracking clutter from copied links)"
echo "  • clean deep          (Clean folders + reclaim Homebrew/pip caches)"
echo "  • git-audit           (Scan uncommitted/unpushed Git repositories)"
echo "  • localserver         (Serve local directory over Wi-Fi with QR code)"
echo "  • awake [30m|1h|off]  (Inhibit sleep and display dimming)"
echo ""
echo "Optional Alfred Workflow:"
echo "  Double-click: $REPO_DIR/alfred/Clean.alfredworkflow"
echo ""

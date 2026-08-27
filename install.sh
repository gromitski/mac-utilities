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

# 2. Add to PATH in the active shell profile (zsh, bash, or fish)
PATH_LINE='export PATH="$HOME/utilities/scripts:$PATH"'
SHELL_NAME="$(basename "$SHELL")"
PROFILE_UPDATED=""

if [ "$SHELL_NAME" = "zsh" ] || [ -f "$HOME/.zshrc" ]; then
    TARGET_RC="$HOME/.zshrc"
    if ! grep -Fq "$PATH_LINE" "$TARGET_RC" 2>/dev/null; then
        echo "" >> "$TARGET_RC"
        echo "# Mac Utilities Toolkit" >> "$TARGET_RC"
        echo "$PATH_LINE" >> "$TARGET_RC"
    fi
    PROFILE_UPDATED="~/.zshrc"
fi

if [ "$SHELL_NAME" = "bash" ] || [ -f "$HOME/.bash_profile" ] || [ -f "$HOME/.bashrc" ]; then
    TARGET_BASH="$HOME/.bash_profile"
    [ ! -f "$TARGET_BASH" ] && [ -f "$HOME/.bashrc" ] && TARGET_BASH="$HOME/.bashrc"
    if ! grep -Fq "$PATH_LINE" "$TARGET_BASH" 2>/dev/null; then
        echo "" >> "$TARGET_BASH"
        echo "# Mac Utilities Toolkit" >> "$TARGET_BASH"
        echo "$PATH_LINE" >> "$TARGET_BASH"
    fi
    PROFILE_UPDATED="${PROFILE_UPDATED:+$PROFILE_UPDATED, }$(basename "$TARGET_BASH")"
fi

if [ "$SHELL_NAME" = "fish" ]; then
    FISH_CONF_DIR="$HOME/.config/fish"
    mkdir -p "$FISH_CONF_DIR"
    FISH_LINE='set -gx PATH $HOME/utilities/scripts $PATH'
    if ! grep -Fq "$FISH_LINE" "$FISH_CONF_DIR/config.fish" 2>/dev/null; then
        echo "" >> "$FISH_CONF_DIR/config.fish"
        echo "# Mac Utilities Toolkit" >> "$FISH_CONF_DIR/config.fish"
        echo "$FISH_LINE" >> "$FISH_CONF_DIR/config.fish"
    fi
    PROFILE_UPDATED="${PROFILE_UPDATED:+$PROFILE_UPDATED, }~/.config/fish/config.fish"
fi

echo "✓ Configured PATH in: ${PROFILE_UPDATED:-~/.zshrc}"

# 3. Setup and Load LaunchAgents (Automated Nightly Housekeeping at 23:59)
echo "⏰ Configuring automated daily LaunchAgents..."
mkdir -p "$USER_LAUNCHAGENTS"
mkdir -p "$HOME/Library/Logs"

# Unload any legacy or previous instances
launchctl unload "$USER_LAUNCHAGENTS/com.mac-utilities.screenshot-housekeeping.plist" 2>/dev/null || true
launchctl unload "$USER_LAUNCHAGENTS/com.mac-utilities.downloads-housekeeping.plist" 2>/dev/null || true

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
if [ "$SHELL_NAME" = "fish" ]; then
    echo "  source ~/.config/fish/config.fish"
elif [ "$SHELL_NAME" = "bash" ]; then
    echo "  source ~/.bash_profile"
else
    echo "  source ~/.zshrc"
fi
echo ""
echo "Available CLI Commands:"
echo "  • clean               (Clean screenshots & downloads on-demand)"
echo "  • clean url           (Strip tracking clutter from copied links)"
echo "  • clean deep          (Clean folders + reclaim Homebrew/pip caches)"
echo "  • git-audit           (Scan uncommitted/unpushed Git repositories)"
echo "  • localserver         (Serve local directory over Wi-Fi with QR code)"
echo "  • awake [30m|1h|off]  (Inhibit sleep and display dimming)"
echo ""
echo "Optional Alfred Workflow (for Alfred users):"
echo "  Double-click: $REPO_DIR/alfred/Clean.alfredworkflow"
echo ""

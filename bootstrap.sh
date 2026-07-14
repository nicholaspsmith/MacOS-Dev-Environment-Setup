#!/usr/bin/env bash
# Cold-start entry point for a factory-fresh Mac.
# Installs Xcode Command Line Tools + Homebrew, then hands off to the Python
# orchestrator. All arguments pass through, e.g.:
#
#   ./bootstrap.sh --all --no-confirm     # fully unattended
#   ./bootstrap.sh                        # interactive component menu
set -euo pipefail

cd "$(dirname "$0")"

# ── Xcode Command Line Tools ────────────────────────────────────────────
if ! xcode-select -p >/dev/null 2>&1; then
    echo "==> Installing Xcode Command Line Tools (confirm the dialog)..."
    xcode-select --install 2>/dev/null || true
    until xcode-select -p >/dev/null 2>&1; do
        sleep 15
        echo "    waiting for Command Line Tools..."
    done
fi
echo "✓ Command Line Tools: $(xcode-select -p)"

# ── Homebrew ────────────────────────────────────────────────────────────
if ! command -v brew >/dev/null 2>&1; then
    echo "==> Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi
for prefix in /opt/homebrew /usr/local; do
    if [[ -x "$prefix/bin/brew" ]]; then
        eval "$("$prefix/bin/brew" shellenv)"
        break
    fi
done
echo "✓ Homebrew: $(brew --version | head -1)"

# ── Hand off to the orchestrator ────────────────────────────────────────
exec python3 setup_macos_dev.py "$@"

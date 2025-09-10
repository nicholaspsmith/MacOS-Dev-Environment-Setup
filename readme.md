# Usage

## Prerequisites
If you wan't to install the dark/light theme switcher, you'll need to have XCode installed:
[Install XCode](https://apps.apple.com/us/app/xcode/id497799835?mt=12)

## Interactive mode (default)
`python3 setup_macos_dev.py`

## Install everything automatically
`python3 setup_macos_dev.py --all --no-confirm`

## Install only specific components
`python3 setup_macos_dev.py --select 1,2,6,9`

## List available components
`python3 setup_macos_dev.py --list`


# Complete Feature List:
## ✅ Core Tools:
- Homebrew installation
- Python (via Homebrew) with alias python → python3
- Node.js installation
- ZSH shell setup (default on macOS 15+)

## ✅ iTerm2 Setup:

- Installs iTerm2 via Homebrew
- Creates custom hotkey profile with:
  - Hotkey: Ctrl+Q (^q)
  - Opacity: 10% (90% transparency)
  - Animations: Enabled for show/hide
  - System-wide hotkey window functionality

## ✅ Claude Code:
- Installs via Homebrew cask (with official installer fallback)
- Ready for terminal use

## ✅ VS Code Configuration:

- Installs VS Code via Homebrew
- Adds code command to PATH
- Uninstalls: GitHub Copilot & GitHub Copilot Chat extensions
- Installs:
  - Claude Code extension (anthropic.claude-code)
  - Python extension (ms-python.python)

## ✅ GitHub CLI:
- Installs GitHub CLI via Homebrew
- Interactive authentication setup
- Opens browser to GitHub sign-in page
- Guides user through authentication process

# Key Features:
## 🔧 Smart Setup:
- macOS 15+ compatibility check
- Automatic shell profile detection (zsh/bash)
- PATH management for current session
- Error handling with detailed logging

## 📊 Progress Tracking:
- Step-by-step progress reports
- Success/failure tracking
- Comprehensive summary at completion
- Next steps guidance

## 🛠️ User Experience:
- Interactive confirmation before starting
- Clear progress indicators
- Detailed manual configuration guide
- Troubleshooting information

After completion, you'll have a fully configured development environment ready for Python, Node.js, and AI-assisted coding with Claude!

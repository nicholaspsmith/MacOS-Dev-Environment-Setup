# Brewfile — curated from the audited machine (macOS 26.5, arm64, 2026-07-14).
# Core (uncommented) is everything the shell config, launchd agents, and
# menu-bar apps depend on, plus daily CLI tools. Heavier stacks are listed
# but commented out so `brew bundle` stays lean; uncomment what you need.
#
# Install:  brew bundle --file=Brewfile

## ── Core CLI ────────────────────────────────────────────────────────────
brew "bash"
brew "bat"
brew "btop"
brew "coreutils"
brew "direnv"            # hooked in .zshrc
brew "fastfetch"
brew "fd"
brew "fzf"               # required by .zshrc (proj picker, fzf-git.sh)
brew "gh"
brew "git-lfs"
brew "glow"              # `projects` catalog browser
brew "gnu-tar"
brew "htop"
brew "hyperfine"
brew "jq"
brew "lazygit"
brew "neovim"            # EDITOR / vim alias in .zshrc
brew "parallel"
brew "rename"
brew "ripgrep"
brew "rsync"
brew "terminal-notifier"
brew "thefuck"
brew "tmux"
brew "watch"
brew "wget"
brew "zoxide"            # hooked in .zshrc (z <name>)

## ── Watcher / agent dependencies ────────────────────────────────────────
brew "fswatch"           # code-catalog watcher
brew "ffmpeg"            # general media transcoding
brew "imagemagick"       # vpn-dns-menubar fallback PNG rebuilds

## ── Languages & version managers ────────────────────────────────────────
brew "nvm"               # lazy-loaded in .zshrc; Node LTS installed by setup script
brew "pyenv"
brew "pipx"
brew "python"
brew "yarn"

## ── Casks: terminal, editor, menu-bar ecosystem ─────────────────────────
cask "iterm2"
cask "visual-studio-code"
cask "jordanbaird-ice@beta"   # hides native Mullvad/Tailscale icons
cask "rectangle"              # window manager (until HotkeyKit-based replacement)
# Tailscale and Mullvad are deliberately NOT here — each is its own optional
# component in setup_macos_dev.py so you choose per machine.

## ── Fonts ────────────────────────────────────────────────────────────────
cask "font-caskaydia-cove-nerd-font"
cask "font-fira-code-nerd-font"
cask "font-hack-nerd-font"
cask "font-monaspace"
cask "font-sauce-code-pro-nerd-font"

## ── Optional: heavier dev stacks (installed on the audited machine) ─────
# brew "cmake"
# brew "meson"
# brew "ninja"
# brew "nasm"
# brew "deno"
# brew "dotnet"
# brew "docker"
# brew "docker-completion"
# brew "golangci-lint"
# brew "ruby"
# brew "boost"
# brew "qemu"
# brew "nmap"
# brew "pandoc"
# brew "esphome"

## ── Optional: databases ──────────────────────────────────────────────────
# tap "mongodb/brew"
# brew "mongodb/brew/mongodb-community@7.0"
# brew "mongodb-database-tools"
# brew "mongosh"
# brew "mysql"

## ── Optional: audio / media ─────────────────────────────────────────────
# brew "aubio"
# brew "jack"
# brew "taglib"
# cask "blackhole-2ch"

## ── Optional: cross-compilers & recovery tools ──────────────────────────
# brew "i686-elf-gcc"
# brew "x86_64-elf-gcc"
# brew "ddrescue"
# brew "testdisk"
# brew "smartmontools"

## ── Optional: other apps on the audited machine ─────────────────────────
# cask "emacs-app"
# cask "moonlight"
# cask "xquartz"
# cask "swiftbar"     # RETIRED — replaced by StatusItemKit Swift apps; fallback only

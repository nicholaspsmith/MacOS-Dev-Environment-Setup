# macOS Dev Environment Setup

Reproduces my full development environment on a fresh Mac (Apple Silicon,
macOS 15+, tested on macOS 26 Tahoe): Homebrew toolchain, zsh config, iTerm2,
editors, the custom StatusItemKit menu-bar app suite, and the launchd agents
that keep everything running.

## Quick start (brand-new Mac)

```sh
git clone https://github.com/nicholaspsmith/MacOS-Dev-Environment-Setup.git
cd MacOS-Dev-Environment-Setup
./bootstrap.sh --all --no-confirm
```

`bootstrap.sh` installs Xcode Command Line Tools and Homebrew, then runs the
Python orchestrator. `--all --no-confirm` is fully unattended: anything that
needs a human (GitHub login, TCC permission dialogs) is skipped and listed in
the summary as follow-up.

### Other modes

```sh
./bootstrap.sh                 # interactive checkbox menu
python3 setup_macos_dev.py --list          # list components
python3 setup_macos_dev.py --select 1,2,5  # install specific components
```

Every component is idempotent — re-running is safe.

## Components

| Component | What it does |
|---|---|
| Homebrew | installs brew itself |
| Brew Bundle | `Brewfile` — curated CLI tools (fd, ripgrep, fzf, zoxide, direnv, neovim, fswatch, nvm, …), casks (iTerm2, VS Code, Ice, Rectangle, Tailscale, Mullvad), nerd fonts. Heavier stacks (docker, DBs, qemu, audio) are in the file but commented out |
| ZSH / Oh My Zsh | ensures zsh default, installs oh-my-zsh |
| Copy .zshrc | installs `zsh/.zshrc` (backs up the old one) and clones `fzf-git.sh` |
| NVM & Node LTS | Homebrew nvm (lazy-loaded by the .zshrc) + Node LTS |
| iTerm2 Quake profile | installs `iterm_profiles/Quake.json` as a dynamic profile |
| Claude Code | native installer (`~/.local/bin/claude`), brew cask fallback |
| VS Code + extensions | installs the editor and the extension set in `vscode/extensions.txt` |
| GitHub CLI & git config | gh, git identity, git-lfs; separate interactive auth step wires `gh` as the git credential helper |
| Menu-bar app suite | clones StatusItemKit + HotkeyKit + 5 app repos side-by-side in `~/Code` (local SPM path deps), sets up the stable signing identity, builds each app, symlinks into `~/Applications` |
| VPN/DNS watcher agent | launchd agent from vpn-dns-menubar: toggles Tailscale `accept-dns` with Mullvad state |
| Code catalog | `~/Code/PROJECTS.md` watcher agent + `proj`/`list`/`projects` shell helpers |
| MOV Watcher | auto-converts `~/Downloads/*.mov` to `.mp4` (fswatch + ffmpeg) |
| Dark Mode Toggle | optional ThemeToggle menu-bar app — the only component that needs **full Xcode** ([App Store](https://apps.apple.com/us/app/xcode/id497799835?mt=12)) |
| Media Tracking Killer / Download Recycler | legacy optional background scripts |

## What can't be automated

macOS and third parties require a human for:

- **TCC permissions** — Accessibility (KeyLight), Screen Recording (MacRecorder),
  System Events (ThemeToggle): grant when each app first asks
- **Logins** — `gh auth login`, Tailscale, Mullvad, App Store
- **Ice menu-bar layout** — hide the native Mullvad/Tailscale icons by hand
- **SSH keys / `~/.ssh/config`** — restore from backup (e.g. the `dino` host)
- **Start at Login** for the menu-bar apps — toggle inside each app's menu (SMAppService)

See `docs/system-inventory.md` for the full audit of the reference machine,
including what was deliberately left out and why.

## Repo layout

```
bootstrap.sh            cold-start entry point (CLT + Homebrew + orchestrator)
setup_macos_dev.py      component-based orchestrator
Brewfile                curated package manifest
zsh/.zshrc              shell config (genericized from the live machine)
iterm_profiles/         iTerm2 dynamic profile(s)
vscode/extensions.txt   VS Code extension set
local_bin/              code-catalog scripts installed to ~/.local/bin
background_scripts/     mov_watcher, media-tracking killer, download recycler
mac_light_dark_toggle/  ThemeToggle Xcode project
docs/                   system inventory + design specs
```

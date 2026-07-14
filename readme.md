# macOS Dev Environment Setup

Reproduces my full development environment on a fresh Mac (Apple Silicon,
macOS 15+, tested on macOS 26 Tahoe): Homebrew toolchain, zsh config, iTerm2,
editors, the custom StatusItemKit menu-bar app suite, and the launchd agents
that keep everything running.

## Quick start — brand-new Mac

Paste this into Terminal.app:

```sh
git clone https://github.com/nicholaspsmith/MacOS-Dev-Environment-Setup.git
cd MacOS-Dev-Environment-Setup
./bootstrap.sh --all --no-confirm
```

That's the whole install. `bootstrap.sh` installs Xcode Command Line Tools and
Homebrew first, then runs every component below. `--all --no-confirm` is fully
unattended — anything that needs a human (GitHub login, keychain password, TCC
permission dialogs) is skipped and listed at the end as follow-up. Then run
the [after-install commands](#after-install-run-these).

Every component is idempotent — re-running is always safe.

## Usage modes

```sh
./bootstrap.sh                              # interactive checkbox menu (pick components)
./bootstrap.sh --all                        # everything, but pause for prompts
./bootstrap.sh --all --no-confirm           # everything, fully unattended
python3 setup_macos_dev.py --list           # list all components with numbers
python3 setup_macos_dev.py --select 2,5,13  # install only components 2, 5, and 13
```

(`bootstrap.sh` and `setup_macos_dev.py` take the same flags; use `bootstrap.sh`
on a machine that might not have Homebrew yet.)

## Components (numbers work with `--select`)

| # | Component | What it does |
|---|---|---|
| 1 | Homebrew | installs brew itself |
| 2 | Brew Bundle | installs the `Brewfile`: CLI tools (fd, ripgrep, fzf, zoxide, direnv, neovim, fswatch, nvm, …), casks (iTerm2, VS Code, Ice, Rectangle, Tailscale, Mullvad), nerd fonts |
| 3 | ZSH Shell | ensures zsh is the default shell |
| 4 | Oh My Zsh | installs oh-my-zsh |
| 5 | Copy .zshrc | installs `zsh/.zshrc` (backs up your old one to `~/.zshrc.backup`) and clones `fzf-git.sh` |
| 6 | NVM & Node LTS | Homebrew nvm + Node LTS (`nvm alias default lts/*`) |
| 7 | iTerm2 Quake profile | installs the dropdown profile via DynamicProfiles |
| 8 | Claude Code | native installer → `~/.local/bin/claude` (brew cask fallback) |
| 9 | VS Code | installs the editor + `code` CLI |
| 10 | VS Code Extensions | installs everything in `vscode/extensions.txt` |
| 11 | GitHub CLI & git config | gh, git identity, git-lfs |
| 12 | GitHub Authentication | interactive `gh auth login` (skipped under `--no-confirm`) |
| 13 | Menu-bar app suite | clones + builds ProcessMonitor, VPN & DNS, Battery Time, KeyLight, MacRecorder into `~/Applications`; retires the legacy battery-time power-watch agent |
| 14 | VPN/DNS watcher agent | launchd agent: Tailscale `accept-dns` follows Mullvad state |
| 15 | Code catalog | `~/Code/PROJECTS.md` watcher + `proj`/`list`/`projects` shell helpers |
| 16 | MOV Watcher | auto-converts `~/Downloads/*.mov` → `.mp4` |
| 17 | Dark Mode Toggle | optional ThemeToggle app — the only component needing **full Xcode** |
| 18 | Media Tracking Killer | legacy optional background script |
| 19 | Download Recycler | legacy optional: trash old Downloads after N days |

Examples:

```sh
python3 setup_macos_dev.py --select 13             # just (re)build the menu-bar apps
python3 setup_macos_dev.py --select 2 --no-confirm # just (re)run the Brewfile
python3 setup_macos_dev.py --select 5,6            # shell config + node
```

## After install — run these

An unattended run skips everything that needs you. Finish with:

```sh
# 1. New shell so PATH/.zshrc take effect
exec zsh

# 2. Sign into GitHub and wire gh as git's credential helper
gh auth login && gh auth setup-git

# 3. Stable code-signing identity (asks for your macOS login password),
#    then rebuild the menu-bar apps so TCC grants survive future rebuilds
~/Code/StatusItemKit/scripts/setup-signing.sh
cd ~/MacOS-Dev-Environment-Setup   # or wherever you cloned this repo
python3 setup_macos_dev.py --select 13 --no-confirm
```

Then do the things macOS won't let a script do:

- Launch each menu-bar app once (`open ~/Applications`) and grant its
  permission when asked: **Accessibility** for KeyLight, **Screen Recording**
  for MacRecorder. Enable **Start at Login** from each app's own menu.
- Sign into **Tailscale** and **Mullvad VPN**, then open **Ice** and hide
  their native menu-bar icons (VPN & DNS.app is the one dot you keep).
- iTerm2: the Quake profile is installed; assign its hotkey under
  **Settings ▸ Profiles ▸ Quake ▸ Keys** if it isn't active.
- Restore SSH keys + `~/.ssh/config` from backup (e.g. the `dino` host).
- App Store: install full Xcode only if you want component 17 (ThemeToggle).

## Health checks

```sh
launchctl list | grep nicholassmith        # custom agents loaded?
brew bundle check --file=Brewfile          # Brewfile satisfied?
gh auth status                             # GitHub wired?
claude --version                           # Claude Code installed?
tail -5 ~/Library/Logs/code-catalog.log    # catalog watcher alive?
tail -5 ~/Library/Logs/mov-converter.log   # MOV watcher alive?
```

Repair anything by re-running its component (`--select N`), or re-run the
whole thing — everything is idempotent.

## Repo layout

```
bootstrap.sh            cold-start entry point (CLT + Homebrew + orchestrator)
setup_macos_dev.py      component-based orchestrator
Brewfile                curated package manifest (heavy stacks commented out)
zsh/.zshrc              shell config (genericized from the live machine)
iterm_profiles/         iTerm2 dynamic profile(s)
vscode/extensions.txt   VS Code extension set
local_bin/              code-catalog scripts installed to ~/.local/bin
background_scripts/     mov_watcher, media-tracking killer, download recycler
mac_light_dark_toggle/  ThemeToggle Xcode project
docs/                   system inventory + design specs
```

`docs/system-inventory.md` records the full audit of the reference machine —
what's automated, what's deliberately manual, and why.

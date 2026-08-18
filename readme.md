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
python3 setup_macos_dev.py --select 2,6,14  # install only components 2, 6, and 14
```

(`bootstrap.sh` and `setup_macos_dev.py` take the same flags; use `bootstrap.sh`
on a machine that might not have Homebrew yet.)

## Components (numbers work with `--select`)

| # | Component | What it does |
|---|---|---|
| 1 | Homebrew | installs brew itself |
| 2 | Brew Bundle | installs the `Brewfile`: CLI tools (fd, ripgrep, fzf, zoxide, atuin, direnv, neovim, mosh, nvm, …), casks (iTerm2, VS Code, Ice, Rectangle, Tailscale, Mullvad), nerd fonts |
| 3 | ZSH Shell | ensures zsh is the default shell |
| 4 | Oh My Zsh | installs oh-my-zsh |
| 5 | Zsh plugins | clones `zsh-autosuggestions` + `fast-syntax-highlighting` into `$ZSH_CUSTOM/plugins` (see [Inline autosuggestions](#inline-autosuggestions)) |
| 6 | Copy .zshrc | installs `zsh/.zshrc` (backs up your old one to `~/.zshrc.backup`) and clones `fzf-git.sh` |
| 7 | NVM & Node LTS | Homebrew nvm + Node LTS (`nvm alias default lts/*`) |
| 8 | iTerm2 Quake profile | installs the dropdown profile via DynamicProfiles |
| 9 | Claude Code | native installer → `~/.local/bin/claude` (brew cask fallback) |
| 10 | VS Code | installs the latest VS Code + puts the `code` command on PATH (brew-bin symlink and `~/.zshrc`) |
| 11 | VS Code Extensions | installs everything in `vscode/extensions.txt` |
| 12 | GitHub CLI & git config | gh, git identity, git-lfs |
| 13 | GitHub Authentication | interactive `gh auth login` (skipped under `--no-confirm`) |
| 14 | Menu-bar app suite | clones + builds **7 apps** into `~/Applications`: ProcessMonitor, VPN & DNS, Battery Time, KeyLight, MacRecorder, [Media Tracking Killer](https://github.com/nicholaspsmith/media-tracking-killer-menubar), [Download Recycler](https://github.com/nicholaspsmith/download-recycler-menubar); retires the launchd agents the apps replaced |
| 15 | Tailscale | Tailscale Mac app — its own checkbox so you choose per machine |
| 16 | Mullvad VPN | Mullvad VPN app — its own checkbox so you choose per machine |
| 17 | VPN/DNS watcher agent | launchd agent: Tailscale `accept-dns` follows Mullvad state (needs 15 + 16) |
| 18 | code-sync (projects) | creates `~/Code` if missing; clones [code-sync](https://github.com/nicholaspsmith/code-sync) and runs its `install.sh` (`projects`/`proj`/`list`, hourly sync agent); retires the old catalog watcher and installs the `newtools` cheat sheet |

The old media-tracking-killer and download-recycler background scripts are now
full menu-bar apps inside component 14 — each with an on/off toggle, its own
settings (kill interval / retention days), and Start at Login. The Dark Mode
Toggle (macOS has this built into Control Center now) and MOV watcher
components were removed.

Examples:

```sh
python3 setup_macos_dev.py --select 14             # just (re)build the menu-bar apps
python3 setup_macos_dev.py --select 2 --no-confirm # just (re)run the Brewfile
python3 setup_macos_dev.py --select 5,6,7          # zsh plugins + shell config + node
```

## Inline autosuggestions

Components 5 + 6 give the shell the grey ghost-text completion you see in fish
and Warp, without leaving zsh:

- **`zsh-autosuggestions`** — suggests as you type from your shell history.
- **`fast-syntax-highlighting`** — colors commands live, so a typo shows up red
  before you press Enter.

Keys, once installed:

| Key | Effect |
|---|---|
| `Tab` | accept the whole suggestion — falls through to normal completion when no suggestion is showing |
| `→` / `End` / `^E` | accept the whole suggestion |
| `⌥F` | accept **one word** of it |
| `↓` / `↑` | walk forward / back through the other matches (below) |

Acceptance only fires with the cursor at end of line; mid-line, `→` just moves
the cursor as usual.

### Cycling to the other matches

The suggestion is a single guess. `↑`/`↓` walk in place through the other
history entries that start with what you've typed:

The grey ghost text is **candidate 1**. From there:

- `↓` reveals candidate 2, then 3, then 4 — one per press, digging deeper.
- `↑` walks back up toward candidate 1.
- `↑` **at candidate 1** — or before you've started cycling at all — opens
  **atuin's full-screen search**, seeded with the text you typed rather than
  whichever candidate happens to be on screen. `Esc` out of atuin and you're
  back to your typed line.
- `↓` at the deepest candidate stays put. Depth is `_hcyc_limit` (default 50).
- If no ghost is showing (nothing matched), the first `↓` starts at candidate 1
  instead of 2, so no option is skipped.
- In a multi-line buffer, both arrows keep their normal line-movement behavior.

Candidates come from **atuin**, not zsh's own history, so the cycle agrees with
the grey ghost text instead of drawing on a second unsynced source. It falls
back to `fc` when atuin isn't installed.

This is hand-rolled rather than `zsh-history-substring-search`, which has no
concept of "out of matches" — and that boundary is the whole point of the
hand-off. The widget is defined after both plugins bind theirs, so it clears
`POSTDISPLAY` and calls `_zsh_highlight` itself; without those two lines the
ghost text and the syntax colors go stale as you cycle.

Two ordering rules are load-bearing, both commented in `zsh/.zshrc`:

1. `fast-syntax-highlighting` must be the **last** entry in `plugins=(…)` — it
   wraps every ZLE widget defined before it.
2. The Tab block must be the **last thing in the file**. It captures whichever
   widget currently owns `^I` instead of hardcoding one, because `fzf --zsh`
   rebinds Tab to `fzf-completion` earlier in the file; hardcoding
   `expand-or-complete` there would silently break fzf's `**<TAB>` trigger. Any
   new Tab-binding tool has to be added *above* that block.

`.zshrc` appends the two plugins only if their directories exist, so a machine
that skipped component 5 still starts a clean shell — just without ghost text.
Suggestions come from shell history, falling back to completions. (This repo
does not install `atuin`, but if you add it yourself it prepends its own
strategy to `ZSH_AUTOSUGGEST_STRATEGY` and its synced DB becomes the first
source.) Cost is roughly +15 ms on shell startup, measured on the reference
machine.

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
python3 setup_macos_dev.py --select 14 --no-confirm
```

Then do the things macOS won't let a script do:

- Launch each menu-bar app once (`open ~/Applications`) and grant its
  permission when asked: **Accessibility** for KeyLight, **Screen Recording**
  for MacRecorder, **Downloads folder** for Download Recycler. Enable
  **Start at Login** from each app's own menu.
- If you installed them: sign into **Tailscale** and **Mullvad VPN**, then
  open **Ice** and hide their native menu-bar icons (VPN & DNS.app is the one
  dot you keep).
- iTerm2: the Quake profile is installed; assign its hotkey under
  **Settings ▸ Profiles ▸ Quake ▸ Keys** if it isn't active.
- Restore SSH keys + `~/.ssh/config` from backup (e.g. the `dino` host).

## Health checks

```sh
launchctl list | grep nicholassmith        # custom agents loaded?
brew bundle check --file=Brewfile          # Brewfile satisfied?
gh auth status                             # GitHub wired?
claude --version                           # Claude Code installed?
bindkey '^I'                               # Tab -> _tab_accept_or_complete?
projects                                   # ~/Code sync status block
tail -5 ~/Library/Logs/code-sync.launchd.log     # sync agent healthy?
tail -5 ~/Library/Logs/download-recycler.log    # recycler audit trail
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
local_bin/              scripts installed to ~/.local/bin (newtools cheat sheet)
docs/                   system inventory + design specs
```

`docs/system-inventory.md` records the full audit of the reference machine —
what's automated, what's deliberately manual, and why.

### About `zsh/.zshrc`

It is a **genericized** copy of the live file, not a verbatim one, and the
differences are deliberate:

- Absolute `/Users/<name>/…` paths become `$HOME`, and every optional tool is
  guarded (`command -v fzf`, `[[ -f … ]]`) so the file starts cleanly on a
  machine that has none of them.
- Machine-local bits are **omitted**: private-app launchers, LAN IPs, and
  Tailscale MagicDNS names have no business in a public repo. The `dino` alias
  survives because it's just an ssh host name you supply yourself in
  `~/.ssh/config`.
- The retired fswatch catalog helpers are gone; `proj`/`list`/`projects` now
  come from code-sync (component 18).

Two ordering constraints matter when re-running components:

1. **Component 18 must run after component 6.** code-sync's `install.sh` edits
   `~/.zshrc` in place; copying the repo's `.zshrc` over it afterwards would
   discard that edit. The default order already does this.
2. `install.sh` **appends** its `projects` block to the end of `~/.zshrc`, so it
   always ends up below the Tab block. `zsh/.zshrc` ships in that same order, so
   component 18 is a no-op on layout rather than a reshuffle. That block binds
   Esc-s, never `^I`, so Tab is unaffected — but nothing that rebinds Tab may go
   below it.

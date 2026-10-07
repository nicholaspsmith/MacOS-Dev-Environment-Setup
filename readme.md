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
| 2 | Brew Bundle | installs the `Brewfile`: CLI tools (fd, ripgrep, fzf, zoxide, atuin, direnv, neovim, mosh, nvm, beads, …), casks (iTerm2, VS Code, Rectangle), nerd fonts. Tailscale and Mullvad are deliberately not in it — see 15 + 16 |
| 3 | ZSH Shell | ensures zsh is the default shell |
| 4 | Oh My Zsh | installs oh-my-zsh |
| 5 | Zsh plugins | clones `fzf-tab`, `zsh-autosuggestions` + `fast-syntax-highlighting` into `$ZSH_CUSTOM/plugins` (see [Inline autosuggestions](#inline-autosuggestions)) |
| 6 | Shared .zshrc config | links `~/.config/zsh/shared.zsh` → this repo's `zsh/shared.zsh` and adds one block to `~/.zshrc` that sources it; never overwrites your `~/.zshrc` (see [Shell config](#shell-config-zshsharedzsh)); clones `fzf-git.sh` |
| 7 | NVM & Node LTS | Homebrew nvm + Node LTS (`nvm alias default lts/*`) |
| 8 | iTerm2 Quake profile | installs the dropdown profile via DynamicProfiles |
| 9 | Claude Code | native installer → `~/.local/bin/claude` (brew cask fallback) |
| 10 | VS Code | installs the latest VS Code + puts the `code` command on PATH (brew-bin symlink and `~/.zshrc`) |
| 11 | VS Code Extensions | installs everything in `vscode/extensions.txt` |
| 12 | GitHub CLI & git config | gh, git identity, git-lfs |
| 13 | GitHub Authentication | interactive `gh auth login` (skipped under `--no-confirm`) |
| 14 | Menu-bar app suite | clones StatusItemKit + HotkeyKit, sets up the stable signing identity (skipped under `--no-confirm`), then clones + builds **12 apps** and symlinks them into `~/Applications`: [Mac Daddy](https://github.com/nicholaspsmith/mac-daddy-menubar), VPN & DNS, Battery Time, KeyLight, MacRecorder, Claude Usage, Apollo Monitor, Monitor Lizard, Homestead, [SoundChain](https://github.com/nicholaspsmith/soundchain-menubar), [Menu Crane](https://github.com/nicholaspsmith/menu-crane), [Panes](https://github.com/nicholaspsmith/panes-menubar); never sunset apps (Barn and the ones Mac Daddy absorbed); skips the rebuild when a repo is unchanged and already built; retires the launchd agents the apps replaced; re-arms each app's release pre-push hook |
| 15 | Tailscale | Tailscale Mac app — its own checkbox so you choose per machine |
| 16 | Mullvad VPN | Mullvad VPN app — its own checkbox so you choose per machine |
| 17 | VPN/DNS watcher agent | launchd agent: Tailscale `accept-dns` follows Mullvad state (needs 15 + 16) |
| 18 | code-sync (projects) | creates `~/Code` if missing; clones [code-sync](https://github.com/nicholaspsmith/code-sync) and runs its `install.sh` (`projects`/`proj`/`list`, hourly sync agent); retires the old catalog watcher and installs the `newtools` cheat sheet |

The old media-tracking-killer, download-recycler and process-monitor apps (and
the godot-headless-reaper agent) are now one menu-bar app, Mac Daddy, inside
component 14 — with an on/off toggle per duty, its own settings, and Start at
Login. The Dark Mode
Toggle (macOS has this built into Control Center now) and MOV watcher
components were removed.

Together the apps are **Menumon** (https://menumon.nicksmith.software). Every
push to a Menumon app is a release; the pre-push hook that enforces it lives
in each repo's local git config, so fresh clones have none until component 14
runs `StatusItemKit/scripts/release/adopt.sh --hooks-only` to re-arm it.

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
- **`fzf-tab`** — Tab completion as an fzf picker: every candidate the
  completion system knows, with descriptions, fuzzy-searchable.

Keys, once installed:

| Key | Effect |
|---|---|
| `Tab` | accept the ghost text when one is showing; otherwise open the fzf-tab completion menu (a single match is inserted directly) |
| `→` / `End` / `^E` | accept the whole suggestion |
| `⌥F` | accept **one word** of it |
| `↓` / `↑` | walk forward / back through the other matches (below) |

Acceptance only fires with the cursor at end of line; mid-line, `→` just moves
the cursor as usual and `Tab` completes.

### Suggestions that can't work are skipped

History doesn't record where a command ran, so `cd foo` typed inside `~/Code`
would otherwise be suggested again in `~`, where `foo` doesn't exist. `_hv_ok`
rejects any `cd`/`pushd` whose target doesn't resolve from `$PWD` (or via
`cdpath`) and the next-newest match is suggested instead; every other command
passes untouched. The ghost-text strategy (`history_valid`) and the arrow-key
cycling both use it, so they stay in step.

`cdpath=(~/Code)` (set when `~/Code` exists) makes `cd <project>` work from any
directory: a name that isn't under `$PWD` is looked up in `~/Code` next, and zsh
prints where it landed.

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

### History vs. completions

Two different questions, deliberately on two different keys:

- **Arrows = history.** "What did I run before?" atuin plus zsh's `HISTFILE`.
  Neither knows what flags a command accepts — atuin is a history database.
- **Tab = completions** (once no ghost text is showing). "What can this
  command do?" fzf-tab renders the completion system's candidates, so
  `brew <TAB>` offers all 194 subcommands with their descriptions,
  fuzzy-searchable; `git checkout <TAB>` picks a branch, `kill <TAB>` a PID.

The Tab chain resolves itself and is worth not disturbing. fzf-tab binds `^I`
when it loads; `fzf --zsh` then rebinds `^I` to `fzf-completion` but first
records the previous owner in `$fzf_default_completion`, so it delegates back
to fzf-tab whenever the line has no `**` trigger. Last, `_tab_accept_or_complete`
takes `^I` itself: it accepts the ghost text if one is showing and otherwise
calls `fzf-completion`. All three coexist:

| You type | You get |
|---|---|
| `brew <TAB>` | fzf-tab menu of brew's subcommands |
| `vim **<TAB>` | fzf's fuzzy path search |
| `git chec<TAB>` (ghost showing) | the suggestion accepted |

Note that completion candidates come in the completion function's order, not by
how often *you* use them — nothing off the shelf ranks by personal frequency.
Type a few characters in the fzf picker instead of hunting alphabetically.

Candidates come from **atuin first** (recent, synced across machines), then
zsh's own `HISTFILE` appended after them, deduped. Both are needed: atuin's DB
only goes back to when atuin was installed, while `HISTFILE` goes back years.
Without atuin installed, the cycle is just `HISTFILE`.

This is hand-rolled rather than `zsh-history-substring-search`, which has no
concept of "out of matches" — and that boundary is the whole point of the
hand-off. The widget is defined after both plugins bind theirs, so it clears
`POSTDISPLAY` and calls `_zsh_highlight` itself; without those two lines the
ghost text and the syntax colors go stale as you cycle.

Two ordering rules are load-bearing, both commented in `zsh/shared.zsh`:

1. `fast-syntax-highlighting` must be the **last** entry in `plugins=(…)` — it
   wraps every ZLE widget defined before it.
2. `fzf --zsh` must load **after** fzf-tab (it does: fzf-tab comes from
   `plugins=(…)`, fzf's keybindings are sourced later). It records the previous
   `^I` owner in `$fzf_default_completion` and delegates to it, so the order is
   what keeps `**<TAB>` and the fzf-tab menu both working. The only other `^I`
   binding is `_tab_accept_or_complete`, which must come after both. (Tab-accept
   was removed on 2026-09-15 because unvalidated history offered `cd` targets
   that no longer existed, and restored on 2026-09-26 once `_hv_ok` filtered
   those out.)

`shared.zsh` appends the three plugins only if their directories exist, so a machine
that skipped component 5 still starts a clean shell — just without ghost text.
Suggestions come from shell history, falling back to completions. (`atuin`
comes from the Brewfile, component 2; when present it prepends its own
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
#    then rebuild the menu-bar apps with it so TCC grants survive future rebuilds.
#    Component 14 skips repos that are unchanged and already built, so call
#    each app's build script directly rather than re-running --select 14:
~/Code/StatusItemKit/scripts/setup-signing.sh
for r in mac-daddy-menubar vpn-dns-menubar battery-time-menubar keylight-menubar \
         MacRecorder claude-usage-menubar apollo-monitor-menubar \
         monitor-lizard-menubar home-assistant-menubar soundchain-menubar; do
  bash ~/Code/$r/scripts/build-app.sh
done
```

Then do the things macOS won't let a script do:

- Launch each menu-bar app once (`open ~/Applications`) and grant its
  permission when asked: **Accessibility** for KeyLight, Monitor
  Lizard, Panes and Menu Crane (for ⌘↩), **Screen Recording** for MacRecorder, **Downloads folder** for
  Mac Daddy; Homestead asks for a Home Assistant token; SoundChain
  asks for **System Audio Recording**. Enable
  **Start at Login** from each app's own menu (SMAppService — no
  LaunchAgents).
- If you installed them: sign into **Tailscale** and **Mullvad VPN**, then
  hide their native menu-bar icons in **System Settings ▸ Menu Bar** (VPN &
  DNS.app is the one icon you keep). Barn, the old menu-bar manager, is sunset
  and no longer installed. Ice is retired and no longer in the Brewfile.
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
```

Repair anything by re-running its component (`--select N`), or re-run the
whole thing — everything is idempotent.

## Repo layout

```
bootstrap.sh            cold-start entry point (CLT + Homebrew + orchestrator)
setup_macos_dev.py      component-based orchestrator
Brewfile                curated package manifest (heavy stacks commented out)
zsh/shared.zsh          shared shell config, sourced from every Mac's ~/.zshrc
iterm_profiles/         iTerm2 dynamic profile(s)
vscode/extensions.txt   VS Code extension set
local_bin/              scripts installed to ~/.local/bin (newtools cheat sheet)
docs/                   system inventory + design specs
```

`docs/system-inventory.md` records the full audit of the reference machine —
what's automated, what's deliberately manual, and why.

### Shell config: `zsh/shared.zsh`

Every Mac's `~/.zshrc` starts with this block, which component 6 adds:

```zsh
# --- MacOS-Dev-Environment-Setup: shared shell config ---
# Lines below this block are this machine's own and override it.
[[ -r ~/.config/zsh/shared.zsh ]] && source ~/.config/zsh/shared.zsh
# --- end MacOS-Dev-Environment-Setup ---
```

`~/.config/zsh/shared.zsh` is a symlink to `zsh/shared.zsh` in this checkout,
so a `git pull` (code-sync does one hourly) updates the shell on every Mac. No
need to re-run setup. `~/.zshrc` stays each machine's own file: its extra
PATH entries, private-app launchers, LAN IPs and a LAN-aware `dino()` go below
the block, and installers (bun, pnpm, code-sync) keep appending to it as
usual. Don't bind `^I` or re-run `fzf --zsh` below the block, because that
would undo the Tab widget. A function with the same name as a shared alias
needs `unalias <name> 2>/dev/null` before it.

What component 6 does, based on what `~/.zshrc` holds:

| Found | Result |
|---|---|
| the block already | only the symlink is refreshed |
| nothing / a few lines | block prepended, the rest kept |
| a file that loads oh-my-zsh itself | backed up to `~/.zshrc.backup-<timestamp>` and replaced by the block (oh-my-zsh would otherwise load twice); reported in the summary so you move that machine's own lines back |
| a copy from the old copy-the-whole-file scheme | rebuilt as block + the former `~/.zshrc.local` + code-sync's block (backup kept, `.zshrc.local` renamed `.migrated`) |

`shared.zsh` is written to be generic. Paths use `$HOME` and every optional
tool is guarded (`command -v fzf`, `[[ -f … ]]`), so it starts cleanly on a
machine that has none of them. `proj`/`list`/`projects` come from code-sync
(component 18), whose `install.sh` appends its own marker block to
`~/.zshrc`, below this one.

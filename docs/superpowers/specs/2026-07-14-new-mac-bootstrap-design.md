# New-Mac Bootstrap — Design

Date: 2026-07-14
Status: Approved (session ran autonomously; scope decisions documented below)

## Goal

Run one command on a brand-new Mac (Apple Silicon, macOS 15+, tested on macOS 26.x)
and get this machine's development environment reproduced as far as automation
allows: CLI toolchain, shell config, terminal, editors, the custom menu-bar app
suite, and the launchd agents that keep the environment running.

## Audit findings (2026-07-14, macOS 26.5.2, arm64)

What the repo covered vs. what the machine actually runs:

| Area | Repo (before) | Machine (actual) |
|---|---|---|
| macOS | "15+" check, written pre-Tahoe | macOS 26.5.2 — check passes, README stale |
| Shell | 92-line `.zshrc` (2025 era) | 264-line `.zshrc`: brew-nvm lazy-load, fzf cache, direnv, zoxide, fzf-git.sh, code-catalog functions |
| Node | nvm via curl v0.39.7 → `~/.nvm` | nvm via **Homebrew**, lazy-loaded |
| Claude Code | brew cask first | **native installer** (`~/.local/bin/claude`) |
| CLI tools | python, node only | ~70 curated brew leaves (fd, ripgrep, fzf, zoxide, direnv, neovim, fswatch, …) |
| Casks | iterm2, vscode, claude-code | + jordanbaird-ice@beta, tailscale-app, rectangle, nerd fonts, blackhole-2ch (Mullvad & iTerm installed outside brew) |
| Menu-bar apps | ThemeToggle only (not even installed anymore) | ProcessMonitor, VPN & DNS, Battery Time, KeyLight, MacRecorder — built from `~/Code` repos on StatusItemKit/HotkeyKit (**local `../` SPM path deps**), symlinked into `~/Applications` |
| launchd agents | killapplemediatracking, downloadrecycler (**neither installed on machine**) | mullvad-tailscale-dns, code-catalog, battery-time-power-watch, godot-headless-reaper, networkscan(+server) |
| iTerm profile | Quake.json shipped but never installed | Not wired via DynamicProfiles either — manual |
| VS Code | installed copilot-removal + 2 extensions | 44 extensions, no anthropic.claude-code extension |
| `~/.local/bin` | not covered | code-catalog-{refresh,watch} live **only** there (unrecoverable on a new Mac) |

Notable inconsistencies observed (reported, machine state not changed):

- `com.nicholassmith.battery-time-power-watch` is still loaded and pointing at
  `power-watch.sh`, although the Battery Time Swift app supposedly replaced it
  with in-process IOKit notifications.
- SwiftBar cask is installed but retired (plugin symlinks removed).
- `background_scripts/mov_watcher.sh` existed untracked in the repo and is not
  installed as an agent on the machine.

## Approaches considered

1. **Extend the existing Python orchestrator + add a Brewfile and `bootstrap.sh`**
   (chosen). Keeps the component-selection UX (`--all`, `--select`, `--list`,
   curses menu) the repo already has; smallest diff; Python 3 is available as
   soon as Xcode CLT is installed.
2. Full bash rewrite — no benefit over (1); loses the menu UX.
3. Adopt chezmoi/nix-darwin — most reproducible but a paradigm shift and a new
   dependency; the environment is already organized around per-repo installers.

## Design

### Entry point

`bootstrap.sh` (new): the only thing run on a factory-fresh Mac.

1. Installs Xcode Command Line Tools if missing (`xcode-select --install`,
   wait-loop until done).
2. Installs Homebrew if missing; puts it on PATH for the session (arm64 and
   Intel prefixes).
3. `exec`s `python3 setup_macos_dev.py "$@"` — flags pass straight through.

Full Xcode (App Store) is only needed for the optional ThemeToggle component;
everything else builds with CLT (`swift build`).

### Package management

`Brewfile` (new): single curated manifest, installed by a new "Brew Bundle"
component via `brew bundle --file`. Core = everything the shell config and
agents depend on plus daily CLI tools. Heavier stacks (docker, databases,
qemu, cross-compilers, media apps) are present but commented out, so
`brew bundle` stays lean and the file still documents the full machine.
SwiftBar is deliberately excluded (retired). Mullvad + Tailscale + Ice are
core casks because the VPN/DNS menu-bar stack requires them.

### Components (setup_macos_dev.py)

Updated list; every component stays individually selectable and idempotent.

| # | Component | Change |
|---|---|---|
| 1 | Homebrew | kept |
| 2 | Brew Bundle (Brewfile) | **new** — replaces the individual python/node/iterm2/gh install steps |
| 3 | Oh My Zsh | kept |
| 4 | `.zshrc` + fzf-git.sh | **updated** — repo `.zshrc` refreshed from the live one, genericized (`$HOME`, guards around optional paths); clones `fzf-git.sh` into `~/Code` |
| 5 | NVM + Node LTS | **updated** — brew nvm (matches live config) instead of curl installer |
| 6 | iTerm2 Quake profile | **new** — wraps `Quake.json` into `{"Profiles":[…]}` and drops it in `~/Library/Application Support/iTerm2/DynamicProfiles/` |
| 7 | Claude Code | **updated** — native installer first, brew cask fallback |
| 8 | VS Code + extensions | **updated** — installs from `vscode/extensions.txt` (captured from this machine); copilot-uninstall step dropped |
| 9 | Git config + GitHub CLI auth | **updated** — sets user.name/email, `gh auth login`, `gh auth setup-git`, `git lfs install` |
| 10 | Menu-bar app suite | **new** — clones StatusItemKit, HotkeyKit, then the 5 app repos side-by-side in `~/Code` (required: local `../` SPM deps); runs StatusItemKit `setup-signing.sh` once (stable self-signed identity so TCC grants survive rebuilds); runs each repo's `scripts/build-app.sh`; symlinks apps into `~/Applications` |
| 11 | VPN/DNS watcher agent | **new** — from the cloned vpn-dns-menubar repo: templates + bootstraps `com.nicholassmith.mullvad-tailscale-dns` (Swift app is primary UI; the repo's own `install.sh` is SwiftBar-era and is not used) |
| 12 | Code catalog | **new** — installs vendored `local_bin/code-catalog-{refresh,watch}` into `~/.local/bin`, bootstraps `com.nicholassmith.code-catalog` |
| 13 | MOV → MP4 watcher | **new** — installs `background_scripts/mov_watcher.sh` (now tracked) + launchd agent (deps: fswatch, ffmpeg) |
| 14 | ThemeToggle | kept, optional; prompts gated behind `--no-confirm` |
| 15 | Apple media tracking killer | kept, optional (not installed on the audited machine — marked legacy) |
| 16 | Download recycler | kept, optional/legacy; retention prompt defaults to 30 days under `--no-confirm` |

launchd management moves from `launchctl load` to
`launchctl bootstrap gui/$UID` with `load -w` fallback (same pattern as the
per-repo installers).

### Unattended mode

`--all --no-confirm` must run without touching stdin. Every `input()` is gated:
interactive extras (launch app now?, login item?, GitHub auth browser flow)
are skipped or defaulted. GitHub auth stays a separate component so it can be
run later interactively.

### Explicitly out of scope (documented in docs/system-inventory.md, not automated)

- Machine-specific agents/scripts: godot-headless-reaper, networkscan(+server),
  dell-display-fix, discord_webhook — tied to hardware or unrelated projects.
- Secrets and auth: SSH keys/config (`ssh dino`), gh/Tailscale/Mullvad logins,
  TCC permission grants (Accessibility etc. — macOS requires clicking through).
- App Store installs (Xcode, Logic, etc.) and personal media/audio software.
- Ice menu-bar layout, System Settings preferences.

### Repo layout after this change

```
bootstrap.sh                 # new cold-start entry point
setup_macos_dev.py           # updated orchestrator
Brewfile                     # new
zsh/.zshrc                   # refreshed + genericized
iterm_profiles/Quake.json    # unchanged (now actually installed)
vscode/extensions.txt        # new, captured from this machine
local_bin/                   # new: code-catalog-refresh, code-catalog-watch
background_scripts/          # mov_watcher.sh now tracked
mac_light_dark_toggle/       # unchanged
docs/system-inventory.md     # new: audit snapshot of this machine
docs/superpowers/specs/      # this document
readme.md                    # rewritten
```

### Error handling & testing

- Every component reports success/failure into the existing summary; a failed
  component never aborts the run.
- Network clones use HTTPS URLs (new machine has no SSH keys yet).
- Verification on this machine: `--list` renders all components,
  `python3 -m py_compile`, `bash -n bootstrap.sh` + shellcheck,
  `brew bundle list --file=Brewfile` parses, and idempotent components
  (zshrc copy is destructive-with-backup, so verified by inspection only).

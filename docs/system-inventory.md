# System Inventory — audited 2026-07-14

Snapshot of the reference machine (MacBook, Apple Silicon, macOS 26.5.2) that
this repo reproduces. Items marked **automated** are handled by
`bootstrap.sh` / `setup_macos_dev.py`; **manual** items can't be scripted
(logins, TCC permission grants) or are deliberately out of scope.

## Menu-bar app suite (automated)

Built from personal repos cloned side-by-side under `~/Code` (the apps depend
on the frameworks via local `../` SPM paths), then symlinked into
`~/Applications` so rebuilds propagate. Start-at-login lives inside each app
(SMAppService), not in a LaunchAgent.

| App | Repo | Notes |
|---|---|---|
| ProcessMonitor.app | MacOS_Process_Monitor | |
| VPN & DNS.app | vpn-dns-menubar | one dot for Mullvad/Tailscale state |
| Battery Time.app | battery-time-menubar | |
| KeyLight.app | keylight-menubar | needs Accessibility (manual grant) |
| MacRecorder.app | MacRecorder | needs Screen Recording (manual grant) |
| Media Tracking Killer.app | media-tracking-killer-menubar | added 2026-07-14; replaces killapplemediatracking.sh |
| Download Recycler.app | download-recycler-menubar | added 2026-07-14; replaces download_recycler.sh; needs Downloads access (manual grant) |
| (framework) | StatusItemKit | shared menu-bar framework + `make-app.sh` + signing |
| (framework) | HotkeyKit | CGEventTap engine used by KeyLight |

Signing: `StatusItemKit/scripts/setup-signing.sh` creates the stable
self-signed "StatusItemKit Local Signing" identity once, so TCC grants
survive rebuilds.

## launchd agents

| Label | Status | Source |
|---|---|---|
| com.nicholassmith.mullvad-tailscale-dns | **automated** | vpn-dns-menubar repo (DNS watcher) |
| com.code-sync.agent | **automated** | code-sync's own `install.sh` (hourly + at login; ~/Code sync) |
| com.nicholassmith.code-catalog | **retired by setup** | the fswatch PROJECTS.md watcher; superseded by code-sync, which schedules itself. The code-sync step boots it out and deletes its plist when it finds one |
| com.nicholassmith.mov-watcher | removed | MOV→MP4 watcher component was dropped 2026-07-14 (never installed anywhere) |
| com.nicholassmith.battery-time-power-watch | **retired by setup** | SwiftBar-era; superseded by the Swift app's in-process IOKit watcher (`main.swift`). The menu-bar suite component boots it out and deletes its plist when it finds one |
| com.nicholassmith.godot-headless-reaper | not reproduced | machine-specific (`~/.local/bin/godot-headless-reaper`) |
| com.nicholassmith.networkscan / networkscan-server | not reproduced | project-specific (`~/Code/networkscan`, github: Network-Scan-Web-UI) |
| com.user.killapplemediatracking | **retired by setup** | replaced by Media Tracking Killer.app (menu-bar suite); suite step boots it out if found |
| com.user.downloadrecycler | **retired by setup** | replaced by Download Recycler.app (menu-bar suite); suite step boots it out if found |

## `~/.local/bin` (beyond what installers create)

| Script | Status |
|---|---|
| newtools | **automated** — vendored in `local_bin/` (exists nowhere else); per-session CLI cheat sheet |
| code-catalog-refresh / code-catalog-watch | **retired** — renamed `.retired` by the code-sync step; no longer vendored |
| claude | **automated** — native Claude Code installer |
| dell-display-fix | manual — BetterDisplay/Dell monitor hardware specific |
| godot-headless-reaper, discord_webhook, routercode, audio-separator*, qwen | manual — project/machine specific |
| uv, uvx, pipenv, yt-dlp | manual — installed by their own installers on demand |

## Shell / CLI (automated)

- Oh My Zsh (robbyrussell theme) + `zsh/.zshrc` (genericized copy of the live
  file: brew-nvm lazy-load, fzf init cache, direnv/zoxide hooks, venv-aware
  `python()`, git helpers, zoxide/atuin init, `newtools` banner; `proj`/`list`/
  `projects` now come from code-sync rather than being defined inline)
- `~/Code/fzf-git.sh` clone (sourced by .zshrc)
- Oh My Zsh custom plugins (git clones, not brew): `zsh-autosuggestions` +
  `fast-syntax-highlighting`, plus a Tab widget that accepts the suggestion and
  falls through to `fzf-completion` otherwise — added 2026-08-17
- Brewfile: curated core (see file); heavier stacks commented out
- Claude Code via native installer; VS Code + `vscode/extensions.txt` (44 ext.)
- git: identity, LFS, gh credential helper (after `gh auth login`)

## Installed outside Homebrew on the audited machine (manual)

- Mullvad VPN (direct download; Brewfile installs the cask on a new machine)
- iTerm2, VS Code, Raycast (direct downloads; casks cover them)
- PostgreSQL 18 (EDB installer, `/Library/PostgreSQL/18`)
- Rust (rustup), Bun, pnpm, Meteor — language installers, run on demand
- App Store: Xcode (only needed for ThemeToggle), Logic Pro, etc.
- LuLu, BetterDisplay, Amphetamine, audio plugins & DAWs — out of scope

## Known machine quirks (documented, not scripted)

- `ssh dino` (home server) only works with Mullvad disconnected.
- SwiftBar cask is installed but retired — plugins unsymlinked; Swift apps
  replaced it. Excluded from the Brewfile.
- BetterTouchTool quarantined in `~/.disabled-apps` (replaced by KeyLight).
- Ice (`jordanbaird-ice@beta`) hides the native Mullvad/Tailscale icons;
  its layout is configured by hand.
- ThemeToggle (this repo's old dark/light toggle) was removed 2026-07-14 —
  macOS now has a light/dark toggle built into Control Center, and it wasn't
  installed on the audited machine anyway.
- Tailscale and Mullvad are individual components (not in the Brewfile) so
  each machine opts in separately; the VPN/DNS watcher needs both.

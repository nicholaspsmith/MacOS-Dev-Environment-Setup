# Shared zsh config from MacOS-Dev-Environment-Setup (zsh/shared.zsh).
# ~/.zshrc sources this through the symlink ~/.config/zsh/shared.zsh, which
# setup component 6 creates -- so a `git pull` of the repo is all it takes to
# update every Mac. Machine-only lines go in ~/.zshrc itself, BELOW the source
# line, where they can override anything here. Don't bind ^I or re-run
# `fzf --zsh` after it: that would undo the Tab widget at the end of this file.

# OPENSPEC:START
# OpenSpec shell completions configuration
fpath=("$HOME/.oh-my-zsh/custom/completions" $fpath)
# compinit is handled by oh-my-zsh below (removed duplicate call)
# OPENSPEC:END

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme: https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME="robbyrussell"

# Cache compinit to skip slow security check on every startup
ZSH_COMPDUMP="${ZSH_CACHE_DIR:-$HOME/.cache}/.zcompdump-${SHORT_HOST}-${ZSH_VERSION}"
DISABLE_COMPFIX=true

# Plugins
# Standard: $ZSH/plugins/
# Custom:  $ZSH_CUSTOM/plugins/
plugins=(git python macos virtualenv)

# Inline autosuggestions (grey ghost text from history) + command syntax
# highlighting. Cloned into $ZSH_CUSTOM/plugins by the setup script; appended
# only when present so a bare .zshrc copy still starts cleanly without them.
# Order matters: fast-syntax-highlighting must come LAST -- it wraps every ZLE
# widget defined before it -- and zsh-autosuggestions must immediately precede it.
for _omz_plugin in fzf-tab zsh-autosuggestions fast-syntax-highlighting; do
  [[ -d "${ZSH_CUSTOM:-$ZSH/custom}/plugins/$_omz_plugin" ]] && plugins+=("$_omz_plugin")
done
unset _omz_plugin

# Suggest from shell history, falling back to completions when history misses.
# atuin, when installed, prepends its own strategy to this array at init time,
# so suggestions come from the synced atuin DB first.
ZSH_AUTOSUGGEST_STRATEGY=(history_valid completion)

# `cd <name>` finds projects from anywhere: a relative name that is not under
# $PWD is looked up in ~/Code next (zsh prints where it landed).
[[ -d ~/Code ]] && cdpath=(~/Code)

# History remembers `cd foo` typed in ~/Code, then offers it back in ~ where
# foo does not exist. _hv_ok rejects a `cd`/`pushd` whose target does not
# resolve from here (cdpath included); anything else passes untouched. Shared
# by the ghost-text strategy below and the ↑/↓ cycling (_hcyc_load), so the
# first ↓ still lands on exactly the line shown as ghost text.
_hv_ok() {
  local -a w=( ${(z)1} )
  [[ $w[1] == (cd|pushd) ]] || return 0
  local d=${(Q)w[2]}
  [[ -z $d || $d == (-|-*|\;|\&\&|\|\|) ]] && return 0
  d=${d/#\~/$HOME}
  [[ -d $d ]] && return 0
  [[ $d == (/|./|../)* ]] && return 1
  local p; for p in $cdpath; do [[ -d $p/$d ]] && return 0; done
  return 1
}

# zsh-autosuggestions' own history strategy, minus suggestions _hv_ok rejects:
# a rejected entry is excluded from the pattern and the next-newest one tried.
_zsh_autosuggest_strategy_history_valid() {
  emulate -L zsh
  setopt EXTENDED_GLOB
  local prefix="${1//(#m)[\\*?[\]<>()|^~#]/\\$MATCH}"
  local base="$prefix*" pattern cand
  [[ -n $ZSH_AUTOSUGGEST_HISTORY_IGNORE ]] && base="($base)~($ZSH_AUTOSUGGEST_HISTORY_IGNORE)"
  local -a bad
  local -i n
  for (( n = 0; n < 20; n++ )); do
    pattern=$base
    (( $#bad )) && pattern="($base)~(${(j:|:)bad})"
    cand="${history[(r)$pattern]}"
    [[ -z $cand ]] && return
    _hv_ok "$cand" && { typeset -g suggestion=$cand; return }
    bad+=( ${(b)cand} )
  done
}

# Homebrew zsh completions — must join fpath BEFORE oh-my-zsh runs compinit
[[ -d /opt/homebrew/share/zsh/site-functions ]] && fpath=(/opt/homebrew/share/zsh/site-functions $fpath)

# The machine's short name ("MacBook-Pro-M1" -> "M1"), for the tab title and
# the SSH prompt tag below.
typeset -g _host_short=${${HOST%%.*}#MacBook-Pro-}
source $ZSH/oh-my-zsh.sh

# The terminal tab reads "<machine>: Shell", or "<machine>: Claude" while
# Claude Code runs (iterm-claude-tab-color then swaps in the session's name
# once it has one). oh-my-zsh calls title() with the directory at the prompt
# and the command word while one runs; reduce both to those two labels.
if (( ${+functions[title]} )); then
  functions[_omz_title]=$functions[title]
  title() {
    local label=Shell
    [[ $1 == (claude|claude-local|llm) ]] && label=Claude
    _omz_title "$_host_short: $label" "$_host_short: $label"
  }
fi

# Over SSH, put the machine in front of the prompt so a remote shell never
# passes for a local one: "MacBook-Pro-M1" shows as a magenta [M1].
if [[ -n $SSH_CONNECTION ]]; then
  PROMPT="%F{magenta}%B[$_host_short]%b%f $PROMPT"
fi

# Shortcut to reload .zshrc
alias zshrc='source ~/.zshrc'
alias zshconfig='/opt/homebrew/bin/nvim ~/.zshrc'

# use nvim instead of vim
alias vim='/opt/homebrew/bin/nvim'


## PATH Configuration ##
# Consolidated at the top for clarity and maintainability

export PATH=/opt/homebrew/bin:$PATH
export PATH="$PATH:$HOME/.rvm/bin"
export PATH="$HOME/.meteor:$PATH"
export PATH="$PATH:$HOME/.local/bin"
# VS Code 'code' CLI (harmless if VS Code isn't installed)
export PATH="$PATH:/Applications/Visual Studio Code.app/Contents/Resources/app/bin"
export PATH="$PATH:$HOME/.cargo/bin/rust-analyzer"
export PATH="$PATH:/Library/PostgreSQL/18/bin"
export PNPM_HOME="$HOME/Library/pnpm"
case ":$PATH:" in
  *":$PNPM_HOME:"*) ;;
  *) export PATH="$PNPM_HOME:$PATH" ;;
esac
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

## Git Shortcuts ##

# Git commit alias function
function commit() {
  git commit -m "$1"
}

# Git amend no-verify alias function
function amend() {
	git commit --amend --no-verify
}

# Git push alias function
push() {
  git push origin $(git branch --show-current)
}

# Git add alias function
function add() {
	git add .
}

# Git push origin master/main
function gpom() {
  if git show-ref --quiet refs/remotes/origin/main; then
    git push origin main
  else
    git push origin master
  fi
}

# Git pull origin master/main
function gpum() {
  if git show-ref --quiet refs/remotes/origin/main; then
    git pull origin main
  else
    git pull origin master
  fi
}

## Utility Funcs ##
getpid() {
  ps aux | grep $1 | grep -v grep | awk '{print $2, $11}'
}


## Python Config ##

# Remember if we were in a venv before sourcing
if [[ -n "$VIRTUAL_ENV" ]]; then
    _OLD_VIRTUAL_ENV="$VIRTUAL_ENV"
fi

# Remove the existing alias
unalias python 2>/dev/null || true

# python command will automatically call venv python install when available
python() {
  if [[ -n "$VIRTUAL_ENV" ]]; then
    # set python alias to virtual env install of python
    "$VIRTUAL_ENV/bin/python" "$@"
  elif [[ -x /opt/homebrew/bin/python3 ]]; then
    # set python alias to global (Homebrew) python
    /opt/homebrew/bin/python3 "$@"
  else
    command python3 "$@"
  fi
}

# (Python) Reactivate venv if we were in one (needs to be last in .zshrc)
if [[ -n "$_OLD_VIRTUAL_ENV" ]] && [[ -f "$_OLD_VIRTUAL_ENV/bin/activate" ]]; then
    source "$_OLD_VIRTUAL_ENV/bin/activate"
    unset _OLD_VIRTUAL_ENV
fi


## C++ ##

# boost library config
# For Apple Silicon Macs (adjust path if on Intel Mac)
export BOOST_ROOT="/opt/homebrew/opt/boost"
export BOOST_INCLUDEDIR="$BOOST_ROOT/include"
export BOOST_LIBRARYDIR="$BOOST_ROOT/lib"

# Some build systems also look for these
export CPLUS_INCLUDE_PATH="$BOOST_ROOT/include:$CPLUS_INCLUDE_PATH"
export LIBRARY_PATH="$BOOST_ROOT/lib:$LIBRARY_PATH"
export LD_LIBRARY_PATH="$BOOST_ROOT/lib:$LD_LIBRARY_PATH"

# For C(++) Libraries
# For Apple Silicon
export PKG_CONFIG_PATH="/opt/homebrew/opt/libarchive/lib/pkgconfig:/opt/homebrew/opt/libsigc++@2/lib/pkgconfig:/opt/homebrew/opt/cairomm@1.14/lib/pkgconfig:/opt/homebrew/opt/pangomm@2.46/lib/pkgconfig:$PKG_CONFIG_PATH"





# Set default editor to nvim
export EDITOR="/opt/homebrew/bin/nvim"
export VISUAL="code"

# bun completions
[ -s "$HOME/.bun/_bun" ] && source "$HOME/.bun/_bun"

## NVM (Node Version Manager) ##
# Lazy-loaded: NVM is only sourced on first use of nvm/node/npm/npx

export NVM_DIR="$HOME/.nvm"

# Internal function to load NVM (called once, then removes itself)
_load_nvm() {
  [ -s "/opt/homebrew/opt/nvm/nvm.sh" ] && \. "/opt/homebrew/opt/nvm/nvm.sh"
  [ -s "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm" ] && \. "/opt/homebrew/opt/nvm/etc/bash_completion.d/nvm"
}

# Lazy-load wrapper: first call to nvm/node/npm/npx triggers NVM load
for _nvm_cmd in nvm node npm npx; do
  eval "${_nvm_cmd}() { unfunction nvm node npm npx 2>/dev/null; _load_nvm; ${_nvm_cmd} \"\$@\" }"
done
unset _nvm_cmd

## FZF with Caching ##
# Cache fzf initialization to improve startup time

FZF_CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/zsh-fzf"
FZF_CACHE_FILE="$FZF_CACHE_DIR/init.zsh"

# Create cache directory if it doesn't exist
mkdir -p "$FZF_CACHE_DIR"

# Check if cache exists and is recent (less than 1 week old)
if command -v fzf >/dev/null; then
  if [[ -f "$FZF_CACHE_FILE" ]] && [[ -s "$FZF_CACHE_FILE" ]] && [[ $(($(date +%s) - $(stat -f%m "$FZF_CACHE_FILE" 2>/dev/null || echo 0))) -lt 604800 ]]; then
    source "$FZF_CACHE_FILE"
  else
    fzf --zsh > "$FZF_CACHE_FILE" 2>/dev/null
    source "$FZF_CACHE_FILE"
  fi
fi

[[ -f ~/Code/fzf-git.sh/fzf-git.sh ]] && source ~/Code/fzf-git.sh/fzf-git.sh

# --- fzf-tab ---
# Tab completion rendered as an fzf picker: every candidate the completion
# system knows about, with its description, fuzzy-searchable. This is where
# contextual options live (`brew <TAB>` lists all 194 subcommands); the arrow
# keys stay on history, which is a different question with a different answer.
#
# Wiring, which is entirely automatic and worth not breaking:
#   * fzf-tab is loaded from plugins=() above -- after compinit, and before
#     zsh-autosuggestions / fast-syntax-highlighting, which wrap widgets.
#   * It binds ^I. Then `fzf --zsh` (further up) rebinds ^I to fzf-completion,
#     but first records the previous owner in $fzf_default_completion -- so it
#     falls back to fzf-tab whenever the line has no `**` trigger. Both survive:
#     `brew <TAB>` gets the fzf-tab menu, `vim **<TAB>` gets fzf's path search.
#   * The Tab widget near the end of this file then captures fzf-completion as
#     its own fallback, so a showing suggestion still wins over both.
# fzf-tab drives the menu itself, so zsh must not also draw one. oh-my-zsh sets
# `menu select` at ':completion:*:*:*:*:*', which is MORE specific than
# ':completion:*' and would win on zstyle's most-specific-match rule -- so the
# override has to name that exact pattern too, not just the general one.
zstyle ':completion:*' menu no
zstyle ':completion:*:*:*:*:*' menu no
# Group headers, so `brew <TAB>` separates subcommands from flags.
zstyle ':completion:*:descriptions' format '[%d]'
zstyle ':fzf-tab:*' switch-group '<' '>'
# Colorise filename completions the way ls does.
zstyle ':completion:*' list-colors ${(s.:.)LS_COLORS}
# Preview the directory you are about to cd into.
command -v eza >/dev/null && \
  zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --color=always $realpath'
# git checkout candidates are already in a meaningful order; do not re-sort.
zstyle ':completion:*:git-checkout:*' sort false
# --- end fzf-tab ---

command -v direnv >/dev/null && eval "$(direnv hook zsh)"

# Home server (Tailscale-only host; needs an ~/.ssh/config entry). mosh survives
# sleep and network roaming, so prefer it and fall back to ssh.
if command -v mosh >/dev/null; then
  alias dino='mosh dino'
else
  alias dino='ssh dino'
fi

# --- Modern CLI toolkit ---
# zoxide: `z <name>` jumps to a directory by frecency.
command -v zoxide >/dev/null && eval "$(zoxide init zsh)"

# atuin: fuzzy, syncable shell history. Takes over ^R, so it must load AFTER
# fzf above or fzf's ^R would win. It also prepends its own strategy to
# ZSH_AUTOSUGGEST_STRATEGY, making the synced atuin DB the first source of
# autosuggestions.
command -v atuin >/dev/null && eval "$(atuin init zsh)"

# Per-session cheat sheet for the toolkit; `newtools table` for the comparison.
command -v newtools >/dev/null && newtools
# --- end Modern CLI toolkit ---

# --- inline history cycling, overflowing into atuin ---
# Standard shell direction: ↑ goes older, ↓ goes newer. Both walk in place
# through the history entries that start with whatever is already typed (or
# through all of history, when the line is empty).
#
#   ↑            step to the next older match -- repeat to keep digging
#   ↑ past end   atuin's full-screen search takes over, pre-filtered with the
#                text you typed rather than whichever candidate was on screen
#   ↓            step to the next older match (the ghost text is the first)
#   ↑            step back toward the newest, then to the line you typed,
#                verbatim; ↑ once more hands it to atuin's full-screen search
#   ↓ no matches falls through to the normal down-line-or-history
#
# A hand-typed line is never lost: the first ↑/↓ that leaves it also saves it
# to zsh history and atuin (_hcyc_save), unless that exact line is already in
# history -- so a mistyped or half-finished command can be ↑'d back and fixed.
#
# Hand-rolled rather than zsh-history-substring-search: that plugin has no
# concept of "out of matches", which is precisely the hand-off this needs.
# Candidates are atuin's recent/synced entries first, then zsh's much deeper
# HISTFILE -- see _hcyc_load for why one cannot stand in for the other.

typeset -g  _hcyc_typed=''      # what the user actually typed
typeset -ga _hcyc_hits=()       # candidates, newest first
typeset -gi _hcyc_i=0           # 0 = the typed text, 1..N = candidates
typeset -g  _hcyc_shown=$'\0'   # last buffer we wrote, to notice hand edits
typeset -gi _hcyc_limit=50      # cycle depth before atuin takes over

_hcyc_load() {
  _hcyc_typed=$BUFFER
  local -a raw hist
  # atuin first: recent, and synced across machines. --filter-mode global is
  # explicit because session/directory modes return almost nothing here.
  if command -v atuin >/dev/null; then
    # atuin prints oldest-first; (Oa) flips the array to newest-first.
    raw=( ${(Oa)${(f)"$(atuin search --search-mode prefix --filter-mode global \
                          --limit $_hcyc_limit --cmd-only -- "$BUFFER" 2>/dev/null)"}} )
  fi
  # Then zsh's own HISTFILE, APPENDED rather than used as a fallback. atuin's DB
  # only goes back to whenever atuin was installed (weeks), while HISTFILE goes
  # back years -- so atuin returning *a* match is not the same as it having them
  # all. Treating it as a fallback made `brew` cycle through exactly one entry,
  # the very one already showing as ghost text.
  hist=( ${(M)${(f)"$(fc -lnr 1 2>/dev/null)"}:#${(b)BUFFER}*} )
  raw=( $raw $hist )
  raw=( ${raw:#} )                                  # drop blank lines
  # (b) quotes glob characters so a stray [ or * in the line is not a pattern.
  # (u) dedupes keeping first occurrence, so atuin's recent hits stay on top.
  _hcyc_hits=( ${(u)${raw:#${(b)_hcyc_typed}}} )    # dedupe, drop the typed text
  local c; raw=( $_hcyc_hits ); _hcyc_hits=()       # drop impossible `cd`s
  for c in $raw; do _hv_ok "$c" && _hcyc_hits+=( $c ); done
  (( $#_hcyc_hits > _hcyc_limit )) && _hcyc_hits=( ${_hcyc_hits[1,_hcyc_limit]} )
  _hcyc_i=0
}

# Save the line the user typed before ↑/↓ replaces it. Exact lines already in
# history are skipped, which also keeps a bare prefix like `git` out of it.
typeset -g _hcyc_saved=''
_hcyc_save() {
  emulate -L zsh -o extendedglob
  local d=${${1##[[:space:]]##}%%[[:space:]]##}
  [[ -n $d && $d != *$'\n'* && $d != "$_hcyc_saved" ]] || return 0
  [[ -n ${history[(re)$d]} ]] && return 0
  _hcyc_saved=$d
  print -sr -- "$d"
  if [[ -n $ATUIN_SESSION ]] && command -v atuin >/dev/null; then
    local id=$(atuin history start -- "$d" 2>/dev/null)
    [[ -n $id ]] && { atuin history end --exit 0 --duration 0 -- "$id" &>/dev/null &! }
  fi
  return 0
}

_hcyc_put() {
  BUFFER=$1; CURSOR=$#BUFFER; _hcyc_shown=$BUFFER
  # This widget is wrapped by neither plugin (both bind at load, we define after),
  # so clear the stale ghost text and re-run highlighting by hand.
  POSTDISPLAY=''
  (( ${+functions[_zsh_highlight]} )) && _zsh_highlight
}

# Past the top of the list: atuin's search when atuin is loaded, otherwise
# plain history so ↑ still works on a machine without it.
_hcyc_overflow() {
  if (( ${+widgets[atuin-up-search]} )); then zle atuin-up-search
  else zle up-line-or-history; fi
}

_hcyc_up() {                                        # back up the list, then atuin
  [[ $BUFFER == *$'\n'* ]] && { zle up-line-or-history; return }
  # Not cycling: we are already sitting at candidate 1 (whatever the ghost text
  # is showing), so there is nothing above it but atuin. BUFFER is still the
  # typed text here, which is exactly what atuin should be seeded with (and
  # what its Esc hands back).
  if [[ $BUFFER != "$_hcyc_shown" ]]; then
    _hcyc_save "$BUFFER"
    _hcyc_shown=$'\0'
    _hcyc_overflow
    return
  fi
  # Cycling and back at the line that was typed: atuin, seeded with that text.
  if (( _hcyc_i <= 0 )); then
    _hcyc_shown=$'\0'
    _hcyc_overflow
    return
  fi
  (( _hcyc_i-- ))
  if (( _hcyc_i == 0 )); then _hcyc_put "$_hcyc_typed"
  else _hcyc_put "$_hcyc_hits[_hcyc_i]"; fi
}

_hcyc_down() {                                      # deeper: the next suggestion
  [[ $BUFFER == *$'\n'* ]] && { zle down-line-or-history; return }
  if [[ $BUFFER != "$_hcyc_shown" ]]; then          # fresh line or hand-edited
    _hcyc_load
    (( $#_hcyc_hits )) || { zle down-line-or-history; return }
    _hcyc_save "$BUFFER"
    # A ghost suggestion on screen already IS candidate 1, so the first press
    # should reveal candidate 2. With no ghost showing, start at 1 instead.
    [[ -n $POSTDISPLAY ]] && _hcyc_i=1 || _hcyc_i=0
  fi
  (( _hcyc_i >= $#_hcyc_hits )) && return           # deepest already; stay put
  (( _hcyc_i++ ))
  _hcyc_put "$_hcyc_hits[_hcyc_i]"
}

zle -N _hcyc_up
zle -N _hcyc_down
bindkey '^[[A' _hcyc_up   ; bindkey '^[OA' _hcyc_up
bindkey '^[[B' _hcyc_down ; bindkey '^[OB' _hcyc_down
# --- end inline history cycling ---

# --- Tab: accept the suggestion, else complete ---
# Tab takes the grey ghost text when one is showing (cursor at end of line);
# with nothing suggested it falls through to fzf-completion, which hands off to
# the fzf-tab picker -- that picker is for commands with real choices
# (`git checkout <TAB>` branches, `brew <TAB>` subcommands, `kill <TAB>` PIDs).
# Safe now that impossible `cd`s never become ghost text (_hv_ok, top of file).
# Must stay below `fzf --zsh` and fzf-tab, which both bind ^I.
_tab_accept_or_complete() {
  if [[ -n $POSTDISPLAY && $CURSOR -eq $#BUFFER ]] && (( $+widgets[autosuggest-accept] )); then
    zle autosuggest-accept
  elif (( $+widgets[fzf-completion] )); then
    zle fzf-completion
  else
    zle expand-or-complete                          # no fzf on this machine
  fi
}
zle -N _tab_accept_or_complete
bindkey '^I' _tab_accept_or_complete
# --- end Tab ---

# --- paste: undo terminal-width line wrapping ---
# Claude Code (and other TUIs) wrap long lines themselves, so copying a command
# off the screen brings hard newlines at the wrap points plus the indentation
# of the block it was drawn in. Pasting that leaves a broken multi-line command
# -- and the leading spaces keep it out of history (histignorespace, and atuin
# skips space-prefixed commands too). This hook rewrites the pasted text:
#
#   - removes the indentation every line shares, and leading spaces entirely
#     when pasting at the start of the line
#   - joins a line to the next when the next one's first word would not have
#     fit on it at this terminal's width -- i.e. the break is a wrap, not a
#     line the author wrote. Where the words either side of the break add up
#     to more than a full line, one token (a long URL) was cut in two, so
#     those halves are joined with no space.
#
# Real multi-line pastes keep their newlines: short lines, lines ending in `\`,
# blank lines, heredocs, and anything with a line wider than this terminal
# (it was not wrapped here). Tune with PASTE_UNWRAP_SLACK (columns of right
# margin the wrapping app leaves, default 10); PASTE_UNWRAP=0 turns it off.
# Undo (^_) after a paste removes the whole paste.
_paste_unwrap() {
  emulate -L zsh -o extendedglob
  [[ ${PASTE_UNWRAP:-1} == 1 ]] || return 0
  [[ $PASTED == *$'\n'* || $PASTED == [[:space:]]* ]] || return 0
  local -a in out
  local l ind row
  local -i i min=-1 maxrow=0 W=${COLUMNS:-80} slack=${PASTE_UNWRAP_SLACK:-10}
  in=( "${(@f)${PASTED//$'\r'/}}" )
  while (( $#in )) && [[ $in[-1] != *[^[:space:]]* ]]; do in[-1]=(); done
  (( $#in )) || return 0
  for l in "${in[@]}"; do
    row=${l%%[[:space:]]##}
    (( $#row > maxrow )) && maxrow=$#row
    [[ $l == *[^[:space:]]* ]] || continue
    ind=${l%%[^[:space:]]*}
    (( min < 0 || $#ind < min )) && min=$#ind
  done
  local join=1
  (( maxrow > W )) && join=0                        # not wrapped at this width
  [[ $PASTED == *'<<'* ]] && join=0                 # heredoc: lines are lines
  local cur=${in[1]:$min} next nw lw sep
  [[ $LBUFFER == *[^[:space:]]* ]] && cur=${in[1]}  # mid-line: keep its spacing
  for (( i = 2; i <= $#in; i++ )); do
    next=${in[i]:$min}
    row=${in[i-1]%%[[:space:]]##}                   # the row as drawn, indent included
    nw=${${next##[[:space:]]##}%%[[:space:]]*}
    lw=${row##*[[:space:]]}
    if (( join )) && [[ -n $nw && $cur != *\\ ]] && (( $#row + 1 + $#nw > W - slack )); then
      sep=' '
      [[ ${in[i-1]} != *[[:space:]] ]] && (( $#lw + $#nw > W - slack - min )) && sep=''
      cur="${cur%%[[:space:]]##}$sep${next##[[:space:]]##}"
    else
      out+=( "$cur" ); cur=$next
    fi
  done
  out+=( "$cur" )
  [[ $LBUFFER != *[^[:space:]]* ]] && out[1]=${out[1]##[[:space:]]##}
  PASTED=${(F)out}
}
zstyle -a :bracketed-paste-magic paste-init _paste_hooks
zstyle :bracketed-paste-magic paste-init ${_paste_hooks:#_paste_unwrap} _paste_unwrap
unset _paste_hooks
# --- end paste ---

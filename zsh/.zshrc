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
for _omz_plugin in zsh-autosuggestions fast-syntax-highlighting; do
  [[ -d "${ZSH_CUSTOM:-$ZSH/custom}/plugins/$_omz_plugin" ]] && plugins+=("$_omz_plugin")
done
unset _omz_plugin

# Suggest from shell history, falling back to completions when history misses.
# atuin, when installed, prepends its own strategy to this array at init time,
# so suggestions come from the synced atuin DB first.
ZSH_AUTOSUGGEST_STRATEGY=(history completion)

# Homebrew zsh completions — must join fpath BEFORE oh-my-zsh runs compinit
[[ -d /opt/homebrew/share/zsh/site-functions ]] && fpath=(/opt/homebrew/share/zsh/site-functions $fpath)

source $ZSH/oh-my-zsh.sh

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

# --- Tab accepts the autosuggestion ---
# Tab accepts the grey suggestion when one is showing and the cursor sits at end
# of line; otherwise it falls through to normal completion.
#
# MUST RUN AFTER EVERYTHING THAT BINDS ^I. It captures whichever widget owns ^I
# at this point rather than hardcoding one, because `fzf --zsh` rebinds Tab to
# fzf-completion further up -- hardcoding expand-or-complete here would silently
# kill fzf's `**<TAB>` fuzzy trigger. Whatever binds ^I last wins, so any new
# Tab-binding tool (fzf-tab, etc.) has to be added above this block.
#
# The `projects` block below is the one exception: code-sync's install.sh always
# appends it to the end of the file, so this block cannot be literally last on a
# fully-installed machine. That is fine -- it binds Esc-s, never ^I. Nothing that
# touches ^I may go below here.
if (( ${+functions[_zsh_autosuggest_start]} )); then
  _tab_orig_widget="${$(bindkey '^I')##* }"
  [[ -z "$_tab_orig_widget" || "$_tab_orig_widget" == "undefined-key" ]] \
    && _tab_orig_widget=expand-or-complete

  _tab_accept_or_complete() {
    if [[ -n "$POSTDISPLAY" ]] && (( CURSOR == ${#BUFFER} )); then
      zle autosuggest-accept
    else
      zle "$_tab_orig_widget"
    fi
  }
  zle -N _tab_accept_or_complete
  bindkey '^I' _tab_accept_or_complete
fi
# --- end Tab accepts the autosuggestion ---

# --- inline history cycling, overflowing into atuin ---
# ↑/↓ walk in place through the history entries that start with whatever is
# already typed. Run off the far end going up and atuin's full-screen search
# takes over, pre-filtered with that same text; come back down past the newest
# match and the line you actually typed is restored verbatim.
#
# Hand-rolled rather than zsh-history-substring-search: that plugin has no
# concept of "out of matches", which is precisely the hand-off this needs.
# Candidates come from atuin, so the cycle agrees with the grey ghost text
# rather than drawing on a second, unsynced history.

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
  (( $#_hcyc_hits > _hcyc_limit )) && _hcyc_hits=( ${_hcyc_hits[1,_hcyc_limit]} )
  _hcyc_i=0
}

_hcyc_put() {
  BUFFER=$1; CURSOR=$#BUFFER; _hcyc_shown=$BUFFER
  # This widget is wrapped by neither plugin (both bind at load, we define after),
  # so clear the stale ghost text and re-run highlighting by hand.
  POSTDISPLAY=''
  (( ${+functions[_zsh_highlight]} )) && _zsh_highlight
}

_hcyc_up() {
  [[ $BUFFER == *$'\n'* ]] && { zle up-line-or-history; return }
  # Bare ↑ on an empty line keeps its old meaning: straight into atuin.
  [[ -z $BUFFER && $BUFFER != "$_hcyc_shown" ]] && { zle atuin-up-search; return }
  [[ $BUFFER != "$_hcyc_shown" ]] && _hcyc_load
  if (( _hcyc_i >= $#_hcyc_hits )); then            # out of candidates
    _hcyc_put "$_hcyc_typed"                        # hand atuin the typed text
    _hcyc_shown=$'\0'
    zle atuin-up-search
    return
  fi
  (( _hcyc_i++ ))
  _hcyc_put "$_hcyc_hits[_hcyc_i]"
}

_hcyc_down() {
  [[ $BUFFER == *$'\n'* ]] && { zle down-line-or-history; return }
  if [[ $BUFFER != "$_hcyc_shown" ]]; then            # not cycling yet -> enter it
    _hcyc_load
    (( $#_hcyc_hits )) || return
    _hcyc_i=1; _hcyc_put "$_hcyc_hits[1]"; return
  fi
  if (( _hcyc_i <= 1 )); then                       # back past the newest match
    _hcyc_i=0; _hcyc_put "$_hcyc_typed"; return
  fi
  (( _hcyc_i-- ))
  _hcyc_put "$_hcyc_hits[_hcyc_i]"
}

zle -N _hcyc_up
zle -N _hcyc_down
bindkey '^[[A' _hcyc_up   ; bindkey '^[OA' _hcyc_up
bindkey '^[[B' _hcyc_down ; bindkey '^[OB' _hcyc_down
# --- end inline history cycling ---

# --- projects (code-sync) ---
# `proj` (fuzzy-pick a ~/Code project and cd into it), `list`, `projects`, and
# the status block printed when a shell lands on ~/Code. This replaced the old
# fswatch-based PROJECTS.md catalog -- there is no resident daemon any more.
#
# Lives LAST because code-sync's install.sh rewrites this marker-delimited region
# by stripping it and re-appending at end-of-file. Keeping it here means the
# shipped file already matches what a fully-installed machine looks like, so
# component 18 is a no-op on ordering instead of a reshuffle. install.sh also
# rewrites the path below to an absolute one. Edit the helpers in code-sync.
[[ -f "$HOME/Code/code-sync/shell/proj.sh" ]] && . "$HOME/Code/code-sync/shell/proj.sh"
# --- end projects ---

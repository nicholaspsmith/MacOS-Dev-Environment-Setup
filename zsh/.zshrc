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

# You can run this to connect to the dinoserver hp dl380 when on tailscale
# ssh dino
alias dino='ssh dino'

# --- ~/Code project catalog (see ~/Code/.claude/specs/2026-06-11-code-catalog-design.md) ---
command -v zoxide >/dev/null && eval "$(zoxide init zsh)"

# Fuzzy-pick a project by name/description/status and cd into it.
# ctrl-t: order by last commit · ctrl-y: order by last change · ctrl-r: status order
proj() {
  local root=~/Code catalog=~/Code/PROJECTS.md line name
  if [[ -f $catalog ]]; then
    local rows="grep '^|' $catalog | grep -v '^| Project ' | grep -v '^|-'"
    line=$(eval "$rows" | fzf \
      --header='name | status | description | lang | last commit | last change | git    [ctrl-t: by commit · ctrl-y: by change · ctrl-r: status order]' \
      --bind "ctrl-t:reload($rows | sort -t'|' -k6,6r)" \
      --bind "ctrl-y:reload($rows | sort -t'|' -k7,7r)" \
      --bind "ctrl-r:reload($rows)" \
      --preview 'n=$(printf "%s" {} | cut -d"|" -f2 | xargs);
                 head -40 ~/Code/"$n"/README.md 2>/dev/null;
                 echo "————";
                 git -C ~/Code/"$n" log -3 --oneline 2>/dev/null')
    name=$(printf '%s' "$line" | cut -d'|' -f2 | xargs)
  else
    name=$(command ls ~/Code | fzf)
  fi
  [[ -n $name && -d $root/$name ]] && cd "$root/$name"
}

# List catalog rows, optionally filtered: projlist [active|idle|stale|dormant|
# ancient|renamed|needs|clone|own|local|<any substring>]. Aliased as `list`.
projlist() {
  local catalog=~/Code/PROJECTS.md
  [[ -f $catalog ]] || { print -u2 "projlist: $catalog not found"; return 1 }
  awk -F'|' -v q="${1:-}" '/^\|/ && $2 !~ /Project/ && $2 !~ /^[ :-]*$/ {
      s=$3; gsub(/^ +| +$/,"",s)
      if (q=="" || s==q || index($0,q)) print
    }' "$catalog" | column -t -s'|'
}
alias list=projlist

# Browse the catalog rendered as markdown (glow pager; falls back to $PAGER).
projects() {
  if command -v glow >/dev/null; then
    glow -p -w ${COLUMNS:-160} ~/Code/PROJECTS.md
  else
    ${PAGER:-less} ~/Code/PROJECTS.md
  fi
}

# Banner when a shell lands exactly on ~/Code.
_code_catalog_banner() {
  [[ $PWD == ~/Code && -f ~/Code/PROJECTS.md ]] || return 0
  awk -F'\\|' '/^\|/ && $2 !~ /Project/ && $2 !~ /^[ :-]*$/ {
      s=$3; gsub(/^ +| +$/,"",s); c[s]++; total++
      d=$4; gsub(/^ +| +$/,"",d); if (d=="") nodesc++
    }
    END {
      printf "📁 %d projects", total
      n=split("active idle stale dormant ancient renamed", t, " ")
      for (i=1;i<=n;i++) if (c[t[i]]) printf " · %d %s", c[t[i]], t[i]
      if (nodesc) printf " · %d undescribed", nodesc
      print "\n   proj → fuzzy-pick & cd (^t: by commit · ^y: by change · ^r: status order)"
      print "   list [status|text] → filtered table · z <name> → jump from anywhere"
      print "   projects → browse catalog (glow) · code-catalog-refresh → manual refresh"
    }' ~/Code/PROJECTS.md
}
autoload -U add-zsh-hook
add-zsh-hook chpwd _code_catalog_banner
_code_catalog_banner
# --- end ~/Code project catalog ---

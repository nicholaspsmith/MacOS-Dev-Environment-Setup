

# Path to your oh-my-zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# Set name of the theme to load. Optionally, if you set this to "random"
# it'll load a random theme each time that oh-my-zsh is loaded.
# See https://github.com/robbyrussell/oh-my-zsh/wiki/Themes
ZSH_THEME="robbyrussell"


# Which plugins would you like to load? 
# (plugins can be found in ~/.oh-my-zsh/plugins/*)
# Custom plugins may be added to ~/.oh-my-zsh/custom/plugins/
plugins=(
  git
  python
  macos
)

source $ZSH/oh-my-zsh.sh

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion


# User configuration

alias python="python3"

alias zshconfig="vim ~/.zshrc"
alias zshrc="source ~/.zshrc"
alias ohmyzsh="vim ~/.oh-my-zsh"


## Git Shortcuts ##

# Git status alias
alias status="git status"

# Git commit alias function
function commit() {
  git commit -m "$1"
}

# Git checkout alias function
function co() {
	git checkout $1
}

# Git amend no-verify alias function
function amend() {
	git commit --amend --no-verify
}

# Git checkout -b alias function
function branch() {
	git checkout -b "$1"
}

# Git push alias function
push() {
  git push origin $(git branch --show-current)
}

# Git add alias function
function add() {
	git add .
}


## cron / crontab ##

# View crontab files alias function
function view_crontab_file() {
  sudo su
  cd /var/at/tabs
}


## Homebrew ##

# Add brew command to path
export PATH=/opt/homebrew/bin:$PATH

# Add Homebrew's zsh completions to fpath
if type brew &>/dev/null; then
  fpath=($(brew --prefix)/share/zsh/site-functions $fpath)
fi



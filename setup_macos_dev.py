#!/usr/bin/env python3
"""
Complete macOS Development Environment Setup
Automatically installs and configures a full development environment on
macOS 15+ (tested on macOS 26 Tahoe, Apple Silicon).

Run via ./bootstrap.sh on a fresh machine (installs CLT + Homebrew first).
"""

import subprocess
import sys
import os
import platform
import shutil
import json
import webbrowser
import plistlib
import curses
import argparse
from pathlib import Path

# Personal repos that make up the menu-bar app suite. The apps depend on the
# frameworks via local `../` SPM paths, so everything must be cloned
# side-by-side under ~/Code before building.
FRAMEWORK_REPOS = [
    ('StatusItemKit', 'https://github.com/nicholaspsmith/StatusItemKit.git'),
    ('HotkeyKit', 'https://github.com/nicholaspsmith/HotkeyKit.git'),
]
MENU_BAR_APP_REPOS = [
    ('MacOS_Process_Monitor', 'https://github.com/nicholaspsmith/MacOS_Process_Monitor.git', 'ProcessMonitor.app'),
    ('vpn-dns-menubar', 'https://github.com/nicholaspsmith/vpn-dns-menubar.git', 'VPN & DNS.app'),
    ('battery-time-menubar', 'https://github.com/nicholaspsmith/battery-time-menubar.git', 'Battery Time.app'),
    ('keylight-menubar', 'https://github.com/nicholaspsmith/keylight-menubar.git', 'KeyLight.app'),
    ('MacRecorder', 'https://github.com/nicholaspsmith/MacRecorder.git', 'MacRecorder.app'),
]

GIT_USER_NAME = 'nicholaspsmith'
GIT_USER_EMAIL = 'npsmith1990@gmail.com'


class MacOSDevSetup:
    def __init__(self, no_confirm=False):
        self.system = platform.system()
        self.macos_version = None
        if self.system == "Darwin":
            self.macos_version = platform.mac_ver()[0]

        self.no_confirm = no_confirm
        self.shell_profile = self.get_shell_profile_path()
        self.success_items = []
        self.failed_items = []
    
    def get_shell_profile_path(self):
        """Determine the correct shell profile path"""
        shell = os.environ.get('SHELL', '/bin/zsh')
        if 'zsh' in shell:
            return Path.home() / '.zshrc'
        elif 'bash' in shell:
            return Path.home() / '.bash_profile'
        else:
            return Path.home() / '.zshrc'  # Default to zsh
    
    def check_macos_compatibility(self):
        """Check if macOS version is compatible (15+)"""
        if self.system != "Darwin":
            print("❌ This script is designed for macOS only.")
            return False
        
        major = int(self.macos_version.split('.')[0])
        if major < 15:
            print(f"❌ This script requires macOS 15 or later. Current version: {self.macos_version}")
            return False
        
        print(f"✅ macOS {self.macos_version} is compatible")
        return True
    
    def run_command(self, command, shell=False, capture_output=True, check=True):
        """Run a shell command safely"""
        try:
            if shell:
                result = subprocess.run(command, shell=True, capture_output=capture_output, 
                                      text=True, check=check)
            else:
                result = subprocess.run(command.split(), capture_output=capture_output, 
                                      text=True, check=check)
            return result
        except subprocess.CalledProcessError as e:
            if capture_output:
                print(f"❌ Command failed: {command}")
                print(f"Error: {e.stderr if e.stderr else e.stdout}")
            return None
        except FileNotFoundError:
            print(f"❌ Command not found: {command.split()[0]}")
            return None
    
    def add_success(self, item):
        self.success_items.append(item)
        print(f"✅ {item}")
    
    def add_failure(self, item):
        self.failed_items.append(item)
        print(f"❌ {item}")

    def ask_yes_no(self, prompt, default=False):
        """Prompt the user, honoring --no-confirm (returns default without touching stdin)"""
        if self.no_confirm:
            return default
        return input(prompt).lower().strip() in ['y', 'yes']

    def load_launch_agent(self, plist_file, label):
        """(Re)load a LaunchAgent via bootstrap, falling back to legacy load -w"""
        uid = os.getuid()
        self.run_command(f'launchctl bootout gui/{uid}/{label}', shell=True, check=False)
        result = self.run_command(f'launchctl bootstrap gui/{uid} "{plist_file}"',
                                  shell=True, check=False)
        if result and result.returncode == 0:
            return True
        result = self.run_command(f'launchctl load -w "{plist_file}"', shell=True, check=False)
        return bool(result and result.returncode == 0)

    def clone_or_update_repo(self, url, dest):
        """Clone a repo, or fast-forward it if already present.

        Returns 'cloned', 'updated', or 'unchanged' (all truthy) on success,
        False on failure."""
        dest = Path(dest)
        if (dest / '.git').exists():
            result = self.run_command(f'git -C "{dest}" pull --ff-only', shell=True, check=False)
            if result and result.returncode == 0:
                return 'unchanged' if 'Already up to date' in (result.stdout or '') else 'updated'
            print(f"⚠️  Could not update {dest.name} (offline or diverged) — using existing checkout")
            return 'unchanged'
        if dest.exists() and any(dest.iterdir()):
            print(f"❌ {dest} exists but is not a git repo — move it aside and re-run")
            return False
        result = self.run_command(f'git clone "{url}" "{dest}"', shell=True, check=False)
        return 'cloned' if result and result.returncode == 0 else False

    def install_launch_agent(self, label, program_args, log_name, extra=None):
        """Write a KeepAlive LaunchAgent plist and (re)load it. Returns True if loaded now."""
        logs_dir = Path.home() / 'Library' / 'Logs'
        logs_dir.mkdir(parents=True, exist_ok=True)
        launch_agents = Path.home() / 'Library' / 'LaunchAgents'
        launch_agents.mkdir(parents=True, exist_ok=True)
        plist = {
            'Label': label,
            'ProgramArguments': [str(a) for a in program_args],
            'EnvironmentVariables': {'PATH': '/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin'},
            'RunAtLoad': True,
            'KeepAlive': True,
            'StandardOutPath': str(logs_dir / log_name),
            'StandardErrorPath': str(logs_dir / log_name),
        }
        if extra:
            plist.update(extra)
        plist_file = launch_agents / f'{label}.plist'
        with open(plist_file, 'wb') as f:
            plistlib.dump(plist, f)
        return self.load_launch_agent(plist_file, label)

    def install_homebrew(self):
        """Install Homebrew"""
        if shutil.which('brew'):
            self.add_success("Homebrew already installed")
            return True
        
        print("📦 Installing Homebrew...")
        install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        result = self.run_command(install_cmd, shell=True, capture_output=False)
        
        if result:
            # Add Homebrew to PATH for current session
            homebrew_paths = ['/opt/homebrew/bin', '/usr/local/bin']
            for path in homebrew_paths:
                if os.path.exists(path) and path not in os.environ['PATH']:
                    os.environ['PATH'] = f"{path}:{os.environ['PATH']}"
            
            self.add_success("Homebrew installed")
            return True
        else:
            self.add_failure("Homebrew installation failed")
            return False
    
    def install_brew_bundle(self):
        """Install the curated Brewfile (CLI tools, casks, fonts)"""
        print("📦 Installing Brewfile (this can take a while on a fresh machine)...")

        brewfile = Path(__file__).parent / 'Brewfile'
        if not brewfile.exists():
            self.add_failure("Brewfile not found next to setup script")
            return False

        result = self.run_command(f'brew bundle --file="{brewfile}"',
                                  shell=True, capture_output=False, check=False)
        if result and result.returncode == 0:
            self.add_success("Brewfile installed (CLI tools, casks, fonts)")
            return True

        # brew bundle exits non-zero if any single entry failed; report but continue
        self.add_failure("Brewfile completed with errors (run 'brew bundle --file=Brewfile' to retry)")
        return False
    
    def install_oh_my_zsh(self):
        """Install Oh My Zsh"""
        print("📦 Installing Oh My Zsh...")
        
        # Check if already installed
        oh_my_zsh_dir = Path.home() / '.oh-my-zsh'
        if oh_my_zsh_dir.exists():
            self.add_success("Oh My Zsh already installed")
            return True
        
        # Install Oh My Zsh
        install_cmd = 'sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended'
        result = self.run_command(install_cmd, shell=True, capture_output=False)
        
        if result and oh_my_zsh_dir.exists():
            self.add_success("Oh My Zsh installed")
            return True
        else:
            self.add_failure("Oh My Zsh installation failed")
            return False
        
    def copy_zshrc(self):
        """Copy .zshrc into place and clone fzf-git.sh, which it sources"""
        source_zshrc = Path(__file__).parent / 'zsh' / '.zshrc'
        dest_zshrc = Path.home() / '.zshrc'

        try:
            # Check if source file exists
            if not source_zshrc.exists():
                self.add_failure(f".zshrc file not found at {source_zshrc}")
                return False

            # Backup existing .zshrc if it exists
            if dest_zshrc.exists():
                backup_path = dest_zshrc.with_suffix('.zshrc.backup')
                shutil.copy2(dest_zshrc, backup_path)
                print(f"Backed up existing .zshrc to {backup_path}")

            # Copy the new .zshrc
            shutil.copy2(source_zshrc, dest_zshrc)
            self.add_success(f".zshrc copied to {dest_zshrc}")
        except Exception as e:
            self.add_failure(f"Failed to copy .zshrc: {e}")
            return False

        # .zshrc sources ~/Code/fzf-git.sh/fzf-git.sh (guarded, but clone it so it works)
        fzf_git_dir = Path.home() / 'Code' / 'fzf-git.sh'
        fzf_git_dir.parent.mkdir(parents=True, exist_ok=True)
        if self.clone_or_update_repo('https://github.com/junegunn/fzf-git.sh.git', fzf_git_dir):
            self.add_success("fzf-git.sh cloned")
        else:
            self.add_failure("fzf-git.sh clone failed (fzf git bindings unavailable)")
        return True

    def install_nvm(self):
        """Install NVM via Homebrew (matches .zshrc lazy-loader) and Node.js LTS"""
        print("📦 Installing NVM via Homebrew...")

        def nvm_script_path():
            result = self.run_command('brew --prefix nvm', check=False)
            if result and result.returncode == 0:
                path = Path(result.stdout.strip()) / 'nvm.sh'
                if path.exists():
                    return path
            return None

        brew_nvm_script = nvm_script_path()
        if not brew_nvm_script:
            if not self.run_command('brew install nvm'):
                self.add_failure("NVM installation failed")
                return False
            brew_nvm_script = nvm_script_path()
        if not brew_nvm_script:
            self.add_failure("NVM script not found after brew install")
            return False

        (Path.home() / '.nvm').mkdir(exist_ok=True)

        # The repo .zshrc lazy-loads brew's nvm. If the user kept their own
        # profile (didn't run the Copy .zshrc component), wire nvm up there.
        profile_text = self.shell_profile.read_text() if self.shell_profile.exists() else ''
        if 'nvm.sh' not in profile_text and '_load_nvm' not in profile_text:
            self.add_to_shell_profile(
                f'export NVM_DIR="$HOME/.nvm"\n[ -s "{brew_nvm_script}" ] && \\. "{brew_nvm_script}"')
            print("Added NVM sourcing to shell profile")

        print("⚙️ Installing Node.js LTS via NVM...")
        node_cmd = (f'bash -c \'export NVM_DIR="$HOME/.nvm" && source "{brew_nvm_script}" '
                    f'&& nvm install --lts && nvm alias default "lts/*"\'')
        result = self.run_command(node_cmd, shell=True, capture_output=False, check=False)
        if result and result.returncode == 0:
            self.add_success("NVM (Homebrew) and Node.js LTS installed")
            return True
        self.add_failure("Node.js installation via NVM failed")
        return False

    def install_iterm_profile(self):
        """Install iTerm2 (if missing) and the Quake hotkey dynamic profile"""
        print("⚙️ Installing iTerm2 'Quake' dynamic profile...")

        # Keep the component self-sufficient when Brew Bundle wasn't selected
        if not Path('/Applications/iTerm.app').exists():
            print("📦 iTerm2 not found — installing cask...")
            if not self.run_command('brew install --cask iterm2'):
                self.add_failure("iTerm2 installation failed")
                return False

        source_profile = Path(__file__).parent / 'iterm_profiles' / 'Quake.json'
        if not source_profile.exists():
            self.add_failure("iterm_profiles/Quake.json not found")
            return False

        try:
            with open(source_profile) as f:
                profile = json.load(f)

            dynamic_dir = Path.home() / 'Library' / 'Application Support' / 'iTerm2' / 'DynamicProfiles'
            dynamic_dir.mkdir(parents=True, exist_ok=True)

            # Dynamic profiles must be wrapped in a {"Profiles": [...]} envelope
            with open(dynamic_dir / 'Quake.json', 'w') as f:
                json.dump({"Profiles": [profile]}, f, indent=2)

            self.add_success("iTerm2 Quake profile installed (DynamicProfiles)")
            print("💡 Assign the hotkey under iTerm2 ▸ Settings ▸ Profiles ▸ Quake ▸ Keys if not active")
            return True
        except Exception as e:
            self.add_failure(f"iTerm2 profile installation failed: {e}")
            return False
    
    # NOTE!
    # With the release of macOS Catalina in 2019, Apple officially changed the default login shell and interactive shell from Bash to Zsh (Z shell)
    # However, I'm leaving this in since it would make it easier to broaden the scope of this project to more than just MacOS
    def install_zsh(self):
        """Ensure ZSH is installed and set as default shell"""
        print("📦 Checking ZSH installation...")
        
        # ZSH should already be default on macOS 15+
        if '/bin/zsh' in os.environ.get('SHELL', ''):
            self.add_success("ZSH already default shell")
            return True
        
        # Install zsh if not present and set as default
        result = self.run_command('brew install zsh')
        if result:
            # Set as default shell
            chsh_result = self.run_command('chsh -s /bin/zsh', capture_output=False)
            if chsh_result:
                self.add_success("ZSH installed and set as default shell")
            else:
                self.add_success("ZSH installed (manual shell change required)")
            return True
        else:
            self.add_failure("ZSH installation failed")
            return False
    
    def install_claude_code(self):
        """Install Claude Code (native installer, matching the audited machine)"""
        print("📦 Installing Claude Code...")

        if shutil.which('claude') or (Path.home() / '.local' / 'bin' / 'claude').exists():
            self.add_success("Claude Code already installed")
            return True

        # Official native installer (installs to ~/.local/bin/claude, self-updates).
        # pipefail so a failed curl can't read as success, then verify the binary.
        result = self.run_command(
            "bash -o pipefail -c 'curl -fsSL https://claude.ai/install.sh | bash'",
            shell=True, capture_output=False, check=False)
        if (result and result.returncode == 0
                and (shutil.which('claude') or (Path.home() / '.local' / 'bin' / 'claude').exists())):
            self.add_success("Claude Code installed via official installer")
            return True

        # Homebrew cask as fallback
        print("📦 Trying Homebrew cask fallback...")
        result = self.run_command('brew install --cask claude-code')
        if result:
            self.add_success("Claude Code installed via Homebrew")
            return True

        self.add_failure("Claude Code installation failed")
        return False
    
    def install_vscode(self):
        """Install Visual Studio Code and ensure code command is available"""
        vscode_app_path = Path("/Applications/Visual Studio Code.app")
        vscode_installed = False
        
        # Check if VS Code is already installed
        if vscode_app_path.exists():
            print("📦 VS Code already installed")
            self.add_success("VS Code already installed")
            vscode_installed = True
        else:
            print("📦 Installing Visual Studio Code...")
            result = self.run_command('brew install --cask visual-studio-code')
            if result:
                self.add_success("VS Code installed")
                vscode_installed = True
            else:
                self.add_failure("VS Code installation failed")
                return False
        
        # Ensure 'code' command is available
        if vscode_installed:
            return self.setup_vscode_cli()
        
        return False
    
    def setup_vscode_cli(self):
        """Set up the VS Code 'code' command in PATH"""
        print("⚙️ Setting up VS Code 'code' command...")
        
        # Check if code command already exists
        if shutil.which('code'):
            self.add_success("'code' command already available")
            return True
        
        # Try to create symlink in /usr/local/bin (requires sudo)
        vscode_bin = "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"
        
        if not os.path.exists(vscode_bin):
            self.add_failure("VS Code binary not found")
            return False
        
        # Try multiple approaches for setting up the code command
        approaches = [
            # Approach 1: Try /usr/local/bin symlink
            ('Creating symlink in /usr/local/bin', 
             f'sudo ln -sf "{vscode_bin}" /usr/local/bin/code'),
            
            # Approach 2: Try homebrew's bin directory
            ('Creating symlink in homebrew bin', 
             f'ln -sf "{vscode_bin}" /opt/homebrew/bin/code'),
            
            # Approach 3: Add to shell profile
            ('Adding to PATH in shell profile', None)  # Special case
        ]
        
        for approach_name, command in approaches:
            try:
                if command:
                    result = self.run_command(command, shell=True, capture_output=False)
                    if result and shutil.which('code'):
                        self.add_success(f"'code' command set up via {approach_name.lower()}")
                        return True
                else:
                    # Special case: add to shell profile
                    self.add_to_shell_profile(f'export PATH="$PATH:{os.path.dirname(vscode_bin)}"')
                    print("Added VS Code to PATH in shell profile (restart terminal to use 'code' command)")
                    # For current session, add to PATH
                    os.environ['PATH'] = f"{os.environ['PATH']}:{os.path.dirname(vscode_bin)}"
                    self.add_success("'code' command added to PATH")
                    return True
            except Exception as e:
                print(f"Approach '{approach_name}' failed: {e}")
                continue
        
        self.add_failure("Could not set up 'code' command")
        return False
    
    def add_to_shell_profile(self, line):
        """Add a line to the shell profile if it doesn't exist"""
        try:
            existing_content = ""
            if self.shell_profile.exists():
                with open(self.shell_profile, 'r') as f:
                    existing_content = f.read()
            
            if line not in existing_content:
                with open(self.shell_profile, 'a') as f:
                    f.write(f'\n{line}\n')
                return True
        except Exception as e:
            print(f"Warning: Could not update shell profile: {e}")
        return False
    
    def setup_kill_apple_media_tracking(self):
        """Setup script to kill Apple media tracking processes"""
        print("⚙️ Setting up Apple media tracking killer script...")
        
        try:
            # Source and destination paths
            source_script = Path(__file__).parent / 'background_scripts' / 'killapplemediatracking.sh'
            dest_dir = Path.home() / 'background_scripts'
            dest_script = dest_dir / 'killapplemediatracking.sh'
            launch_agents_dir = Path.home() / 'Library' / 'LaunchAgents'
            plist_file = launch_agents_dir / 'com.user.killapplemediatracking.plist'
            
            # Check if source script exists
            if not source_script.exists():
                self.add_failure("killapplemediatracking.sh not found in background_scripts directory")
                return False
            
            # Create destination directory if it doesn't exist
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy the script to user's background_scripts directory
            shutil.copy2(source_script, dest_script)
            # Make it executable
            os.chmod(dest_script, 0o755)
            print(f"Copied script to {dest_script}")
            
            # Create LaunchAgents directory if it doesn't exist
            launch_agents_dir.mkdir(parents=True, exist_ok=True)
            
            # Create the LaunchAgent plist file
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.killapplemediatracking</string>
    <key>ProgramArguments</key>
    <array>
        <string>{dest_script}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/killapplemediatracking.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/killapplemediatracking.error.log</string>
</dict>
</plist>"""
            
            # Write the plist file
            with open(plist_file, 'w') as f:
                f.write(plist_content)
            
            print(f"Created LaunchAgent at {plist_file}")
            
            # Load the LaunchAgent
            if self.load_launch_agent(plist_file, 'com.user.killapplemediatracking'):
                self.add_success("Apple media tracking killer script installed and started")
                print("The script will run continuously in the background and restart on login")
                return True
            else:
                self.add_success("Apple media tracking killer script installed (will start on next login)")
                print("Note: Run 'launchctl load ~/Library/LaunchAgents/com.user.killapplemediatracking.plist' to start now")
                return True
                
        except Exception as e:
            self.add_failure(f"Failed to setup Apple media tracking killer: {e}")
            return False
    
    def setup_download_recycler(self):
        """Setup script to automatically clean old downloads"""
        print("⚙️ Setting up Download Recycler script...")
        
        try:
            # Source and destination paths
            source_script = Path(__file__).parent / 'background_scripts' / 'download_recycler.sh'
            dest_dir = Path.home() / 'background_scripts'
            dest_script = dest_dir / 'download_recycler.sh'
            config_file = dest_dir / 'download_recycler.conf'
            launch_agents_dir = Path.home() / 'Library' / 'LaunchAgents'
            plist_file = launch_agents_dir / 'com.user.downloadrecycler.plist'
            
            # Check if source script exists
            if not source_script.exists():
                self.add_failure("download_recycler.sh not found in background_scripts directory")
                return False
            
            # Create destination directory if it doesn't exist
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy the script to user's background_scripts directory
            shutil.copy2(source_script, dest_script)
            # Make it executable
            os.chmod(dest_script, 0o755)
            print(f"Copied script to {dest_script}")
            
            # Create or update config file
            if not config_file.exists():
                days_to_keep = 30
                if not self.no_confirm:
                    # Ask user for the number of days
                    print("\n" + "="*50)
                    print("Download Recycler Configuration")
                    print("="*50)
                    print("Files in your Downloads folder older than the specified")
                    print("number of days will be automatically moved to Trash.")
                    print("(You can change this later by editing ~/background_scripts/download_recycler.conf)")
                    print()

                    while True:
                        try:
                            days_input = input("Enter number of days to keep downloads (default: 30): ").strip()
                            if days_input == "":
                                days_to_keep = 30
                                break
                            days_to_keep = int(days_input)
                            if days_to_keep < 1:
                                print("Please enter a positive number.")
                                continue
                            break
                        except ValueError:
                            print("Please enter a valid number.")
                            continue
                
                # Write config file
                config_content = f"""# Download Recycler Configuration
# Files in Downloads folder older than this many days will be moved to Trash
DAYS_TO_KEEP={days_to_keep}

# To change this value, simply edit the number above and save the file.
# The change will take effect on the next scheduled run.
"""
                with open(config_file, 'w') as f:
                    f.write(config_content)
                print(f"Created config file with {days_to_keep} days retention period")
            else:
                print(f"Config file already exists at {config_file}")
            
            # Create LaunchAgents directory if it doesn't exist
            launch_agents_dir.mkdir(parents=True, exist_ok=True)
            
            # Create the LaunchAgent plist file for daily execution
            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.downloadrecycler</string>
    <key>ProgramArguments</key>
    <array>
        <string>{dest_script}</string>
    </array>
    <key>RunAtLoad</key>
    <false/>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{dest_dir}/download_recycler.out</string>
    <key>StandardErrorPath</key>
    <string>{dest_dir}/download_recycler.err</string>
</dict>
</plist>"""
            
            # Write the plist file
            with open(plist_file, 'w') as f:
                f.write(plist_content)
            
            print(f"Created LaunchAgent at {plist_file}")
            
            # Load the LaunchAgent
            if self.load_launch_agent(plist_file, 'com.user.downloadrecycler'):
                self.add_success("Download Recycler installed and scheduled (runs daily at 9:00 AM)")
                print(f"Log file: ~/background_scripts/download_recycler.log")
                print(f"Config file: ~/background_scripts/download_recycler.conf")
                return True
            else:
                self.add_success("Download Recycler installed (will start on next login)")
                print("Note: Run 'launchctl load ~/Library/LaunchAgents/com.user.downloadrecycler.plist' to start now")
                print(f"Log file: ~/background_scripts/download_recycler.log")
                print(f"Config file: ~/background_scripts/download_recycler.conf")
                return True
                
        except Exception as e:
            self.add_failure(f"Failed to setup Download Recycler: {e}")
            return False
    
    def configure_vscode_extensions(self):
        """Configure VS Code extensions"""
        print("⚙️ Configuring VS Code extensions...")
        
        # Verify code command is available
        if not shutil.which('code'):
            print("❌ 'code' command not found. Cannot configure extensions.")
            print("💡 You may need to restart your terminal or manually install extensions.")
            self.add_failure("VS Code extensions (code command not available)")
            return False
        
        # Extension list captured from the audited machine (vscode/extensions.txt)
        extensions_file = Path(__file__).parent / 'vscode' / 'extensions.txt'
        if not extensions_file.exists():
            self.add_failure("vscode/extensions.txt not found")
            return False

        desired_extensions = [line.strip() for line in extensions_file.read_text().splitlines()
                              if line.strip() and not line.startswith('#')]

        list_result = self.run_command('code --list-extensions')
        already_installed = set(list_result.stdout.split()) if list_result else set()

        installed, failed = 0, []
        print(f"📦 Installing {len(desired_extensions)} extensions from vscode/extensions.txt...")
        for ext_id in desired_extensions:
            if ext_id in already_installed:
                installed += 1
                continue
            result = self.run_command(f'code --install-extension {ext_id}', check=False)
            if result and result.returncode == 0:
                installed += 1
            else:
                failed.append(ext_id)

        if installed:
            self.add_success(f"VS Code extensions: {installed}/{len(desired_extensions)} installed")
        if failed:
            self.add_failure(f"VS Code extensions failed: {', '.join(failed)}")
            print("💡 You can manually install failed extensions from VS Code's Extensions panel")

        return len(failed) == 0

    def install_github_cli(self):
        """Install GitHub CLI and configure git identity, LFS, and credential helper"""
        print("📦 Installing GitHub CLI...")
        if shutil.which('gh'):
            self.add_success("GitHub CLI already installed")
        elif self.run_command('brew install gh'):
            self.add_success("GitHub CLI installed")
        else:
            self.add_failure("GitHub CLI installation failed")
            return False

        print("⚙️ Configuring git...")
        self.run_command(f'git config --global user.name "{GIT_USER_NAME}"', shell=True, check=False)
        self.run_command(f'git config --global user.email "{GIT_USER_EMAIL}"', shell=True, check=False)
        lfs = self.run_command('git lfs install', check=False)
        self.add_success(f"git configured (user.name={GIT_USER_NAME}, LFS {'enabled' if lfs and lfs.returncode == 0 else 'skipped'})")
        return True
    
    def install_dark_mode_toggle(self):
        """Build and install ThemeToggle - a custom menu bar app for toggling dark mode"""
        print("📦 Building and installing ThemeToggle (Dark Mode Toggle)...")
        
        # Check if already installed
        themetoggle_app = Path("/Applications/ThemeToggle.app")
        if themetoggle_app.exists():
            self.add_success("ThemeToggle already installed")
            return True
        
        # Check if Xcode is installed and properly configured
        if not shutil.which('xcodebuild'):
            print("❌ Xcode is required to build ThemeToggle")
            print("Please install Xcode from the Mac App Store and try again")
            self.add_failure("ThemeToggle installation failed - Xcode not found")
            return False
        
        # Check if xcode-select is pointing to full Xcode
        xcode_path_result = self.run_command('xcode-select -p', shell=True, capture_output=True)
        if xcode_path_result and 'CommandLineTools' in xcode_path_result.stdout:
            print("⚠️  Xcode Command Line Tools detected, but full Xcode is required")
            print("🔧 Attempting to switch to full Xcode installation...")
            
            # Try to find and set Xcode path
            if Path("/Applications/Xcode.app").exists():
                print("Found Xcode at /Applications/Xcode.app")
                print("Switching xcode-select to use full Xcode (may require admin password)...")
                switch_result = self.run_command('sudo xcode-select -s /Applications/Xcode.app/Contents/Developer', shell=True, capture_output=False)
                if not switch_result:
                    print("❌ Failed to switch to Xcode. Please run manually:")
                    print("   sudo xcode-select -s /Applications/Xcode.app/Contents/Developer")
                    self.add_failure("ThemeToggle installation failed - Could not configure Xcode")
                    return False
            else:
                print("❌ Xcode.app not found in /Applications/")
                print("Please install Xcode from the Mac App Store and run:")
                print("   sudo xcode-select -s /Applications/Xcode.app/Contents/Developer")
                self.add_failure("ThemeToggle installation failed - Xcode not properly installed")
                return False
        
        # Get the script directory
        script_dir = Path(__file__).parent
        project_path = script_dir / "mac_light_dark_toggle" / "ThemeToggle"
        
        if not project_path.exists():
            print("❌ ThemeToggle project not found")
            self.add_failure("ThemeToggle installation failed - project not found")
            return False
        
        # Build the app
        print("🔨 Building ThemeToggle app...")
        build_cmd = f'cd "{project_path}" && xcodebuild -project ThemeToggle.xcodeproj -scheme ThemeToggle -configuration Release build CONFIGURATION_BUILD_DIR=./build'
        result = self.run_command(build_cmd, shell=True, capture_output=True)
        
        if not result:
            self.add_failure("ThemeToggle build failed")
            return False
        
        # Check if build was successful
        built_app = project_path / "build" / "ThemeToggle.app"
        if not built_app.exists():
            self.add_failure("ThemeToggle build failed - app not found")
            return False
        
        # Copy to Applications folder
        print("📂 Installing ThemeToggle to Applications folder...")
        try:
            # Remove existing app if present
            if themetoggle_app.exists():
                shutil.rmtree(themetoggle_app)
            
            # Copy the app
            shutil.copytree(built_app, themetoggle_app)
            
            # Make it executable
            self.run_command(f'chmod +x "{themetoggle_app}/Contents/MacOS/ThemeToggle"', shell=True)
            
            self.add_success("ThemeToggle installed successfully")
            print("✨ ThemeToggle will appear in your menu bar after launch")
            print("💡 Click the menu bar icon to toggle between light and dark mode")
            print("\n⚠️  Note: On first launch, macOS will ask for permission to control System Events")
            print("   Please grant this permission for the app to work properly")
            
            # Optionally launch ThemeToggle
            if self.ask_yes_no("\nWould you like to launch ThemeToggle now? (y/n): "):
                self.run_command(f'open "{themetoggle_app}"', shell=True, check=False)
                print("ThemeToggle launched - check your menu bar!")
                print("If prompted, please grant permission to control System Events")

            # Add to login items
            if self.ask_yes_no("\nWould you like ThemeToggle to start automatically at login? (y/n): "):
                # Use osascript to add to login items
                add_login_cmd = f'''osascript -e 'tell application "System Events" to make login item at end with properties {{path:"{themetoggle_app}", hidden:false}}' '''
                self.run_command(add_login_cmd, shell=True, check=False)
                print("ThemeToggle added to login items")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to install ThemeToggle: {e}")
            self.add_failure("ThemeToggle installation failed")
            return False
    
    def setup_github_cli(self):
        """Prompt user to sign into GitHub CLI and wire it as git credential helper"""
        print("🔐 Setting up GitHub CLI authentication...")

        # Already authenticated? Just make sure the credential helper is wired.
        status = self.run_command('gh auth status', check=False)
        if status and status.returncode == 0:
            self.run_command('gh auth setup-git', check=False)
            self.add_success("GitHub CLI already authenticated (credential helper wired)")
            return True

        if self.no_confirm:
            self.add_success("GitHub CLI auth skipped in unattended mode (run 'gh auth login && gh auth setup-git' later)")
            return True

        print("\n" + "="*50)
        print("GitHub CLI Authentication Required")
        print("="*50)
        print("You will now be prompted to authenticate with GitHub.")
        print("This will open a browser window to GitHub's sign-in page.")

        # Open GitHub sign-in page
        print("🌐 Opening GitHub sign-in page in browser...")
        webbrowser.open('https://github.com/login')

        # Prompt user
        input("\nPress Enter when ready to continue with GitHub CLI authentication...")

        # Start GitHub CLI authentication
        print("Starting GitHub CLI authentication...")
        result = self.run_command('gh auth login', capture_output=False)

        if result is not None:
            self.run_command('gh auth setup-git', check=False)
            self.add_success("GitHub CLI authentication completed")
            return True
        else:
            self.add_failure("GitHub CLI authentication failed")
            return False
    
    def install_menu_bar_apps(self):
        """Clone, build, and link the StatusItemKit menu-bar app suite"""
        print("📦 Installing menu-bar app suite (StatusItemKit apps)...")

        code_dir = Path.home() / 'Code'
        code_dir.mkdir(exist_ok=True)
        apps_dir = Path.home() / 'Applications'
        apps_dir.mkdir(exist_ok=True)

        # Frameworks first — the apps reference them as local ../ SPM path deps
        for name, url in FRAMEWORK_REPOS:
            if not self.clone_or_update_repo(url, code_dir / name):
                self.add_failure(f"Menu-bar suite: could not clone {name}")
                return False

        # Stable self-signed identity so TCC grants survive rebuilds.
        # The script asks for the login password (tty prompt or GUI dialog),
        # so it can't run unattended.
        signing_script = code_dir / 'StatusItemKit' / 'scripts' / 'setup-signing.sh'
        if self.no_confirm:
            print("⏭️  Skipping signing identity setup (needs your password). Builds use")
            print(f"    ad-hoc signing; run {signing_script} later, then re-run this component.")
        elif signing_script.exists():
            result = self.run_command(f'bash "{signing_script}"', shell=True,
                                      capture_output=False, check=False)
            if not (result and result.returncode == 0):
                print("⚠️  setup-signing.sh failed; builds fall back to ad-hoc signing "
                      "(TCC grants reset on every rebuild)")

        # Clone + build each app, symlink into ~/Applications
        built, failed = [], []
        for name, url, app_name in MENU_BAR_APP_REPOS:
            repo = code_dir / name
            status = self.clone_or_update_repo(url, repo)
            if not status:
                failed.append(f"{name} (clone)")
                continue
            built_app = repo / 'build' / app_name
            if status == 'unchanged' and built_app.exists():
                # Source didn't move and a build exists — skip the rebuild
                self.run_command(f'ln -sfn "{built_app}" "{apps_dir / app_name}"',
                                 shell=True, check=False)
                built.append(f"{app_name} (up to date)")
                continue
            build_script = repo / 'scripts' / 'build-app.sh'
            if not build_script.exists():
                failed.append(f"{name} (no scripts/build-app.sh)")
                continue
            print(f"🔨 Building {app_name}...")
            result = self.run_command(f'bash "{build_script}"', shell=True,
                                      capture_output=False, check=False)
            if not (result and result.returncode == 0 and built_app.exists()):
                failed.append(f"{name} (build)")
                continue
            self.run_command(f'ln -sfn "{built_app}" "{apps_dir / app_name}"',
                             shell=True, check=False)
            built.append(app_name)

        if built:
            self.add_success(f"Menu-bar apps linked into ~/Applications: {', '.join(built)}")
            print("💡 Launch each app once and grant its permissions (KeyLight needs Accessibility);")
            print("   enable 'Start at Login' from each app's own menu (SMAppService).")
        if failed:
            self.add_failure(f"Menu-bar apps failed: {', '.join(failed)}")
        return not failed

    def install_vpn_dns_agent(self):
        """Install the Mullvad/Tailscale DNS-sync launchd agent from vpn-dns-menubar"""
        print("⚙️ Installing VPN/DNS watcher launchd agent...")

        label = 'com.nicholassmith.mullvad-tailscale-dns'
        repo = Path.home() / 'Code' / 'vpn-dns-menubar'
        if not self.clone_or_update_repo(
                'https://github.com/nicholaspsmith/vpn-dns-menubar.git', repo):
            self.add_failure("VPN/DNS agent: vpn-dns-menubar clone failed")
            return False

        watch_script = repo / 'dns-watcher' / 'mullvad-tailscale-dns-sync.sh'
        template = repo / 'dns-watcher' / f'{label}.plist'
        if not (watch_script.exists() and template.exists()):
            self.add_failure("VPN/DNS agent: dns-watcher files not found in repo")
            return False

        try:
            template_text = template.read_text()
            if '__SCRIPT__' not in template_text:
                # Fail loudly if the upstream template convention drifts
                self.add_failure("VPN/DNS agent: template no longer uses the __SCRIPT__ "
                                 "placeholder — update this component to match vpn-dns-menubar")
                return False
            os.chmod(watch_script, 0o755)
            launch_agents = Path.home() / 'Library' / 'LaunchAgents'
            launch_agents.mkdir(parents=True, exist_ok=True)
            plist_file = launch_agents / f'{label}.plist'
            plist_file.write_text(template_text.replace('__SCRIPT__', str(watch_script)))

            if self.load_launch_agent(plist_file, label):
                self.add_success("VPN/DNS watcher agent loaded (Tailscale accept-dns follows Mullvad)")
            else:
                self.add_success("VPN/DNS watcher agent installed (loads at next login)")
            print("💡 Requires the Mullvad VPN and Tailscale apps (Brewfile) to be signed in")
            return True
        except Exception as e:
            self.add_failure(f"VPN/DNS agent installation failed: {e}")
            return False

    def install_code_catalog(self):
        """Install the ~/Code project catalog watcher (regenerates PROJECTS.md)"""
        print("⚙️ Installing ~/Code project catalog watcher...")

        source_dir = Path(__file__).parent / 'local_bin'
        local_bin = Path.home() / '.local' / 'bin'
        label = 'com.nicholassmith.code-catalog'
        try:
            local_bin.mkdir(parents=True, exist_ok=True)
            for script in ['code-catalog-refresh', 'code-catalog-watch']:
                src = source_dir / script
                if not src.exists():
                    self.add_failure(f"Code catalog: local_bin/{script} missing from repo")
                    return False
                shutil.copy2(src, local_bin / script)
                os.chmod(local_bin / script, 0o755)

            if self.install_launch_agent(label, [local_bin / 'code-catalog-watch'],
                                         'code-catalog.log', extra={'ThrottleInterval': 30}):
                self.add_success("Code catalog watcher loaded (regenerates ~/Code/PROJECTS.md)")
            else:
                self.add_success("Code catalog watcher installed (loads at next login)")
            print("💡 Requires fswatch (Brewfile); `proj`/`list`/`projects` helpers live in .zshrc")
            return True
        except Exception as e:
            self.add_failure(f"Code catalog installation failed: {e}")
            return False

    def setup_mov_watcher(self):
        """Install the Downloads MOV → MP4 auto-converter watcher"""
        print("⚙️ Setting up MOV → MP4 watcher...")

        label = 'com.nicholassmith.mov-watcher'
        source_script = Path(__file__).parent / 'background_scripts' / 'mov_watcher.sh'
        if not source_script.exists():
            self.add_failure("mov_watcher.sh not found in background_scripts directory")
            return False
        try:
            dest_dir = Path.home() / 'background_scripts'
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_script = dest_dir / 'mov_watcher.sh'
            shutil.copy2(source_script, dest_script)
            os.chmod(dest_script, 0o755)

            # ThrottleInterval keeps a missing-fswatch failure from hot-looping
            if self.install_launch_agent(label, [dest_script], 'mov-watcher.log',
                                         extra={'ThrottleInterval': 300}):
                self.add_success("MOV watcher started (converts Downloads/*.mov to .mp4)")
            else:
                self.add_success("MOV watcher installed (starts at next login)")
            print("💡 Requires fswatch and ffmpeg (Brewfile)")
            return True
        except Exception as e:
            self.add_failure(f"MOV watcher installation failed: {e}")
            return False

    def print_summary(self):
        """Print installation summary"""
        print("\n" + "="*60)
        print("🎉 SETUP COMPLETE!")
        print("="*60)
        
        if self.success_items:
            print("\n✅ Successfully installed/configured:")
            for item in self.success_items:
                print(f"   • {item}")
        
        if self.failed_items:
            print("\n❌ Failed items:")
            for item in self.failed_items:
                print(f"   • {item}")
        
        print("\n📋 Next Steps:")
        print("1. Restart your terminal to ensure all PATH changes take effect")
        print("2. Open iTerm2 and assign the Quake profile hotkey (Settings ▸ Profiles ▸ Quake ▸ Keys)")
        print("3. Launch each menu-bar app once, grant permissions, enable Start at Login in its menu")
        print("4. Sign in: gh auth login, Tailscale, Mullvad VPN")
        print("5. Run 'claude' in your project directory to start Claude Code")

        print("\n🔧 Manual Configuration Required (macOS won't let us automate these):")
        print("• TCC permissions: Accessibility for KeyLight, Screen Recording for MacRecorder,")
        print("  System Events for ThemeToggle — grant when each app first asks")
        print("• Ice: arrange which menu-bar icons stay visible (hide native Mullvad/Tailscale)")
        print("• SSH keys + ~/.ssh/config (e.g. the 'dino' host) — restore from backup")
        print("• App Store apps (full Xcode is only needed for ThemeToggle)")
        if not shutil.which('code'):
            print("• VS Code: If 'code' command not working, restart terminal or run:")
            print("  sudo ln -sf '/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code' /usr/local/bin/code")

        print("\n📚 Useful Commands:")
        print("• claude --help          - Claude Code help")
        print("• code .                 - Open current directory in VS Code")
        print("• gh auth status         - Check GitHub CLI status")
        print("• nvm list               - List installed Node.js versions")
        print("• proj                   - Fuzzy-pick a ~/Code project (after new shell)")
        print("• launchctl list | grep nicholassmith - Check custom launchd agents")
        print("• brew bundle --file=Brewfile - Re-run/repair package installs")
    
    def get_installation_steps(self):
        """Get all available installation steps"""
        return [
            ("Homebrew", "Package manager for macOS", self.install_homebrew),
            ("Brew Bundle", "Curated Brewfile: CLI tools, casks, fonts", self.install_brew_bundle),
            ("ZSH Shell", "Z Shell (should already be default)", self.install_zsh),
            ("Oh My Zsh", "ZSH framework for terminal customization", self.install_oh_my_zsh),
            ("Copy .zshrc config", "Custom ZSH configuration + fzf-git.sh", self.copy_zshrc),
            ("NVM & Node.js LTS", "Node Version Manager (Homebrew) and Node.js", self.install_nvm),
            ("iTerm2 Quake profile", "Hotkey dropdown profile via DynamicProfiles", self.install_iterm_profile),
            ("Claude Code", "Claude AI coding assistant (native installer)", self.install_claude_code),
            ("VS Code", "Visual Studio Code editor", self.install_vscode),
            ("VS Code Extensions", "Extension set captured from this machine", self.configure_vscode_extensions),
            ("GitHub CLI & git config", "gh, git identity, git-lfs", self.install_github_cli),
            ("GitHub Authentication", "Sign in to GitHub CLI (interactive)", self.setup_github_cli),
            ("Menu-bar app suite", "ProcessMonitor, VPN & DNS, Battery Time, KeyLight, MacRecorder", self.install_menu_bar_apps),
            ("VPN/DNS watcher agent", "Tailscale accept-dns follows Mullvad state", self.install_vpn_dns_agent),
            ("Code catalog", "~/Code PROJECTS.md watcher + proj/list helpers", self.install_code_catalog),
            ("MOV Watcher", "Auto-convert Downloads/*.mov to .mp4", self.setup_mov_watcher),
            ("Dark Mode Toggle", "ThemeToggle menu bar app (requires full Xcode)", self.install_dark_mode_toggle),
            ("Apple Media Tracking Killer", "Legacy: background process to disable media tracking", self.setup_kill_apple_media_tracking),
            ("Download Recycler", "Legacy: auto-clean old files from Downloads folder", self.setup_download_recycler),
        ]
    
    def display_checkbox_menu(self):
        """Display an interactive checkbox menu for selecting installation steps"""
        # Check if we're in an interactive terminal
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            print("Non-interactive environment detected, using simple menu...")
            return self.display_simple_menu()
        
        steps = self.get_installation_steps()
        selected = [True] * len(steps)  # Default all selected
        
        def draw_menu(stdscr, current_pos=0):
            curses.curs_set(0)  # Hide cursor
            stdscr.clear()
            height, width = stdscr.getmaxyx()
            
            # Title
            title = "🚀 macOS Development Environment Setup"
            subtitle = "Use arrow keys to navigate, SPACE to toggle, ENTER to proceed, Q to quit"
            
            try:
                stdscr.addstr(0, 0, title[:width-1], curses.A_BOLD)
                stdscr.addstr(1, 0, "="*min(50, width-1))
                stdscr.addstr(2, 0, subtitle[:width-1])
                stdscr.addstr(3, 0, "-"*min(50, width-1))
                
                # Menu items
                for idx, (name, description, _) in enumerate(steps):
                    y = idx + 5
                    if y >= height - 2:
                        break
                        
                    checkbox = "[✓]" if selected[idx] else "[ ]"
                    line = f"{checkbox} {name}"
                    
                    if idx == current_pos:
                        stdscr.addstr(y, 0, line[:width-1], curses.A_REVERSE)
                        # Show description on the line below when selected
                        if y + 1 < height - 2:
                            desc_line = f"    → {description}"
                            stdscr.addstr(y + 1, 0, desc_line[:width-1], curses.A_DIM)
                    else:
                        stdscr.addstr(y, 0, line[:width-1])
                
                # Footer
                footer_y = min(len(steps) + 7, height - 2)
                stdscr.addstr(footer_y, 0, "-"*min(50, width-1))
                footer_text = "Commands: ↑↓ Navigate | SPACE Toggle | A Select All | N Select None | ENTER Run | Q Quit"
                stdscr.addstr(footer_y + 1, 0, footer_text[:width-1])
            except curses.error:
                pass  # Ignore curses errors for small terminals
            
            stdscr.refresh()
        
        def curses_menu(stdscr):
            nonlocal selected
            current = 0
            
            while True:
                draw_menu(stdscr, current)
                key = stdscr.getch()
                
                if key == curses.KEY_UP and current > 0:
                    current -= 1
                elif key == curses.KEY_DOWN and current < len(steps) - 1:
                    current += 1
                elif key == ord(' '):  # Space to toggle
                    selected[current] = not selected[current]
                elif key == ord('a') or key == ord('A'):  # Select all
                    selected = [True] * len(steps)
                elif key == ord('n') or key == ord('N'):  # Select none
                    selected = [False] * len(steps)
                elif key == ord('\n') or key == ord('\r'):  # Enter to proceed
                    return True
                elif key == ord('q') or key == ord('Q'):  # Q to quit
                    return False
        
        # Use curses wrapper for the menu
        try:
            proceed = curses.wrapper(curses_menu)
        except Exception:
            # Fallback to simple text menu if curses fails
            return self.display_simple_menu()
        
        if not proceed:
            return None
        
        # Return selected steps
        selected_steps = [(name, func) for (name, _, func), is_selected in zip(steps, selected) if is_selected]
        return selected_steps
    
    def display_simple_menu(self):
        """Fallback simple text-based menu"""
        print("\n🚀 macOS Development Environment Setup")
        print("="*50)
        print("\nSelect which components to install:")
        print("Enter the numbers separated by commas (e.g., 1,3,5)")
        print("Or type: 'all' for everything, 'none' for interactive selection only, 'q' to quit\n")
        
        steps = self.get_installation_steps()
        for idx, (name, description, _) in enumerate(steps, 1):
            print(f"{idx:2}. {name}")
            print(f"    → {description}")
        
        while True:
            try:
                print("\nYour selection: ", end="", flush=True)
                selection = input().strip().lower()
                
                if selection == 'q':
                    return None
                elif selection == 'all' or selection == '':
                    return [(name, func) for name, _, func in steps]
                elif selection == 'none':
                    return []
                else:
                    indices = [int(x.strip()) - 1 for x in selection.split(',') if x.strip()]
                    selected_steps = []
                    invalid_indices = []
                    
                    for idx in indices:
                        if 0 <= idx < len(steps):
                            name, _, func = steps[idx]
                            selected_steps.append((name, func))
                        else:
                            invalid_indices.append(idx + 1)
                    
                    if invalid_indices:
                        print(f"\n⚠️  Invalid selection(s): {', '.join(map(str, invalid_indices))}")
                        print("Please enter valid numbers between 1 and", len(steps))
                        continue
                    
                    if selected_steps:
                        return selected_steps
                    else:
                        print("\n⚠️  No valid selections made. Please try again.")
                        continue
                        
            except ValueError:
                print("\n⚠️  Invalid input. Please enter numbers separated by commas, 'all', 'none', or 'q'.")
                continue
            except KeyboardInterrupt:
                print("\n\nSetup cancelled.")
                return None
            except EOFError:
                print("\n\nNo input received. Using default (all components).")
                return [(name, func) for name, _, func in steps]
    
    def setup_all(self):
        """Legacy method for backwards compatibility"""
        # This method is kept for backwards compatibility
        # The main logic has been moved to main() function
        selected_steps = self.display_checkbox_menu()
        
        if selected_steps is None:
            print("\nSetup cancelled.")
            return False
        
        if not selected_steps:
            print("\nNo components selected for installation.")
            return False
        
        # Display what will be installed
        print("\n🚀 macOS Development Environment Setup")
        print("="*50)
        print("\nThe following components will be installed:")
        for name, _ in selected_steps:
            print(f"  • {name}")
        
        # Confirm with user
        confirm = input("\nProceed with installation? (y/n): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("Setup cancelled.")
            return False
        
        # Check compatibility
        if not self.check_macos_compatibility():
            return False
        
        print(f"\n🔧 Starting setup process...")
        
        # Run selected installation steps
        for step_name, step_func in selected_steps:
            print(f"\n🔄 Installing {step_name}...")
            try:
                step_func()
            except Exception as e:
                print(f"❌ Error in {step_name}: {e}")
                self.add_failure(f"{step_name} (error: {e})")
        
        # Print summary
        self.print_summary()
        
        return len(self.failed_items) == 0

def main():
    parser = argparse.ArgumentParser(
        description='macOS Development Environment Setup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 setup_macos_dev.py              # Interactive mode (default)
  python3 setup_macos_dev.py --all        # Install everything
  python3 setup_macos_dev.py --list       # List all available components
  python3 setup_macos_dev.py --select 1,3,5  # Install specific components
        """)
    
    parser.add_argument('--all', '-a', action='store_true',
                        help='Install all components without interactive menu')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List all available components and exit')
    parser.add_argument('--select', '-s', type=str,
                        help='Select specific components by number (e.g., "1,3,5")')
    parser.add_argument('--no-confirm', action='store_true',
                        help='Skip confirmation prompt')
    
    args = parser.parse_args()
    setup = MacOSDevSetup(no_confirm=args.no_confirm)
    
    # Handle --list option
    if args.list:
        print("\n🚀 Available Installation Components:")
        print("="*50)
        steps = setup.get_installation_steps()
        for idx, (name, description, _) in enumerate(steps, 1):
            print(f"{idx:2}. {name}")
            print(f"    → {description}")
        print()
        return
    
    # Handle --all option
    if args.all:
        steps = setup.get_installation_steps()
        selected_steps = [(name, func) for name, _, func in steps]
    # Handle --select option
    elif args.select:
        try:
            steps = setup.get_installation_steps()
            indices = [int(x.strip()) - 1 for x in args.select.split(',')]
            selected_steps = []
            for idx in indices:
                if 0 <= idx < len(steps):
                    name, _, func = steps[idx]
                    selected_steps.append((name, func))
                else:
                    print(f"❌ Invalid component number: {idx + 1}")
                    sys.exit(1)
        except ValueError:
            print("❌ Invalid selection format. Use numbers separated by commas (e.g., 1,3,5)")
            sys.exit(1)
    # Interactive mode (default)
    else:
        selected_steps = setup.display_checkbox_menu()
        if selected_steps is None:
            print("\nSetup cancelled.")
            return
    
    if not selected_steps:
        print("\nNo components selected for installation.")
        return
    
    # Display what will be installed
    print("\n🚀 macOS Development Environment Setup")
    print("="*50)
    print("\nThe following components will be installed:")
    for name, _ in selected_steps:
        print(f"  • {name}")
    
    # Confirm with user (unless --no-confirm is used)
    if not args.no_confirm:
        confirm = input("\nProceed with installation? (y/n): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("Setup cancelled.")
            return
    
    # Check compatibility
    if not setup.check_macos_compatibility():
        sys.exit(1)
    
    print(f"\n🔧 Starting setup process...")
    
    # Run selected installation steps
    for step_name, step_func in selected_steps:
        print(f"\n🔄 Installing {step_name}...")
        try:
            step_func()
        except Exception as e:
            print(f"❌ Error in {step_name}: {e}")
            setup.add_failure(f"{step_name} (error: {e})")
    
    # Print summary
    setup.print_summary()
    
    success = len(setup.failed_items) == 0
    if not success:
        print(f"\n⚠️  Setup completed with {len(setup.failed_items)} issues.")
        print("Check the summary above for details.")
        sys.exit(1)
    else:
        print("\n🎉 Setup completed successfully!")

if __name__ == "__main__":
    main()
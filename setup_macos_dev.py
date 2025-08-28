#!/usr/bin/env python3
"""
Complete macOS Development Environment Setup
Automatically installs and configures a full development environment on macOS 15+
"""

import subprocess
import sys
import os
import platform
import shutil
import json
import webbrowser
import time
import plistlib
from pathlib import Path

class MacOSDevSetup:
    def __init__(self):
        self.system = platform.system()
        self.macos_version = None
        if self.system == "Darwin":
            self.macos_version = platform.mac_ver()[0]
        
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
    
    def install_python_via_homebrew(self):
        """Install Python via Homebrew and set up alias"""
        print("📦 Installing Python via Homebrew...")
        
        result = self.run_command('brew install python')
        if not result:
            self.add_failure("Python installation failed")
            return False
        
        # Add python alias to shell profile
        try:
            alias_line = 'alias python="python3"\n'
            with open(self.shell_profile, 'a') as f:
                # Check if alias already exists
                existing_content = ""
                if self.shell_profile.exists():
                    with open(self.shell_profile, 'r') as rf:
                        existing_content = rf.read()
                
                if 'alias python="python3"' not in existing_content:
                    f.write(alias_line)
            
            self.add_success("Python installed and alias configured")
            return True
        except Exception as e:
            print(f"Warning: Could not set Python alias: {e}")
            self.add_success("Python installed (alias setup failed)")
            return True
    
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
        """Copy .zshrc from local zsh directory to user's home directory"""
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
            return True
            
        except Exception as e:
            self.add_failure(f"Failed to copy .zshrc: {e}")
            return False


    
    def install_nvm(self):
        """Install NVM (Node Version Manager)"""
        print("📦 Installing NVM (Node Version Manager)...")
        
        # Check if NVM is already installed
        nvm_dir = Path.home() / '.nvm'
        if nvm_dir.exists():
            self.add_success("NVM already installed")
            return self.setup_nvm_and_node()
        
        # Install NVM
        install_cmd = 'curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash'
        result = self.run_command(install_cmd, shell=True, capture_output=False)
        
        if result:
            self.add_success("NVM installed")
            return self.setup_nvm_and_node()
        else:
            self.add_failure("NVM installation failed")
            return False
    
    def setup_nvm_and_node(self):
        """Setup NVM environment and install Node.js LTS"""
        print("⚙️ Setting up NVM and installing Node.js LTS...")
        
        try:
            # Add NVM to current session
            nvm_dir = str(Path.home() / '.nvm')
            nvm_script = f'{nvm_dir}/nvm.sh'
            
            if not os.path.exists(nvm_script):
                self.add_failure("NVM script not found after installation")
                return False
            
            # Ensure NVM is added to shell profile (NVM installer should do this, but let's be sure)
            self.ensure_nvm_in_profile(nvm_dir)
            
            # Source NVM and install Node LTS
            setup_commands = [
                f'export NVM_DIR="{nvm_dir}"',
                f'[ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh"',
                'nvm install --lts',
                'nvm use --lts',
                'nvm alias default lts/*'
            ]
            
            combined_cmd = ' && '.join(setup_commands)
            result = self.run_command(combined_cmd, shell=True, capture_output=False)
            
            if result:
                # Verify Node.js is available
                node_check = self.run_command('bash -c "source ~/.nvm/nvm.sh && node --version"', shell=True)
                if node_check:
                    self.add_success(f"Node.js LTS installed via NVM")
                    return True
            
            # If the above failed, try a simpler approach
            print("Trying alternative NVM setup...")
            fallback_cmd = f'bash -c "export NVM_DIR={nvm_dir} && source {nvm_script} && nvm install --lts && nvm use --lts"'
            fallback_result = self.run_command(fallback_cmd, shell=True, capture_output=False)
            
            if fallback_result:
                self.add_success("Node.js LTS installed via NVM (fallback method)")
                return True
            
            self.add_failure("Node.js installation via NVM failed")
            return False
            
        except Exception as e:
            print(f"Error setting up NVM: {e}")
            self.add_failure(f"NVM setup failed: {e}")
            return False
    
    def ensure_nvm_in_profile(self, nvm_dir):
        """Ensure NVM is properly configured in shell profile"""
        nvm_lines = [
            f'export NVM_DIR="{nvm_dir}"',
            '[ -s "$NVM_DIR/nvm.sh" ] && \\. "$NVM_DIR/nvm.sh"  # This loads nvm',
            '[ -s "$NVM_DIR/bash_completion" ] && \\. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion'
        ]
        
        try:
            existing_content = ""
            if self.shell_profile.exists():
                with open(self.shell_profile, 'r') as f:
                    existing_content = f.read()
            
            lines_to_add = []
            for line in nvm_lines:
                if line not in existing_content and 'NVM_DIR' not in existing_content:
                    lines_to_add.append(line)
            
            if lines_to_add:
                with open(self.shell_profile, 'a') as f:
                    f.write('\n# NVM Configuration\n')
                    f.write('\n'.join(lines_to_add))
                    f.write('\n')
                print("Added NVM configuration to shell profile")
                
        except Exception as e:
            print(f"Warning: Could not update shell profile for NVM: {e}")
    
    def install_iterm(self):
        """Install iTerm2 via Homebrew"""
        print("📦 Installing iTerm2...")
        result = self.run_command('brew install --cask iterm2')
        if result:
            self.add_success("iTerm2 installed")
            return True
        else:
            self.add_failure("iTerm2 installation failed")
            return False
    
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
        """Install Claude Code"""
        print("📦 Installing Claude Code...")
        
        # Try Homebrew cask first
        result = self.run_command('brew install --cask claude-code')
        if result:
            self.add_success("Claude Code installed via Homebrew")
            return True
        
        # Try official installer as fallback
        print("📦 Trying official Claude Code installer...")
        result = self.run_command('curl -fsSL https://claude.ai/install.sh | bash', shell=True, capture_output=False)
        if result:
            self.add_success("Claude Code installed via official installer")
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
    
    def configure_vscode_extensions(self):
        """Configure VS Code extensions"""
        print("⚙️ Configuring VS Code extensions...")
        
        # Verify code command is available
        if not shutil.which('code'):
            print("❌ 'code' command not found. Cannot configure extensions.")
            print("💡 You may need to restart your terminal or manually install extensions.")
            self.add_failure("VS Code extensions (code command not available)")
            return False
        
        # Wait a moment for VS Code to be ready
        time.sleep(2)
        
        extensions_success = []
        extensions_failed = []
        
        # Install desired extensions
        desired_extensions = [
            ('anthropic.claude-code', 'Claude Code for VS Code'),
            ('ms-python.python', 'Python extension'),
        ]
        
        print("📦 Installing extensions...")
        for ext_id, ext_name in desired_extensions:
            print(f"Installing {ext_name}...")
            
            # First check if already installed
            list_result = self.run_command('code --list-extensions')
            if list_result and ext_id in list_result.stdout:
                extensions_success.append(f"{ext_name} (already installed)")
                continue
            
            # Try to install
            result = self.run_command(f'code --install-extension {ext_id}')
            if result:
                # Verify installation
                verify_result = self.run_command('code --list-extensions')
                if verify_result and ext_id in verify_result.stdout:
                    extensions_success.append(f"Installed {ext_name}")
                else:
                    extensions_failed.append(f"Installation verification failed for {ext_name}")
            else:
                extensions_failed.append(f"Failed to install {ext_name}")
        
        # Report results
        if extensions_success:
            success_msg = f"VS Code extensions: {', '.join(extensions_success)}"
            self.add_success(success_msg)
        
        if extensions_failed:
            failure_msg = f"Some VS Code extensions failed: {', '.join(extensions_failed)}"
            self.add_failure(failure_msg)
            print("💡 You can manually install failed extensions from VS Code's Extensions panel")
        
        return len(extensions_failed) == 0
    
    def install_github_cli(self):
        """Install GitHub CLI"""
        print("📦 Installing GitHub CLI...")
        result = self.run_command('brew install gh')
        if result:
            self.add_success("GitHub CLI installed")
            return True
        else:
            self.add_failure("GitHub CLI installation failed")
            return False
    
    def setup_github_cli(self):
        """Prompt user to sign into GitHub CLI and open browser"""
        print("🔐 Setting up GitHub CLI authentication...")
        
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
            self.add_success("GitHub CLI authentication completed")
            return True
        else:
            self.add_failure("GitHub CLI authentication failed")
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
        print("2. Open iTerm2 and test the hotkey: Ctrl+Q")
        print("3. Check your new Oh My Zsh-powered terminal!")
        print("4. Open VS Code and configure Claude Code extension")
        print("5. Run 'claude' in your project directory to start Claude Code")
        print("6. Test GitHub CLI with: gh auth status")
        
        print("\n🔧 Manual Configuration Required:")
        print("• iTerm2: Go to Settings > Keys > Hotkey to fine-tune hotkey window")
        print("• VS Code: Configure Claude Code extension with your API key")
        print("• Python: Run 'source ~/.zshrc' to use new shell configuration")
        print("• Oh My Zsh: Customize themes and plugins in ~/.zshrc")
        if not shutil.which('code'):
            print("• VS Code: If 'code' command not working, restart terminal or run:")
            print("  sudo ln -sf '/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code' /usr/local/bin/code")
        
        print("\n📚 Useful Commands:")
        print("• claude --help          - Claude Code help")
        print("• code .                 - Open current directory in VS Code")
        print("• gh status              - Check GitHub CLI status")
        print("• python --version       - Check Python version")
        print("• node --version         - Check Node.js version")
        print("• nvm --version          - Check NVM version")
        print("• nvm list               - List installed Node.js versions")
        print("• nvm install <version>  - Install specific Node.js version")
        print("• nvm use <version>      - Switch to Node.js version")
        print("• code --list-extensions - List installed VS Code extensions")
    
    def setup_all(self):
        """Run the complete setup process"""
        print("🚀 macOS Development Environment Setup")
        print("="*50)
        print("This will install and configure:")
        print("• Homebrew, Python, NVM & Node.js LTS")
        print("• iTerm2 with custom hotkey profile")  
        print("• ZSH shell with Oh My Zsh")
        print("• Claude Code")
        print("• VS Code with extensions")
        print("• GitHub CLI with authentication")
        
        # Confirm with user
        confirm = input("\nProceed with installation? (y/n): ").lower().strip()
        if confirm not in ['y', 'yes']:
            print("Setup cancelled.")
            return False
        
        # Check compatibility
        if not self.check_macos_compatibility():
            return False
        
        print(f"\n🔧 Starting setup process...")
        
        # Run all installation steps
        steps = [
            ("Installing Homebrew", self.install_homebrew),
            ("Installing Python", self.install_python_via_homebrew),
            ("Setting up ZSH", self.install_zsh),
            ("Installing Oh My Zsh", self.install_oh_my_zsh),
            ("Copying zsh config to ~/.zshrc", self.copy_zshrc),
            ("Installing NVM & Node.js", self.install_nvm),
            ("Installing iTerm2", self.install_iterm),
            ("Installing Claude Code", self.install_claude_code),
            ("Installing/Checking VS Code", self.install_vscode),
            ("Configuring VS Code extensions", self.configure_vscode_extensions),
            ("Installing GitHub CLI", self.install_github_cli),
            ("Setting up GitHub authentication", self.setup_github_cli),
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔄 {step_name}...")
            try:
                step_func()
            except Exception as e:
                print(f"❌ Error in {step_name}: {e}")
                self.add_failure(f"{step_name} (error: {e})")
        
        # Print summary
        self.print_summary()
        
        return len(self.failed_items) == 0

def main():
    setup = MacOSDevSetup()
    success = setup.setup_all()
    
    if not success:
        print(f"\n⚠️  Setup completed with {len(setup.failed_items)} issues.")
        print("Check the summary above for details.")
        sys.exit(1)
    else:
        print("\n🎉 Setup completed successfully!")

if __name__ == "__main__":
    main()
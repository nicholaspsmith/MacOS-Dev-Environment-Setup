import Cocoa

@main
class AppDelegate: NSObject, NSApplicationDelegate {
    var statusBarItem: NSStatusItem!
    var menu: NSMenu!
    
    func applicationDidFinishLaunching(_ aNotification: Notification) {
        setupStatusBarItem()
        setupMenu()
        
        NSApp.setActivationPolicy(.accessory)
    }
    
    func setupStatusBarItem() {
        statusBarItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.squareLength)
        
        if let statusBarButton = statusBarItem.button {
            statusBarButton.image = NSImage(systemSymbolName: getCurrentThemeIcon(), 
                                          accessibilityDescription: "Theme Toggle")
            statusBarButton.image?.isTemplate = true
        }
    }
    
    func setupMenu() {
        menu = NSMenu()
        let currentTheme = getCurrentTheme()
        let toggleItem = NSMenuItem(title: "Toggle Theme",
                                  action: #selector(toggleTheme),
                                  keyEquivalent: "")
        toggleItem.target = self
        
        
        let statusItem = NSMenuItem(title: "Theme: \(currentTheme)",
                                  action: nil,
                                  keyEquivalent: "")
        statusItem.isEnabled = false
        
        menu.addItem(statusItem)
        menu.addItem(NSMenuItem.separator())
        menu.addItem(toggleItem)
        menu.addItem(NSMenuItem.separator())
        
        let quitItem = NSMenuItem(title: "Quit", 
                                action: #selector(quit), 
                                keyEquivalent: "q")
        quitItem.target = self
        menu.addItem(quitItem)
        
        statusBarItem.menu = menu
    }
    
    @objc func toggleTheme() {
        let task = Process()
        task.launchPath = "/usr/bin/osascript"
        task.arguments = ["-e", """
            tell application "System Events"
                tell appearance preferences
                    set dark mode to not dark mode
                end tell
            end tell
        """]
        
        let pipe = Pipe()
        task.standardOutput = pipe
        task.standardError = pipe
        
        do {
            try task.run()
            task.waitUntilExit()
            
            if task.terminationStatus == 0 {
                updateMenuAndIcon()
            } else {
                let data = pipe.fileHandleForReading.readDataToEndOfFile()
                if let output = String(data: data, encoding: .utf8) {
                    print("Error toggling theme: \(output)")
                    if output.contains("not authorized") {
                        showPermissionInstructions()
                    }
                }
            }
        } catch {
            print("Failed to execute theme toggle: \(error)")
            showPermissionInstructions()
        }
    }
    
    @objc func quit() {
        NSApplication.shared.terminate(self)
    }
    
    func getCurrentTheme() -> String {
        let task = Process()
        task.launchPath = "/usr/bin/osascript"
        task.arguments = ["-e", """
            tell application "System Events"
                tell appearance preferences
                    return dark mode as boolean
                end tell
            end tell
        """]
        
        let pipe = Pipe()
        task.standardOutput = pipe
        task.standardError = pipe
        
        do {
            try task.run()
            task.waitUntilExit()
            
            if task.terminationStatus == 0 {
                let data = pipe.fileHandleForReading.readDataToEndOfFile()
                if let output = String(data: data, encoding: .utf8)?.trimmingCharacters(in: .whitespacesAndNewlines) {
                    return output == "true" ? "Dark" : "Light"
                }
            }
        } catch {
            print("Failed to get theme: \(error)")
        }
        
        return "Unknown"
    }
    
    func getCurrentThemeIcon() -> String {
        let isDarkMode = getCurrentTheme() == "Dark"
        return isDarkMode ? "moon.fill" : "sun.max.fill"
    }
    
    func updateMenuAndIcon() {
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            if let statusBarButton = self.statusBarItem.button {
                statusBarButton.image = NSImage(systemSymbolName: self.getCurrentThemeIcon(), 
                                              accessibilityDescription: "Theme Toggle")
                statusBarButton.image?.isTemplate = true
            }
            
            if let statusItem = self.menu.items.first {
                let currentTheme = self.getCurrentTheme()
                statusItem.title = "Current: \(currentTheme)"
            }
        }
    }
    
    func showPermissionInstructions() {
        DispatchQueue.main.async {
            NSApp.setActivationPolicy(.regular)
            NSApp.activate(ignoringOtherApps: true)
            
            let alert = NSAlert()
            alert.messageText = "Permission Required"
            alert.informativeText = """
            ThemeToggle needs permission to control System Events.
            
            When you click OK, macOS may ask for permission.
            
            If no dialog appears:
            1. Open System Settings
            2. Go to Privacy & Security → Automation
            3. Find ThemeToggle and enable System Events
            4. Restart the app
            """
            alert.alertStyle = .warning
            alert.addButton(withTitle: "Open System Settings")
            alert.addButton(withTitle: "OK")
            
            let response = alert.runModal()
            
            if response == .alertFirstButtonReturn {
                NSWorkspace.shared.open(URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_Automation")!)
            }
            
            NSApp.setActivationPolicy(.accessory)
        }
    }
}

#!/bin/bash
# nicholaspsmith 2025
# Built for MacOS Sequoia (15.6.*)

# Download Recycler - Automatically move old files from Downloads to Trash
# This script reads the number of days from a config file and moves files
# older than that threshold to the Trash

# Configuration file path
CONFIG_FILE="$HOME/background_scripts/download_recycler.conf"

# Default number of days if config doesn't exist
DEFAULT_DAYS=30

# Read the number of days from config file
if [ -f "$CONFIG_FILE" ]; then
    DAYS=$(grep "^DAYS_TO_KEEP=" "$CONFIG_FILE" | cut -d'=' -f2 | tr -d ' ')
    # Validate that DAYS is a number
    if ! [[ "$DAYS" =~ ^[0-9]+$ ]]; then
        echo "Warning: Invalid value in config file. Using default: $DEFAULT_DAYS days"
        DAYS=$DEFAULT_DAYS
    fi
else
    echo "Config file not found at $CONFIG_FILE. Using default: $DEFAULT_DAYS days"
    DAYS=$DEFAULT_DAYS
fi

# Get current user
CURRENT_USER=$(whoami)

# Downloads directory
DOWNLOADS_DIR="/Users/$CURRENT_USER/Downloads"

# Log file for tracking operations
LOG_FILE="$HOME/background_scripts/download_recycler.log"

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# Start logging
log_message "Starting download recycler (threshold: $DAYS days)"

# Check if Downloads directory exists
if [ ! -d "$DOWNLOADS_DIR" ]; then
    log_message "ERROR: Downloads directory not found: $DOWNLOADS_DIR"
    exit 1
fi

# Count files before operation
FILES_MOVED=0

# Find and move old files to Trash
# Using -mtime +$DAYS to find files modified more than $DAYS days ago
# Using osascript to properly move to Trash (preserves ability to restore)
find "$DOWNLOADS_DIR" -mindepth 1 -maxdepth 1 -mtime +$DAYS -print0 2>/dev/null | while IFS= read -r -d '' file; do
    # Get file basename for logging
    basename_file=$(basename "$file")
    
    # Move to trash using AppleScript (proper macOS way)
    if osascript -e "tell application \"Finder\" to move POSIX file \"$file\" to trash" 2>/dev/null; then
        log_message "Moved to Trash: $basename_file"
        ((FILES_MOVED++))
    else
        log_message "ERROR: Failed to move to Trash: $basename_file"
    fi
done

# Log completion
if [ $FILES_MOVED -eq 0 ]; then
    log_message "No files older than $DAYS days found in Downloads"
else
    log_message "Completed: Moved $FILES_MOVED item(s) to Trash"
fi

# Keep log file size reasonable (keep last 1000 lines)
if [ -f "$LOG_FILE" ]; then
    tail -n 1000 "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
fi

exit 0
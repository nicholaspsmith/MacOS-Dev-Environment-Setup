#!/bin/bash

# Cover both Homebrew prefixes for manual runs (launchd sets PATH via plist)
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

DOWNLOADS_DIR="$HOME/Downloads"
LOG_FILE="$HOME/Library/Logs/mov-converter.log"

mkdir -p "$(dirname "$LOG_FILE")"
touch "$LOG_FILE"

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1" >> "$LOG_FILE"
    echo "$(date '+%Y-%m-%d %H:%M:%S'): $1"
}

convert_mov_file() {
    local file="$1"
    
    if [[ ! -f "$file" ]]; then
        return
    fi
    
    local filename=$(basename "$file")
    local extension="${filename##*.}"
    if [[ "$extension" != "mov" ]] && [[ "$extension" != "MOV" ]]; then
        return
    fi
    
    log_message "Processing: $file"

    # Wait until the file has finished writing (size stable across checks),
    # so a large download/AirDrop isn't transcoded half-written
    local prev_size=-1 size
    size=$(stat -f%z "$file" 2>/dev/null || echo 0)
    while [[ "$size" != "$prev_size" ]]; do
        sleep 2
        prev_size=$size
        size=$(stat -f%z "$file" 2>/dev/null || echo 0)
    done
    if [[ ! -f "$file" ]]; then
        return
    fi

    local dir=$(dirname "$file")
    local basename="${filename%.*}"
    local output="$dir/$basename.mp4"
    
    if [[ -f "$output" ]]; then
        log_message "Skipping $file - MP4 already exists"
        return
    fi
    
    local ffmpeg_path=""
    if command -v ffmpeg > /dev/null; then
        ffmpeg_path=$(command -v ffmpeg)
    elif [[ -f "/opt/homebrew/bin/ffmpeg" ]]; then
        ffmpeg_path="/opt/homebrew/bin/ffmpeg"
    fi
    
    if [[ -z "$ffmpeg_path" ]]; then
        log_message "ERROR: ffmpeg not found"
        return
    fi
    
    log_message "Converting with: $ffmpeg_path"
    
    if "$ffmpeg_path" -i "$file" -c:v libx264 -c:a aac -movflags +faststart "$output" 2>>"$LOG_FILE"; then
        log_message "Conversion successful, moving original to Trash"
        
        # Use osascript to move to Trash (this bypasses permission issues)
        if osascript -e "tell application \"Finder\" to delete POSIX file \"$file\"" 2>/dev/null; then
            log_message "Successfully converted and moved to Trash: $file"
            osascript -e "display notification \"Converted $filename to MP4\" with title \"MOV Converter\""
        else
            log_message "Converted but could not move to Trash: $file"
            osascript -e "display notification \"Converted $filename to MP4 (original still in Downloads)\" with title \"MOV Converter\""
        fi
    else
        log_message "Failed to convert: $file"
        osascript -e "display notification \"Failed to convert $filename\" with title \"MOV Converter Error\""
    fi
}

if ! command -v fswatch > /dev/null; then
    log_message "ERROR: fswatch not found (brew install fswatch) — exiting"
    exit 1
fi

log_message "Starting MOV file watcher for: $DOWNLOADS_DIR"

fswatch -0 -e ".*" -i "\\.mov$" -i "\\.MOV$" "$DOWNLOADS_DIR" | while IFS= read -r -d '' file; do
    log_message "File event detected: $file"
    sleep 1
    convert_mov_file "$file"
done

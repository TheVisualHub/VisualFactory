#!/bin/bash
# A simple workflow to prepare videos for HTML embedding:
# Requires ffmpeg to be accessible from the terminal.
# Created by Gleb Novikov
# (c) The VisualHub 2025

home="$(pwd)"
inputs="$home"/READY

# MAIN CONFIG
REENCODE=false
CLEAN_OLD=true
trim='3'

# advanced options
suffix='okay'

# === CLEAN OLD OUTPUT WITH EXTENSION CHECK ===
if [ "$CLEAN_OLD" = true ]; then
    echo "Removing old visuals, Master!"; sleep 2
    for f in "$home"/*${suffix}.mp4 "$home"/*${suffix}.mov; do
        if [ -e "$f" ]; then
            rm "$f"
            echo "Removed $f"
        fi
    done
else
    echo "Old visuals are still there, Master!"; sleep 2
fi

for f in "$inputs"/*; do
    [ -f "$f" ] || continue

    base="${f%.*}"
    ext="${f##*.}"
    filename="$(basename "$base")"

    # Get video duration in seconds
    duration=$(ffprobe -v error -show_entries format=duration \
        -of default=noprint_wrappers=1:nokey=1 "$f")

    # New duration = total - trim seconds
    new_duration=$(echo "$duration - $trim" | bc)

     # Skip too-short videos
    if (( $(echo "$new_duration <= 0" | bc -l) )); then
        echo "Skipping (too short): $f"
        continue
    fi

    # Define output path
    output="$home/${filename}_${suffix}.${ext}"

    # === CHOOSE CONVERSION MODE ===
    if [ "$REENCODE" = true ]; then
        # Fully re-encode videos for HTML compatibility
        if [ "$ext" = "mp4" ]; then
            ffmpeg -y -i "$f" -t "$new_duration" \
                -c:v libx264 -preset fast -crf 23 -c:a aac -movflags +faststart "$output"
        elif [ "$ext" = "mov" ]; then
            ffmpeg -y -i "$f" -t "$new_duration" \
                -c:v libx264 -preset fast -crf 23 -c:a aac -movflags +faststart "$output"
        fi
    else
        # Perform simple video conversion into mp4 for HTML compatibility
        #ffmpeg -y -i "$f" -t "$new_duration" -c copy -movflags +faststart "$output"
        ffmpeg -y -i "$f" -t "$new_duration" -c:v copy -c:a copy -movflags +faststart "${home}/${filename}_${suffix}.mp4"
    fi
done

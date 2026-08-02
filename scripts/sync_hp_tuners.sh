#!/bin/bash
# One-way synchronization script:
# Syncs from Windows/OneDrive HP Tuners folder to Linux repository HP Tuners folder.

SRC="/mnt/c/Users/ls0775/OneDrive/Documents/HP Tuners/"
DEST="/home/ls0775/source/repos/GMTuning/HP Tuners/"

if [ -d "$SRC" ] && [ -d "$DEST" ]; then
    rsync -av --update "$SRC" "$DEST"
fi

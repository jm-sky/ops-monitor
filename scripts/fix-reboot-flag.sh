#!/usr/bin/env bash
# Removes /var/run/reboot-required if it was mistakenly created as a directory
# by Docker bind-mount (old docker-compose.yml). Safe to run on any server.
set -euo pipefail

TARGET="/var/run/reboot-required"

if [ -d "$TARGET" ]; then
    if [ "$(ls -A "$TARGET")" ]; then
        echo "ERROR: $TARGET is a non-empty directory — not removing." >&2
        exit 1
    fi
    rmdir "$TARGET"
    echo "Removed spurious directory: $TARGET"
elif [ -f "$TARGET" ]; then
    echo "OK: $TARGET is a regular file — nothing to do."
else
    echo "OK: $TARGET does not exist — nothing to do."
fi

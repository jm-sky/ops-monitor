#!/usr/bin/env bash
# Removes /var/run/reboot-required and /var/run/reboot-required.pkgs if they
# were mistakenly created as directories by Docker bind-mount (old
# docker-compose.yml). Safe to run on any server.
set -euo pipefail

fix_target() {
    local target="$1"

    if [ -d "$target" ]; then
        if [ "$(ls -A "$target")" ]; then
            echo "ERROR: $target is a non-empty directory — not removing." >&2
            return 1
        fi
        rmdir "$target"
        echo "Removed spurious directory: $target"
    elif [ -f "$target" ]; then
        echo "OK: $target is a regular file — nothing to do."
    else
        echo "OK: $target does not exist — nothing to do."
    fi
}

status=0
fix_target "/var/run/reboot-required" || status=1
fix_target "/var/run/reboot-required.pkgs" || status=1
exit "$status"

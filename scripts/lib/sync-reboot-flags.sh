#!/usr/bin/env bash
# Copy the host's reboot flags into a dedicated directory that the ops-monitor agent
# container mounts read-only (instead of the whole /var/run). Installed by
# scripts/agent-host-sync-install.sh and run by ops-monitor-reboot-sync.service.
#
# Copies keep their mtime (cp -p): the agent reports it as reboot_detected_at.
# A copy is removed once its original is gone. The .last-sync marker is touched on
# every run so the agent can tell "no reboot needed" from "sync not installed".
#
# Env overrides (used by tests): OPS_AGENT_REBOOT_SRC, OPS_AGENT_REBOOT_DEST.
set -euo pipefail

SRC="${OPS_AGENT_REBOOT_SRC:-/run}"
DEST="${OPS_AGENT_REBOOT_DEST:-/run/ops-monitor-agent/reboot}"
FILES=(reboot-required reboot-required.pkgs)

mkdir -p "$DEST"
chmod 0755 "$DEST"

for name in "${FILES[@]}"; do
    src="$SRC/$name"
    dest="$DEST/$name"
    # Only regular files count: an old Docker bind mount may have left a directory here
    # (see scripts/fix-reboot-flag.sh).
    if [ -f "$src" ] && [ ! -L "$src" ]; then
        tmp=$(mktemp "$DEST/.$name.XXXXXX")
        cp -p "$src" "$tmp"
        chmod 0644 "$tmp"
        mv -f "$tmp" "$dest"
    else
        rm -f "$dest"
    fi
done

touch "$DEST/.last-sync"
chmod 0644 "$DEST/.last-sync"

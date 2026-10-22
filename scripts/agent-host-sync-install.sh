#!/usr/bin/env bash
# Install (or remove) the host-side reboot flag sync for the Dockerized ops-monitor agent.
#
# The hardened agent container no longer mounts the host's /var/run (it exposes
# docker.sock, containerd and D-Bus). Instead this sync copies only
# /run/reboot-required and /run/reboot-required.pkgs into DEST_DIR, which the
# container mounts read-only at /host/reboot.
#
#   - ops-monitor-reboot-sync.path    triggers the sync when a flag file changes
#   - ops-monitor-reboot-sync.timer   re-syncs every 5 min (fallback, catches removals)
#   - tmpfiles.d                      creates DEST_DIR at boot, before Docker starts
#
# DEST_DIR lives on tmpfs (/run), so a reboot clears the copies together with the originals.
#
# Usage (as root, idempotent):
#   sudo bash scripts/agent-host-sync-install.sh             # install / update
#   sudo bash scripts/agent-host-sync-install.sh --uninstall # remove
set -euo pipefail

SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

UNIT_NAME=ops-monitor-reboot-sync
DEST_DIR=/run/ops-monitor-agent/reboot
SYNC_BIN=/usr/local/libexec/ops-monitor-agent/sync-reboot-flags
TMPFILES_CONF=/etc/tmpfiles.d/ops-monitor-agent.conf
UNIT_DIR=/etc/systemd/system

usage() {
    cat <<EOF
Usage: $0 [--uninstall] [--dest DIR]

  --dest DIR    Directory for the flag copies (default: $DEST_DIR).
                Must match the host side of the agent's /host/reboot mount.
  --uninstall   Stop and remove the sync units, tmpfiles config and copies.
EOF
}

ACTION=do_install
while [ $# -gt 0 ]; do
    case "$1" in
        --uninstall) ACTION=do_uninstall ;;
        --dest)
            [ $# -ge 2 ] || { usage >&2; exit 2; }
            DEST_DIR="$2"
            shift
            ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
    esac
    shift
done

case "$DEST_DIR" in
    /*) ;;
    *) echo "ERROR: --dest must be an absolute path" >&2; exit 2 ;;
esac

if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: run as root (sudo bash $0)" >&2
    exit 1
fi

do_uninstall() {
    echo "==> Disabling $UNIT_NAME units"
    systemctl disable --now "$UNIT_NAME.path" "$UNIT_NAME.timer" 2>/dev/null || true
    rm -f "$UNIT_DIR/$UNIT_NAME.service" "$UNIT_DIR/$UNIT_NAME.path" "$UNIT_DIR/$UNIT_NAME.timer"
    systemctl daemon-reload

    echo "==> Removing $SYNC_BIN, $TMPFILES_CONF and $DEST_DIR"
    rm -f "$SYNC_BIN" "$TMPFILES_CONF"
    rmdir "$(dirname "$SYNC_BIN")" 2>/dev/null || true
    # Only the files the sync creates — never rm -rf a user-supplied path.
    rm -f "$DEST_DIR/reboot-required" "$DEST_DIR/reboot-required.pkgs" "$DEST_DIR/.last-sync"
    rmdir "$DEST_DIR" 2>/dev/null || true
    echo "Done. The agent container will log 'host sync not installed' until it is"
    echo "reinstalled or the agent is switched to docker-compose.legacy-varrun.yml."
}

do_install() {
    echo "==> Installing sync script to $SYNC_BIN"
    install -D -m 0755 -o root -g root "$SCRIPTS_DIR/lib/sync-reboot-flags.sh" "$SYNC_BIN"

    echo "==> Writing $TMPFILES_CONF"
    cat > "$TMPFILES_CONF" <<EOF
# ops-monitor agent: directory with copies of the reboot flags (mounted into the agent container)
d $DEST_DIR 0755 root root -
EOF
    systemd-tmpfiles --create "$TMPFILES_CONF"

    echo "==> Writing systemd units ($UNIT_NAME.service/.path/.timer)"
    cat > "$UNIT_DIR/$UNIT_NAME.service" <<EOF
[Unit]
Description=Copy reboot-required flags for the ops-monitor agent container

[Service]
Type=oneshot
Environment=OPS_AGENT_REBOOT_SRC=/run
Environment=OPS_AGENT_REBOOT_DEST=$DEST_DIR
ExecStart=$SYNC_BIN
EOF

    # PathChanged (not PathExists): PathExists re-triggers the oneshot for as long as the
    # file exists and ends in trigger-limit-hit.
    cat > "$UNIT_DIR/$UNIT_NAME.path" <<EOF
[Unit]
Description=Watch reboot-required flags for the ops-monitor agent container

[Path]
PathChanged=/run/reboot-required
PathChanged=/run/reboot-required.pkgs
Unit=$UNIT_NAME.service

[Install]
WantedBy=paths.target
EOF

    cat > "$UNIT_DIR/$UNIT_NAME.timer" <<EOF
[Unit]
Description=Periodic reboot-required flag sync for the ops-monitor agent container

[Timer]
OnBootSec=30s
OnUnitActiveSec=5min
Unit=$UNIT_NAME.service

[Install]
WantedBy=timers.target
EOF

    systemctl daemon-reload
    systemctl enable "$UNIT_NAME.path" "$UNIT_NAME.timer"
    systemctl restart "$UNIT_NAME.path" "$UNIT_NAME.timer"

    echo "==> Running initial sync"
    systemctl start "$UNIT_NAME.service"

    if [ ! -f "$DEST_DIR/.last-sync" ]; then
        echo "ERROR: $DEST_DIR/.last-sync missing after sync — check: journalctl -u $UNIT_NAME.service" >&2
        exit 1
    fi

    echo ""
    echo "Done. Flag copies in $DEST_DIR:"
    ls -la "$DEST_DIR"
    echo ""
    systemctl --no-pager list-timers "$UNIT_NAME.timer" || true
    if [ "$DEST_DIR" != /run/ops-monitor-agent/reboot ]; then
        echo ""
        echo "NOTE: non-default --dest; mount $DEST_DIR at /host/reboot in the agent's compose file."
    fi
}

"$ACTION"

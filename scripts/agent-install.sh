#!/usr/bin/env bash
# Install ops-monitor agent as a systemd service (Debian/Ubuntu).
# Run as root: sudo bash install.sh

set -euo pipefail

INSTALL_DIR=/opt/ops-monitor-agent
SERVICE_USER=ops-agent

echo "==> Creating user $SERVICE_USER"
id "$SERVICE_USER" &>/dev/null || useradd --system --no-create-home --shell /usr/sbin/nologin "$SERVICE_USER"

echo "==> Installing to $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
cp agent.py requirements.txt "$INSTALL_DIR/"
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

echo "==> Creating Python venv"
python3 -m venv "$INSTALL_DIR/venv"
"$INSTALL_DIR/venv/bin/pip" install --no-cache-dir -r "$INSTALL_DIR/requirements.txt"

if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp .env.example "$INSTALL_DIR/.env"
    echo "==> Created $INSTALL_DIR/.env — edit it and set AGENT_TOKEN before starting"
fi
chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.env"
chmod 600 "$INSTALL_DIR/.env"

echo "==> Installing systemd unit"
cat > /etc/systemd/system/ops-monitor-agent.service <<EOF
[Unit]
Description=Ops Monitor Agent
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/venv/bin/python agent.py
EnvironmentFile=$INSTALL_DIR/.env
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ops-monitor-agent
systemctl restart ops-monitor-agent

echo ""
echo "Done. Agent status:"
systemctl status ops-monitor-agent --no-pager

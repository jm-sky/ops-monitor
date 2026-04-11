#!/usr/bin/env bash
# Deploy ops-monitor to production server.
# Run from the project root directory.
set -euo pipefail

DIST_DIR=/var/www/ops-monitor/dist
BACKEND_DIR="$(cd "$(dirname "$0")/backend" && pwd)"

echo "==> Building frontend..."
pnpm install --frozen-lockfile
pnpm build

echo "==> Deploying frontend to $DIST_DIR..."
mkdir -p "$DIST_DIR"
rsync -a --delete dist/ "$DIST_DIR/"

echo "==> Starting/updating backend..."
docker compose -f "$BACKEND_DIR/docker-compose.yml" pull --quiet
docker compose -f "$BACKEND_DIR/docker-compose.yml" up -d --build

echo "==> Running migrations..."
docker exec ops-monitor-app python -m cli db migrate

echo "==> Reloading Caddy..."
caddy reload --config /etc/caddy/Caddyfile 2>/dev/null || systemctl reload caddy

echo ""
echo "Done. https://ops-monitor.dev-made.it"

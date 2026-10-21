#!/usr/bin/env bash
# Build Vue frontend and deploy to /var/www/ops-monitor/dist.
# Called by deploy.sh — can also be run standalone from the project root.
#
# Always runs the pnpm build as the deploy OS user so node_modules/.pnpm-store
# ownership never splits between CI and manual deploys.
# User comes from DEPLOY_USER in .env (fallback: `deploy`); the web server user
# that owns dist/ from DEPLOY_WEB_USER (fallback: `caddy`).
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$PROJECT_DIR/scripts"
DEPLOY_DIR="/var/www/ops-monitor/dist"

# Read a single key from .env without sourcing it (values may contain shell chars).
env_value() {
  local line
  line="$(grep -E "^$1=" "$PROJECT_DIR/.env" 2>/dev/null | tail -n1 || true)"
  line="${line#*=}"
  line="${line%\"}"; line="${line#\"}"
  line="${line%\'}"; line="${line#\'}"
  printf '%s' "$line"
}

DEPLOY_USER="${DEPLOY_USER:-$(env_value DEPLOY_USER)}"
DEPLOY_USER="${DEPLOY_USER:-deploy}"
DEPLOY_WEB_USER="${DEPLOY_WEB_USER:-$(env_value DEPLOY_WEB_USER)}"
DEPLOY_WEB_USER="${DEPLOY_WEB_USER:-caddy}"

echo -e "${GREEN}Building frontend...${NC}"

echo -e "${YELLOW}Installing dependencies and building...${NC}"
if [ "$(whoami)" = "$DEPLOY_USER" ]; then
  "$SCRIPTS_DIR/frontend_pnpm_build.sh"
else
  sudo -u "$DEPLOY_USER" "$SCRIPTS_DIR/frontend_pnpm_build.sh"
fi

echo -e "${YELLOW}Deploying to $DEPLOY_DIR...${NC}"

deploy_frontend() {
  mkdir -p "$DEPLOY_DIR"
  rm -rf "${DEPLOY_DIR:?}"/*
  cp -r dist/* "$DEPLOY_DIR/"
}

if [ -w "$(dirname "$DEPLOY_DIR")" ] || [ -w "$DEPLOY_DIR" ]; then
  deploy_frontend
else
  sudo mkdir -p "$DEPLOY_DIR"
  sudo rm -rf "${DEPLOY_DIR:?}"/*
  sudo cp -r dist/* "$DEPLOY_DIR/"
fi

sudo chown -R "$DEPLOY_WEB_USER:$DEPLOY_USER" "$DEPLOY_DIR"

echo -e "${GREEN}Frontend deployed to $DEPLOY_DIR${NC}"

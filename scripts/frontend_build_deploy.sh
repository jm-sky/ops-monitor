#!/usr/bin/env bash
# Build Vue frontend and deploy to /var/www/ops-monitor/dist.
# Called by deploy.sh — can also be run standalone from the project root.
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOY_DIR="/var/www/ops-monitor/dist"

echo -e "${GREEN}Building frontend...${NC}"

echo -e "${YELLOW}Installing dependencies...${NC}"
cd "$PROJECT_DIR"
pnpm install --frozen-lockfile

echo -e "${YELLOW}Building...${NC}"
rm -rf dist
# Cap Node heap below typical free RAM on this VPS (no swap).
# Run type-check and vite sequentially — `pnpm build` uses run-p and doubles peak RSS (OOM / exit 137).
export NODE_OPTIONS="--max-old-space-size=2048"
pnpm type-check
pnpm build-only

echo -e "${YELLOW}Deploying to $DEPLOY_DIR...${NC}"
sudo mkdir -p "$DEPLOY_DIR"
sudo rm -rf "${DEPLOY_DIR:?}"/*
sudo cp -r dist/* "$DEPLOY_DIR/"
sudo chown -R caddy:deploy "$DEPLOY_DIR"

echo -e "${GREEN}Frontend deployed to $DEPLOY_DIR${NC}"

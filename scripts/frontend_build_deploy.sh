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

echo -e "${YELLOW}Step 1: Installing dependencies...${NC}"
cd "$PROJECT_DIR"
pnpm install --frozen-lockfile

echo -e "${YELLOW}Step 2: Building...${NC}"
rm -rf dist
export NODE_OPTIONS="--max-old-space-size=4096"
pnpm build

echo -e "${YELLOW}Step 3: Deploying to $DEPLOY_DIR...${NC}"
sudo mkdir -p "$DEPLOY_DIR"
sudo rm -rf "${DEPLOY_DIR:?}"/*
sudo cp -r dist/* "$DEPLOY_DIR/"
sudo chown -R caddy:deploy "$DEPLOY_DIR"

echo -e "${GREEN}Frontend deployed to $DEPLOY_DIR${NC}"

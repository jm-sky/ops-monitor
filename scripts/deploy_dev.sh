#!/usr/bin/env bash
# Deploy ops-monitor using the dev-flavored backend (backend/docker-compose.dev.yml —
# bind-mounted source, Dockerfile.dev with --reload). For the prod-flavored backend
# (root docker-compose.yml, baked image, no reload), use deploy.sh instead.
# Run from the project root: bash scripts/deploy_dev.sh
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCRIPTS_DIR="$PROJECT_DIR/scripts"

echo -e "${GREEN}Starting ops-monitor deployment...${NC}"

echo -e "${YELLOW}Requesting sudo access...${NC}"
sudo -v
while true; do sudo -n true; sleep 60; kill -0 "$$" || exit; done 2>/dev/null &

echo -e "${YELLOW}Step 1: Pulling latest changes...${NC}"
cd "$PROJECT_DIR"
git pull

echo -e "${YELLOW}Step 2: Building and deploying frontend...${NC}"
"$SCRIPTS_DIR/frontend_build_deploy.sh"

echo -e "${YELLOW}Step 3: Restarting backend and running migrations...${NC}"
"$SCRIPTS_DIR/backend_restart_migrate_dev.sh"

echo ""
echo -e "${GREEN}Deployment complete. https://ops-monitor.dev-made.it${NC}"

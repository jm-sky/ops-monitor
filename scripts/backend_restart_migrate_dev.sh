#!/usr/bin/env bash
# Rebuild and restart the dev-flavored ops-monitor backend (backend/docker-compose.dev.yml),
# then run migrations. Called by deploy_dev.sh — can also be run standalone from the project root.
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
COMPOSE_FILE="docker-compose.dev.yml"

echo -e "${GREEN}Restarting backend...${NC}"

cd "$BACKEND_DIR"

echo -e "${YELLOW}Step 1: Building app image...${NC}"
docker compose -f "$COMPOSE_FILE" build app

echo -e "${YELLOW}Step 2: Recreating app container...${NC}"
docker compose -f "$COMPOSE_FILE" up -d --force-recreate app

echo -e "${YELLOW}Step 3: Waiting for app to be healthy...${NC}"
sleep 5

echo -e "${YELLOW}Step 4: Running migrations...${NC}"
docker compose -f "$COMPOSE_FILE" exec app python -m cli db migrate

echo -e "${GREEN}Backend restarted and migrations applied${NC}"


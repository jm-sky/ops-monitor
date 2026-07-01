#!/usr/bin/env bash
# Rebuild and restart the prod-flavored ops-monitor backend (root docker-compose.yml —
# backend/Dockerfile, no --reload), then run migrations. --force-recreate is required:
# the app process doesn't watch for file changes, so a plain `up -d` on an unchanged
# compose config is a no-op and leaves the old code running in memory.
# Called by deploy.sh — can also be run standalone from the project root.
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="docker-compose.yml"

echo -e "${GREEN}Restarting backend...${NC}"

cd "$PROJECT_DIR"

echo -e "${YELLOW}Step 1: Building app image...${NC}"
docker compose -f "$COMPOSE_FILE" build app

echo -e "${YELLOW}Step 2: Recreating app container...${NC}"
docker compose -f "$COMPOSE_FILE" up -d --force-recreate app

echo -e "${YELLOW}Step 3: Waiting for app to be healthy...${NC}"
sleep 5

echo -e "${YELLOW}Step 4: Running migrations...${NC}"
docker compose -f "$COMPOSE_FILE" exec app python -m cli db migrate

echo -e "${GREEN}Backend restarted and migrations applied${NC}"

#!/bin/bash
#
# E2E Test Runner for KAI Chat UI
#
# This script verifies services are running and executes Playwright E2E tests.
#
# Prerequisites:
#   - Node.js and npm installed
#   - Docker running (for Typesense)
#   - Python environment with langgraph installed
#
# Usage:
#   ./scripts/run-e2e-tests.sh [options]
#
# Options:
#   --headed    Run tests in headed mode (visible browser)
#   --ui        Run tests with Playwright UI
#   --check     Only check service status, don't run tests
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_PORT=3000
BACKEND_PORT=8000
TYPESENSE_PORT=8108
FRONTEND_URL="http://localhost:${FRONTEND_PORT}"
BACKEND_URL="http://localhost:${BACKEND_PORT}"
TYPESENSE_URL="http://localhost:${TYPESENSE_PORT}"

# Parse arguments
HEADED=false
UI_MODE=false
CHECK_ONLY=false

for arg in "$@"; do
    case $arg in
        --headed)
            HEADED=true
            shift
            ;;
        --ui)
            UI_MODE=true
            shift
            ;;
        --check)
            CHECK_ONLY=true
            shift
            ;;
    esac
done

echo "========================================"
echo "  KAI E2E Test Runner"
echo "========================================"
echo ""

# Function to check if a service is running
check_service() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [ "$status_code" = "$expected_code" ] || [ "$status_code" = "302" ] || [ "$status_code" = "301" ]; then
        echo -e "${GREEN}✓${NC} $name: Running (HTTP $status_code)"
        return 0
    else
        echo -e "${RED}✗${NC} $name: Not running or wrong response (HTTP $status_code)"
        return 1
    fi
}

# Check all services
echo "Checking service status..."
echo ""

SERVICES_OK=true

if ! check_service "Typesense" "${TYPESENSE_URL}/health"; then
    SERVICES_OK=false
    echo "  → Start with: docker compose up typesense -d"
fi

if ! check_service "Backend" "${BACKEND_URL}/api/connections" "200"; then
    # Try alternative health check
    if ! check_service "Backend (alt)" "${BACKEND_URL}/docs" "200"; then
        SERVICES_OK=false
        echo "  → Start with: langgraph dev (or uvicorn app.main:app --reload --port 8000)"
    fi
fi

if ! check_service "Frontend" "${FRONTEND_URL}/chat"; then
    SERVICES_OK=false
    echo "  → Start with: cd ui && npm run dev"
fi

echo ""

if [ "$CHECK_ONLY" = true ]; then
    if [ "$SERVICES_OK" = true ]; then
        echo -e "${GREEN}All services are running!${NC}"
        exit 0
    else
        echo -e "${RED}Some services are not running.${NC}"
        exit 1
    fi
fi

if [ "$SERVICES_OK" = false ]; then
    echo -e "${YELLOW}Warning: Some services are not running.${NC}"
    echo "Tests may fail. Continue anyway? (y/N)"
    read -r response
    if [ "$response" != "y" ] && [ "$response" != "Y" ]; then
        echo "Aborted."
        exit 1
    fi
fi

# Check if Playwright is installed
echo "Checking Playwright installation..."
if ! npx playwright --version > /dev/null 2>&1; then
    echo -e "${YELLOW}Installing Playwright browsers...${NC}"
    npx playwright install chromium
fi
echo -e "${GREEN}✓${NC} Playwright ready"
echo ""

# Run tests
echo "Running E2E tests..."
echo ""

if [ "$UI_MODE" = true ]; then
    npx playwright test --ui
elif [ "$HEADED" = true ]; then
    npx playwright test --headed
else
    npx playwright test
fi

echo ""
echo "========================================"
echo "  Test run complete!"
echo "========================================"

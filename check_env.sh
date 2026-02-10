#!/bin/bash
# Environment Check Script for Company Crawler
# Verifies that all dependencies and configurations are properly set up

echo "=================================================="
echo "🔍 Company Crawler - Environment Check"
echo "=================================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_passed=0
check_failed=0

# Function to check command
check_command() {
    if command -v "$1" &> /dev/null; then
        echo -e "${GREEN}✅${NC} $1: $(command -v $1)"
        version=$($1 --version 2>&1 | head -1)
        echo "   Version: $version"
        ((check_passed++))
        return 0
    else
        echo -e "${RED}❌${NC} $1: Not found"
        ((check_failed++))
        return 1
    fi
}

echo "1️⃣  System Tools"
echo "---"
check_command python3
check_command pip3
check_command git
echo ""

echo "2️⃣  Project Structure"
echo "---"
if [ -d ".venv" ]; then
    echo -e "${GREEN}✅${NC} Virtual environment: .venv/"
    ((check_passed++))
else
    echo -e "${RED}❌${NC} Virtual environment: Not found"
    ((check_failed++))
fi

if [ -f "requirements.txt" ]; then
    echo -e "${GREEN}✅${NC} requirements.txt: Found"
    ((check_passed++))
else
    echo -e "${RED}❌${NC} requirements.txt: Not found"
    ((check_failed++))
fi

if [ -d "data" ]; then
    echo -e "${GREEN}✅${NC} Data directory: data/"
    ((check_passed++))
else
    echo -e "${YELLOW}⚠️${NC}  Data directory: Not found (will be created on first run)"
fi
echo ""

echo "3️⃣  Python Packages"
echo "---"
if [ -d ".venv" ]; then
    source .venv/bin/activate

    # Check requests
    if python -c "import requests" 2>/dev/null; then
        version=$(python -c "import requests; print(requests.__version__)" 2>/dev/null || echo "installed")
        echo -e "${GREEN}✅${NC} requests: $version"
        ((check_passed++))
    else
        echo -e "${RED}❌${NC} requests: Not installed"
        ((check_failed++))
    fi

    # Check beautifulsoup4 (imports as bs4)
    if python -c "import bs4" 2>/dev/null; then
        version=$(python -c "import bs4; print(bs4.__version__)" 2>/dev/null || echo "installed")
        echo -e "${GREEN}✅${NC} beautifulsoup4: $version"
        ((check_passed++))
    else
        echo -e "${RED}❌${NC} beautifulsoup4: Not installed"
        ((check_failed++))
    fi

    # Check playwright
    if python -c "import playwright" 2>/dev/null; then
        version=$(python -c "import playwright; print(playwright.__version__)" 2>/dev/null || echo "installed")
        echo -e "${GREEN}✅${NC} playwright: $version"
        ((check_passed++))
    else
        echo -e "${RED}❌${NC} playwright: Not installed"
        ((check_failed++))
    fi

    # Check playwright browsers
    if playwright --version &> /dev/null; then
        echo -e "${GREEN}✅${NC} Playwright browsers: Installed"
        ((check_passed++))
    else
        echo -e "${RED}❌${NC} Playwright browsers: Not installed"
        echo "   Run: playwright install chromium"
        ((check_failed++))
    fi
else
    echo -e "${RED}❌${NC} Cannot check packages: .venv not found"
    ((check_failed+=4))
fi
echo ""

echo "4️⃣  Scripts & Permissions"
echo "---"
for script in "daily_crawler.py" "run_daily_crawler.sh" "setup_cron.sh"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo -e "${GREEN}✅${NC} $script: Executable"
            ((check_passed++))
        else
            echo -e "${YELLOW}⚠️${NC}  $script: Not executable (run: chmod +x $script)"
        fi
    else
        echo -e "${RED}❌${NC} $script: Not found"
        ((check_failed++))
    fi
done
echo ""

echo "5️⃣  Environment Variables"
echo "---"
if [ -n "$SLACK_WEBHOOK_URL" ]; then
    echo -e "${GREEN}✅${NC} SLACK_WEBHOOK_URL: Set"
    echo "   URL: ${SLACK_WEBHOOK_URL:0:40}..."
    ((check_passed++))
else
    echo -e "${YELLOW}⚠️${NC}  SLACK_WEBHOOK_URL: Not set"
    echo "   (Required for Slack notifications)"
    echo "   Set in ~/.bashrc: export SLACK_WEBHOOK_URL='your-url'"
fi
echo ""

echo "6️⃣  Documentation"
echo "---"
for doc in "SETUP.md" "AUTOMATION_README.md" ".gitignore"; do
    if [ -f "$doc" ]; then
        echo -e "${GREEN}✅${NC} $doc: Found"
        ((check_passed++))
    else
        echo -e "${YELLOW}⚠️${NC}  $doc: Not found"
    fi
done
echo ""

echo "=================================================="
echo "📊 Summary"
echo "=================================================="
echo -e "Passed: ${GREEN}$check_passed${NC}"
echo -e "Failed: ${RED}$check_failed${NC}"
echo ""

if [ $check_failed -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Environment is ready.${NC}"
    echo ""
    echo "Quick Start:"
    echo "  # Test crawler"
    echo "  source .venv/bin/activate"
    echo "  TEST_MODE=true python daily_crawler.py"
    echo ""
    echo "  # Setup automation"
    echo "  ./setup_cron.sh"
    exit 0
else
    echo -e "${RED}⚠️  Some checks failed. Please review the issues above.${NC}"
    echo ""
    echo "Common fixes:"
    echo "  # Install missing packages"
    echo "  source .venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    echo "  # Install Playwright browsers"
    echo "  playwright install chromium"
    echo ""
    echo "  # Set executable permissions"
    echo "  chmod +x *.sh *.py"
    exit 1
fi

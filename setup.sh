#!/usr/bin/env bash
set -e

# 1) Check for python
if ! command -v python3 &> /dev/null; then
	echo "❌ Python3 could not be found. Please install it first."
fi

# 2) create venv
if [ ! -d "venv" ]; then
	echo "📦 Creating virtual environment..."
	python3 -m venv .venv
else
	echo "✅ Virtual environment already exists."

source .venv/bin/activate

# 3) install deps
echo "⬇️ Installing requirements from requirements.txt..."
pip install -U pip
pip install playwright pandas python-dotenv selenium

# 4) install browsers
python -m playwright install --with-deps chromium

# 5) create .env template (optional)
if [ ! -f .env ]; then
cat > .env << 'EOF'
# Google Maps place URL
MAPS_URL=""

# Output file
OUTPUT_CSV="scraping_reviews.csv"

# Max scroll loops (more loops = more reviews, but slower)
MAX_SCROLL=250

# If no new reviews loaded for N consecutive scrolls -> stop
NO_GROWTH_LIMIT=10

# Headless mode: 1 = headless, 0 = visible browser
HEADLESS=1

# Slow motion (ms) - helps when Google is heavy or for debugging
SLOWMO=0

# Optional: Use persistent user profile (helps reduce captcha)
# USER_DATA_DIR="./chrome_profile"
USER_DATA_DIR=""
EOF
else
	echo "✅ .env file already exists."
fi

echo "✅ Setup done. Next: edit .env (MAPS_URL) and run: python scrape_gmaps_reviews.py"

# chmod +x setup.sh
# ./setup.sh

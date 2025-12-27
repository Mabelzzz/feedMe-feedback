#!/usr/bin/env bash
set -e

# 1) create venv
python3 -m venv .venv
source .venv/bin/activate

# 2) install deps
pip install -U pip
pip install playwright pandas python-dotenv selenium

# 3) install browsers
python -m playwright install --with-deps chromium

# 4) create .env template (optional)
if [ ! -f .env ]; then
cat > .env << 'EOF'
# Google Maps place URL
MAPS_URL="https://www.google.com/maps/place/Mo-Mo-Paradise+(Megabangna)/@13.6468884,100.6792784,17z/data=!3m2!4b1!5s0x311d5e5b6aa2c6e3:0xd8022fa11255c100!4m18!1m9!3m8!1s0x311d5e5c98aa52d7:0xa40d3abc4c7930b6!2sMo-Mo-Paradise+(Megabangna)!8m2!3d13.6468884!4d100.6818533!9m1!1b1!16s%2Fg%2F11gdtgsw7h!3m7!1s0x311d5e5c98aa52d7:0xa40d3abc4c7930b6!8m2!3d13.6468884!4d100.6818533!9m1!1b1!16s%2Fg%2F11gdtgsw7h?entry=ttu&g_ep=EgoyMDI1MTIwOS4wIKXMDSoASAFQAw%3D%3D"

# Output file
OUTPUT_CSV="momo_megabangna_reviews.csv"

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
fi

echo "✅ Setup done. Next: edit .env (MAPS_URL) and run: python scrape_gmaps_reviews.py"

# chmod +x setup.sh
# ./setup.sh

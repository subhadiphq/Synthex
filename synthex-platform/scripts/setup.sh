#!/bin/bash
set -e
echo "🚀 Synthex Local Setup"
echo "======================"
cd "$(dirname "$0")/../backend"
pip install -r requirements.txt
echo ""
echo "✅ Done! Now:"
echo "  1. cp .env.example .env"
echo "  2. Edit .env — add your API keys"
echo "  3. python main.py"
echo "  4. Open http://localhost:8000/docs"

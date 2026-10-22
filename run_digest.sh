#!/bin/zsh
set -e
cd "$(dirname "$0")"
mkdir -p logs
source .venv/bin/activate
.venv/bin/python bot.py >> logs/digest.log 2>&1

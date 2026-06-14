#!/usr/bin/env bash
#
# Update an existing native install to the latest code. Run from the repo root:
#
#   sudo bash deploy/update.sh
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run as root (sudo bash deploy/update.sh)." >&2
  exit 1
fi

echo ">> Pulling latest code..."
cd "$REPO_DIR"
git pull --ff-only

echo ">> Rebuilding the frontend..."
cd "$REPO_DIR/frontend"
npm install
npm run build
rm -rf "$REPO_DIR/backend/app/static"
cp -r dist "$REPO_DIR/backend/app/static"

echo ">> Updating the Python environment..."
cd "$REPO_DIR/backend"
.venv/bin/pip install .

echo ">> Restarting the service..."
systemctl restart dahlia
echo ">> Done. Your data was untouched."

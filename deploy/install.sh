#!/usr/bin/env bash
#
# Native install of the Dahlia tool on a Debian/Ubuntu Proxmox LXC (or any VM).
# Run from the repository root as root:
#
#   sudo bash deploy/install.sh
#
# Optional environment overrides:
#   PORT=8000           port to listen on
#   DATA_DIR=/path      where the database + photos live (default: <repo>/data)
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DATA_DIR="${DATA_DIR:-$REPO_DIR/data}"
PORT="${PORT:-8000}"

if [ "$(id -u)" -ne 0 ]; then
  echo "Please run as root (sudo bash deploy/install.sh)." >&2
  exit 1
fi

echo ">> Installing system packages..."
apt-get update
apt-get install -y python3 python3-venv python3-pip git curl ca-certificates

# Debian's packaged Node is too old for Vite; install Node 20 LTS if needed.
need_node=1
if command -v node >/dev/null 2>&1; then
  major="$(node -v | sed 's/^v//' | cut -d. -f1)"
  [ "${major:-0}" -ge 18 ] && need_node=0
fi
if [ "$need_node" -eq 1 ]; then
  echo ">> Installing Node.js 20 LTS..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
fi

echo ">> Building the frontend..."
cd "$REPO_DIR/frontend"
npm install
npm run build
rm -rf "$REPO_DIR/backend/app/static"
cp -r dist "$REPO_DIR/backend/app/static"

echo ">> Setting up the Python environment..."
cd "$REPO_DIR/backend"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
# Install the app + its dependencies (frontend already copied into app/static).
.venv/bin/pip install .

mkdir -p "$DATA_DIR"

echo ">> Installing the systemd service..."
sed -e "s#__REPO_DIR__#$REPO_DIR#g" \
    -e "s#__DATA_DIR__#$DATA_DIR#g" \
    -e "s#__PORT__#$PORT#g" \
    "$REPO_DIR/deploy/dahlia.service" > /etc/systemd/system/dahlia.service

systemctl daemon-reload
systemctl enable --now dahlia

ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
echo ""
echo ">> Done. The Dahlia tool is running."
echo "   Open:  http://${ip:-<this-container-ip>}:$PORT"
echo "   Data:  $DATA_DIR   (back up this folder)"
echo "   Logs:  journalctl -u dahlia -f"

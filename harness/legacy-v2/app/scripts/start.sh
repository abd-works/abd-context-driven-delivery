#!/usr/bin/env bash
# Start the Knowledge Graph explorer (Vite UI + API). Ctrl+C stops both.
set -euo pipefail
APP="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP"

port_in_use() {
  python - "$1" <<'PY'
import socket, sys
port = int(sys.argv[1])
s = socket.socket()
try:
    s.bind(("127.0.0.1", port))
except OSError:
    sys.exit(0)
s.close()
sys.exit(1)
PY
}

pick_ports() {
  for ui in 3000 3010 3020 3030 3040; do
    api=$((ui + 1))
    if ! port_in_use "$ui" && ! port_in_use "$api"; then
      echo "$ui $api"
      return
    fi
  done
  echo "No free UI/API port pair (tried 3000/3001 through 3040/3041)." >&2
  exit 1
}

wait_port() {
  local port="$1"
  local n=0
  while (( n < 80 )); do
    if port_in_use "$port"; then
      return
    fi
    sleep 0.25
    n=$((n + 1))
  done
  echo "Timed out waiting for port $port" >&2
  exit 1
}

if [ ! -d node_modules ]; then
  npm install
fi

read -r VITE_PORT PORT <<<"$(pick_ports)"
export VITE_PORT PORT

npm run dev:server &
server_pid=$!
npm run dev &
ui_pid=$!

cleanup() {
  kill "$server_pid" "$ui_pid" 2>/dev/null || true
  wait "$server_pid" "$ui_pid" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

wait_port "$PORT"
wait_port "$VITE_PORT"
echo "Knowledge Graph explorer: http://localhost:${VITE_PORT}/"
echo "API: http://localhost:${PORT}/"
wait

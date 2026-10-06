#!/usr/bin/env bash
# boot.sh — container entrypoint for Render deployment.
# Boots: sandbox -> bootstrap -> json-api -> roles UI
set -euo pipefail
cd /app

DAR=".daml/dist/provenance-0.1.0.dar"

# PORT is injected by Render (or defaults to 8090)
UI_PORT="${PORT:-8090}"
echo "[boot] UI_PORT: $UI_PORT"

echo "[boot] starting canton sandbox..."
rm -f /tmp/canton-port.txt
daml sandbox --dar "$DAR" --port-file /tmp/canton-port.txt > /tmp/sandbox.log 2>&1 &
SANDBOX_PID=$!

# Wait for sandbox to be ready (check log file)
for i in $(seq 1 90); do
  if grep -q "sandbox is ready" /tmp/sandbox.log 2>/dev/null; then
    echo "[boot] sandbox is ready"
    break
  fi
  sleep 1
  if [ $i -eq 90 ]; then
    echo "[boot] FATAL: sandbox never became ready"
    cat /tmp/sandbox.log
    exit 1
  fi
done

# Read ledger port
LEDGER_PORT=$(cat /tmp/canton-port.txt 2>/dev/null || echo "6865")
echo "[boot] ledger port: $LEDGER_PORT"

echo "[boot] bootstrapping parties + first hold..."
if ! daml script --dar "$DAR" --script-name ListParties:run \
  --ledger-host 127.0.0.1 --ledger-port "$LEDGER_PORT" > /tmp/bootstrap.log 2>&1; then
  echo "[boot] FATAL: bootstrap failed"
  cat /tmp/bootstrap.log
  exit 1
fi

if ! grep -q "held_cid=" /tmp/bootstrap.log; then
  echo "[boot] FATAL: bootstrap did not produce held contract"
  cat /tmp/bootstrap.log
  exit 1
fi
echo "[boot] bootstrap ok"

echo "[boot] starting json-api..."
daml json-api --ledger-host 127.0.0.1 --ledger-port "$LEDGER_PORT" \
  --address 0.0.0.0 --http-port 7575 > /tmp/jsonapi.log 2>&1 &
for i in $(seq 1 60); do
  if grep -q "Started server" /tmp/jsonapi.log 2>/dev/null; then
    echo "[boot] json-api ready"
    break
  fi
  sleep 1
  if [ $i -eq 60 ]; then
    echo "[boot] FATAL: json-api failed to start"
    cat /tmp/jsonapi.log
    exit 1
  fi
done

echo "[boot] starting roles UI on port $UI_PORT..."
export PROVENANCE_UI_PORT="$UI_PORT"
echo "[boot] UI port: $UI_PORT"

# Final health check before declaring success
echo "[boot] health check..."
for i in $(seq 1 30); do
  if curl -sf "http://127.0.0.1:${UI_PORT}/api/state" -o /dev/null 2>/dev/null; then
    echo "[boot] READY"
    break
  fi
  sleep 2
  if [ $i -eq 30 ]; then
    echo "[boot] WARNING: health check failed, but starting anyway"
  fi
done

echo "[boot] starting web server"
exec python3 ui/server.py
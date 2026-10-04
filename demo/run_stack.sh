#!/usr/bin/env bash
# Provenance — bring up the full local stack and run the judge-facing demo.
# Usage: ./demo/run_stack.sh
set -euo pipefail
cd "$(dirname "$0")/.."
export PATH="$HOME/.daml/bin:$PATH"

DAR=.daml/dist/provenance-0.1.0.dar

echo "── build ──────────────────────────────────────────"
daml build 2>&1 | tail -1
echo "── unit tests ─────────────────────────────────────"
daml test 2>&1 | grep -E ": ok|failed" || true

echo "── sandbox (background) ───────────────────────────"
pkill -f "canton.jar" 2>/dev/null || true
pkill -f "daml-sdk.jar json-api" 2>/dev/null || true
sleep 2
nohup daml sandbox --dar "$DAR" --port-file /tmp/canton-port.txt > /tmp/sandbox.log 2>&1 &
for i in $(seq 1 30); do [ -s /tmp/canton-port.txt ] && break; sleep 1; done
PORT=$(cat /tmp/canton-port.txt)
sleep 8   # let the participant finish booting

echo "── bootstrap (parties + two-party create) ─────────"
daml script --dar "$DAR" --script-name ListParties:run \
  --ledger-host 127.0.0.1 --ledger-port "$PORT" 2>&1 | grep -E "held_cid|Exception" | head -2

echo "── json api (background) ──────────────────────────"
nohup daml json-api --ledger-host 127.0.0.1 --ledger-port "$PORT" \
  --address 127.0.0.1 --http-port 7575 > /tmp/jsonapi.log 2>&1 &
for i in $(seq 1 30); do
  grep -q "Started server" /tmp/jsonapi.log 2>/dev/null && break; sleep 1
done

echo "── live demo ──────────────────────────────────────"
python3 demo/live_demo.py

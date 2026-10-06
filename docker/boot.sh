#!/usr/bin/env bash
# boot.sh — container entrypoint: the full stack, in order, with health waits.
# Mirrors demo/run_stack.sh but for an ephemeral host: the ledger is in-memory,
# so every boot recreates the parties and the bootstrap hold. Nothing persists
# between restarts — that is stated in the README and on the site, and it is
# fine for a judge-facing demo (the demo IS the rules, and the rules are in
# the DAR).
set -uo pipefail
export PATH="$HOME/.daml/bin:$PATH"
cd /app

DAR=.daml/dist/provenance-0.1.0.dar
# PORT is the platform-injected WEB port (Render etc.). The ledger gRPC port is
# separate and must NOT reuse the same variable — an earlier version let the
# sandbox port overwrite PORT and the UI bound to 6865 instead of the web port.
UI_PORT="${PORT:-8090}"

echo "[boot] starting canton sandbox…"
rm -f /tmp/canton-port.txt
daml sandbox --dar "$DAR" --port-file /tmp/canton-port.txt > /tmp/sandbox.log 2>&1 &
for i in $(seq 1 90); do
  grep -q "sandbox is ready" /tmp/sandbox.log 2>/dev/null && break
  sleep 1
done
if ! grep -q "sandbox is ready" /tmp/sandbox.log; then
  echo "[boot] FATAL: sandbox never became ready"; tail -20 /tmp/sandbox.log; exit 1
fi
LEDGER_PORT=$(cat /tmp/canton-port.txt)
echo "[boot] sandbox ready on $LEDGER_PORT"

echo "[boot] bootstrapping parties + first hold…"
daml script --dar "$DAR" --script-name ListParties:run \
  --ledger-host 127.0.0.1 --ledger-port "$LEDGER_PORT" > /tmp/bootstrap.log 2>&1
grep -q "held_cid=" /tmp/bootstrap.log || { echo "[boot] FATAL: bootstrap failed"; tail -10 /tmp/bootstrap.log; exit 1; }
echo "[boot] bootstrap ok"

echo "[boot] starting json-api…"
daml json-api --ledger-host 127.0.0.1 --ledger-port "$LEDGER_PORT" \
  --address 127.0.0.1 --http-port 7575 > /tmp/jsonapi.log 2>&1 &
for i in $(seq 1 60); do grep -q "Started server" /tmp/jsonapi.log 2>/dev/null && break; sleep 1; done
grep -q "Started server" /tmp/jsonapi.log || { echo "[boot] FATAL: json-api failed"; tail -10 /tmp/jsonapi.log; exit 1; }
echo "[boot] json-api ready"

echo "[boot] starting roles UI…"
# ui/server.py reads PROVENANCE_UI_PORT; it binds 0.0.0.0 so the container port maps
export PROVENANCE_UI_PORT="$UI_PORT"
echo "[boot] UI port: $UI_PORT"
exec python3 ui/server.py
